from __future__ import annotations

import json
import logging
import os
import subprocess
import time

logger = logging.getLogger(__name__)

# Pinned by digest, NOT by floating tag. The original `:main-stable` reference
# silently rolled forward and on EC2 2026-06-13 07:23 (darren_weston run_1)
# produced empty thinking text on the FIRST Bedrock response despite the
# adaptive+display:summarized+output_config:effort:high shape being correct in
# our YAML — i.e. litellm regressed its Converse passthrough between two
# main-stable pulls. The pinned digest below is the Mac-cached image that
# repeatedly produced text_len 111-5230 of reasoning. To bump: pull a new
# main-stable, smoke-test it against a known-good task end-to-end (look for
# nonempty `thinking` in output.json), then update both this constant AND the
# `FROM` line in docker/litellm-headroom.Dockerfile to the new digest.
LITELLM_IMAGE = "ghcr.io/berriai/litellm@sha256:c98c9395c56a35b7abacff8269d43ff99aabacb62bbf42a04cc1514fcb9bde4a"
LITELLM_INTERNAL_PORT = 4000
LITELLM_HEADROOM_IMAGE = "wildclawbench-litellm-headroom:v2"


def build_litellm_config_yaml(
    bedrock_arn: str = "",
    aws_region: str = "ap-south-1",
    openai_api_key: str = "",
    bedrock_sonnet_arn: str = "",
    enable_usage_callback: bool = False,
    openai_whisper_api_key: str = "",
    enable_headroom_callback: bool = False,
    anthropic_api_key: str = "",
    use_claude_oauth: bool = False,
    bridge_url: str = "",
    enable_oauth_usage_callback: bool = False,
    meta_api_key: str = "",
    meta_base_url: str = "https://api.ai.meta.com/v1",
    meta_model: str = "",
) -> str:
    whisper_env_ref = (
        "os.environ/OPENAI_API_KEY_WHISPER"
        if openai_whisper_api_key
        else "os.environ/OPENAI_API_KEY"
    )
    model_blocks: list[str] = []
    # `cache_control_injection_points` MUST live inside each model's
    # `litellm_params:` block, NOT in global `litellm_settings:`. Empirically
    # verified with the LiteLLM main-stable image (probe_cache.py + GitHub
    # source litellm/litellm_core_utils/litellm_logging.py:917): the
    # `anthropic_cache_control_hook` only instantiates when the directive is
    # in the per-call `non_default_params` payload, which is fed from per-
    # model params. The global-settings form was accepted by the proxy
    # (visible in DEBUG logs as `setting litellm.cache_control_injection_points
    # =[...]`) but never produced cache_read/cache_write > 0 on any request.
    # Required on every Anthropic-on-Bedrock route. OpenAI routes auto-cache
    # server-side at >=1024 prompt tokens and do not need the directive.
    cache_marker = (
        "      cache_control_injection_points:\n"
        "        - location: message\n"
        "          role: system\n"
    )
    if use_claude_oauth and bridge_url:
        # ---------------------------------------------------------------
        # Claude Code OAuth trajectory path (opt-in via --use-claude-oauth).
        #
        # Approved deviation from src/utils/AGENTS.md invariant at line 276
        # ("Opus traffic NEVER reaches public Anthropic transport"). Opus
        # here is fronted by the wcbsh-cc-bridge-<suffix> sidecar which
        # attaches an OAuth Bearer token (from WCB_CC_ACCOUNT_POOL creds)
        # and forwards to https://api.anthropic.com under a Claude Code
        # Max subscription. LiteLLM sees a plain `anthropic/` model on a
        # custom api_base; the bridge is a transparent Anthropic-Messages
        # proxy (per Oracle review — pure pass-through, no key rewriting).
        #
        # Thinking directive shape here MUST be {type:enabled,budget_tokens}
        # not adaptive+effort:high — Anthropic-direct 400s the adaptive
        # shape (that's a Bedrock-Converse-specific extension). budget_tokens
        # 32000 mirrors kaiju-harness's Opus fixed-budget shape and yields
        # visibly populated thinking blocks on api.anthropic.com's opus route.
        #
        # cost_per_token = 0 so LiteLLM's completion_cost() reports $0 for
        # subscription usage (the real subscription is prepaid, per-request
        # cost is zero). Bedrock-equivalent pricing is emitted separately by
        # litellm_usage_oauth_callback.py into usage_oauth.jsonl for audit.
        #
        # extra_headers.x-wcb-bridge-secret enforces that only sidecar co-
        # tenants with the shared batch secret can drain the subscription.
        # Bridge validates via hmac.compare_digest; missing/mismatched → 401.
        # ---------------------------------------------------------------
        opus_oauth_params = (
            "    litellm_params:\n"
            "      model: anthropic/claude-opus-4-8\n"
            f"      api_base: {bridge_url}\n"
            "      api_key: os.environ/WCB_CC_STUB_KEY\n"
            "      thinking: {\"type\": \"enabled\", \"budget_tokens\": 32000}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            "      extra_headers:\n"
            "        x-wcb-bridge-secret: os.environ/WCB_CC_BRIDGE_SECRET\n"
            + cache_marker
            + "      input_cost_per_token: 0\n"
            "      output_cost_per_token: 0\n"
            "      cache_read_input_token_cost: 0\n"
            "      cache_creation_input_token_cost: 0"
        )
        model_blocks.append("  - model_name: claude-opus-4.7\n" + opus_oauth_params)
        model_blocks.append("  - model_name: claude-opus-4-6\n" + opus_oauth_params)
    elif bedrock_arn:
        # Extended-thinking visibility on opus-4-6/4-7 via Bedrock Converse needs the
        # EXACT pair thinking:{type:adaptive} + output_config:{effort}. Three shapes
        # were tried empirically against this LiteLLM (main-stable sha 75543fa1d739):
        #   - thinking:{type:enabled,budget_tokens} -> Bedrock 400 "thinking.type.enabled
        #     is not supported... use thinking.type.adaptive and output_config.effort".
        #   - bare thinking:{type:adaptive} (no effort) -> Bedrock accepts but returns
        #     ZERO reasoningContent -> 0 thinking blocks every turn (run_4/run_5).
        #   - additional_model_request_fields:{...} -> Bedrock 400 "Extra inputs are
        #     not permitted" (LiteLLM forwards the unknown key literally).
        # The thinking block MUST include display:"summarized". Empirically (direct
        # Bedrock /converse probes against this opus ARN, sheep-math reasoning prompt):
        #   - thinking:{type:adaptive} alone           -> reasoning text_len=0 (EMPTY),
        #     signature present. This is what reasoning_effort:high builds, and it made
        #     openclaw persist an EMPTY thinking block (run_6 1/32, text len 0).
        #   - thinking:{type:adaptive,display:summarized} -> reasoning text_len 289-665
        #     (POPULATED) + signature. THIS is the shape that yields visible reasoning.
        #   - display:"detailed" -> Bedrock 400 "display: Input should be summarized or
        #     omitted". Valid values are ONLY "summarized" or "omitted".
        # output_config:{effort} is OPTIONAL once display:summarized is present (the
        # no-output_config probe returned MORE text, 665). So we pass the explicit
        # thinking dict (same known-good shape the sonnet judge entry uses below) rather
        # than reasoning_effort:high, which strips display and yields empty text.
        #
        # CRITICAL routing/detection decoupling (still required): adaptive-thinking
        # detection keys off the `model` STRING via get_base_model()->_is_opus_4_6_model()
        # substring match. Our opus access is an opaque application-inference-profile ARN
        # (.../j6mdizxjngus); putting that ARN in `model:` makes get_base_model return
        # "j6mdizxjngus" (split('/')[-1]) -> fails the opus-4-6 substring -> Bedrock
        # 400s the legacy shape. Fix: `model:` carries the RECOGNIZABLE name
        # "anthropic.claude-opus-4-6-v1"; `model_id:` (common_utils.py:get_bedrock_model_id
        # pops it, URL-encodes into the endpoint URL) carries the real ARN for routing.
        # Do NOT collapse these into a single `model: bedrock/converse/<ARN>` line, and
        # do NOT drop display:summarized -- either re-breaks thinking visibility.
        opus_params = (
            "    litellm_params:\n"
            # NO `converse/` infix: per LiteLLM common_utils.py:873 (`if "claude"
            # in model -> AmazonAnthropicClaudeMessagesConfig`), /v1/messages routes
            # a claude model through Bedrock INVOKE (native Anthropic SSE) not
            # Converse. Direct HTTP probes proved Invoke emits parseable thinking_
            # delta+signature_delta+text_delta; Converse leaks camelCase
            # reasoningContent that pi-ai's @anthropic-ai/sdk cannot parse. The
            # "anthropic.claude-opus-4-6-v1" substring must remain so get_base_model
            # ->_is_opus_4_6_model() matches and adaptive detection fires; model_id
            # carries the real ARN. Do NOT re-add `converse/` -- re-breaks thinking.
            "      model: bedrock/anthropic.claude-opus-4-6-v1\n"
            f"      model_id: {bedrock_arn}\n"
            f"      aws_region_name: {aws_region or 'ap-south-1'}\n"
            # output_config.effort:high: probes showed bare adaptive can return an
            # empty/absent thinking block; +effort:high reliably populates it.
            # Bedrock REQUIRES this {type:adaptive,display:summarized}+output_config
            # pair on the opus ARN and 400s {type:enabled,budget_tokens} with
            # "thinking.type.enabled is not supported... use thinking.type.adaptive
            # and output_config.effort" (re-confirmed live 2026-06-12 on
            # profile 0pou38ej54bo). Do NOT switch to enabled+budget_tokens.
            "      thinking: {\"type\": \"adaptive\", \"display\": \"summarized\"}\n"
            "      output_config: {\"effort\": \"high\"}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            + cache_marker
            + "      input_cost_per_token: 0.000005\n"
            "      output_cost_per_token: 0.000025\n"
            # Opus 4.6/4.7 cache rates: read 0.1x ($0.50/MTok), write 1.25x
            # ($6.25/MTok). Required or cache_write under-counts on Bedrock
            # streaming (SIX_CHECK report); honored by both completion_cost and
            # the proxy per-deployment cost path.
            "      cache_read_input_token_cost: 0.0000005\n"
            "      cache_creation_input_token_cost: 0.00000625"
        )
        # Opus model name(s). All alias the one Bedrock opus inference-profile ARN
        # (KENSEI_BEDROCK_MODEL_ARN, currently Opus 4.8). claude-opus-4.8 is the
        # current name; claude-opus-4.7 is kept as a backward-compat alias so older
        # scripts/run args keep working (they now route to the same 4.8 ARN).
        model_blocks.append("  - model_name: claude-opus-4.8\n" + opus_params)
        model_blocks.append("  - model_name: claude-opus-4.7\n" + opus_params)
        # openclaw's _set_model presents the recognized id "claude-opus-4-6" to
        # activate extended thinking (see runner.py); that id arrives here on the
        # /v1/messages route and must resolve to the SAME opus ARN as
        # claude-opus-4.7. Both names alias one ARN so the harness model arg and
        # the openclaw-facing id stay decoupled.
        model_blocks.append("  - model_name: claude-opus-4-6\n" + opus_params)
    elif anthropic_api_key:
        # Fallback upstream for opus when no Bedrock ARN is available. Routes
        # the same claude-opus-4.7 / claude-opus-4-6 aliases through Anthropic
        # direct using `model: anthropic/claude-opus-4-20250514`. Keeps the
        # `cache_control_injection_points` directive and `include_usage` on
        # stream so the per-judge usage dict shape (7-key, see grading.py
        # header + AGENTS.md) and prompt-caching telemetry remain identical
        # to the Bedrock path. Thinking is NOT requested here: Anthropic's
        # `thinking:{type:adaptive}` shape is Bedrock-Converse-specific; the
        # /v1/messages route on the direct API would 400 it. Agent behavior
        # is unaffected because the opus model still responds correctly; only
        # the streamed reasoning trace is absent on this fallback path.
        #
        # NOTE on AGENTS.md invariant "Opus traffic NEVER reaches public
        # Anthropic transport": this fallback IS a deviation, retained for
        # dev-machine usability when Bedrock creds are rotated. Production
        # OAuth path (use_claude_oauth branch above) is a SEPARATE approved
        # deviation using OAuth subscription + wcbsh-cc-bridge sidecar for
        # authorized/audited access; do not conflate the two.
        opus_anthropic_params = (
            "    litellm_params:\n"
            "      model: anthropic/claude-opus-4-20250514\n"
            "      api_key: os.environ/ANTHROPIC_API_KEY\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            + cache_marker
            + "      input_cost_per_token: 0.000015\n"
            "      output_cost_per_token: 0.000075"
        )
        model_blocks.append("  - model_name: claude-opus-4.7\n" + opus_anthropic_params)
        model_blocks.append("  - model_name: claude-opus-4-6\n" + opus_anthropic_params)
    if bedrock_sonnet_arn:
        model_blocks.append(
            "  - model_name: claude-sonnet-4-6\n"
            "    litellm_params:\n"
            # model:/model_id: split mirrors Opus so the RECOGNIZABLE name resolves
            # in litellm's catalog for cost (an opaque inference-profile ARN in
            # model: raises "isn't mapped yet" -> cost falls back to the under-
            # counting response_cost). model_id carries the real ARN for routing
            # (get_bedrock_model_id pops it). KEEP the converse/ infix here (unlike
            # Opus): Sonnet's reasoningContent is tolerated by the harness on
            # Converse; do NOT switch to Invoke without re-testing thinking parsing.
            "      model: bedrock/converse/anthropic.claude-sonnet-4-6\n"
            f"      model_id: {bedrock_sonnet_arn}\n"
            f"      aws_region_name: {aws_region or 'ap-south-1'}\n"
            # Same adaptive+display:summarized shape as Opus; Bedrock 400s
            # enabled+budget_tokens here too (see opus block).
            "      thinking: {\"type\": \"adaptive\", \"display\": \"summarized\"}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            + cache_marker
            + "      input_cost_per_token: 0.000003\n"
            "      output_cost_per_token: 0.000015\n"
            # Sonnet 4.6 cache rates: read 0.1x ($0.30/MTok), write 1.25x
            # ($3.75/MTok). Same rationale as Opus above.
            "      cache_read_input_token_cost: 0.0000003\n"
            "      cache_creation_input_token_cost: 0.00000375"
        )
    if openai_api_key:
        # The dict `reasoning_effort: {effort, summary}` shape is a Responses
        # API feature; /v1/chat/completions rejects it as
        # `invalid_request_error: Unsupported value: 'reasoning_effort' does
        # not support {...}. Supported values are: 'none','low','medium','high'`.
        # That is exactly the silent 'Connection error.' the agent saw on
        # 2026-06-02 (alden-croft run_3 chat.jsonl 4x stopReason=error).
        # Fix: prefix the upstream model with `openai/responses/` so LiteLLM
        # bridges every chat-completions call to /v1/responses, where the
        # dict form is accepted. summary="auto" (NOT "detailed") because per
        # LiteLLM docs/providers/openai#reasoning-effort, "detailed" requires
        # OpenAI org verification and 400s otherwise; "auto" works for any
        # gpt-5.5 caller and still emits a reasoning summary. gpt-5.5 default
        # effort is "medium"; we keep "high" deliberately for hard tasks.
        model_blocks.append(
            "  - model_name: gpt-5.5\n"
            "    litellm_params:\n"
            "      model: openai/responses/gpt-5.5\n"
            "      api_key: os.environ/OPENAI_API_KEY\n"
            "      reasoning_effort: {\"effort\": \"high\", \"summary\": \"auto\"}\n"
            "      stream_options:\n"
            "        include_usage: true\n"
            "      input_cost_per_token: 0.000005\n"
            "      output_cost_per_token: 0.00003"
        )
        # Without this, /v1/audio/transcriptions returns HTTP 400 "Invalid
        # model name passed in model=whisper-1" (see failure report §6a) and
        # the agent burns its budget on broken pip-install whisper fallbacks.
        model_blocks.append(
            "  - model_name: whisper-1\n"
            "    litellm_params:\n"
            "      model: openai/whisper-1\n"
            f"      api_key: {whisper_env_ref}"
        )
        # OpenClaw's built-in transcribeAudio runner auto-POSTs the sidecar's
        # /v1/audio/transcriptions but its OpenAI plugin defaults to model=
        # "gpt-4o-mini-transcribe" (DEFAULT_OPENAI_AUDIO_MODEL), NOT whisper-1.
        # With only whisper-1 registered, that request 400s "Invalid model
        # name" and the agent punts ("give it a listen yourself"), zeroing
        # audio-dependent criteria. Alias every audio id openclaw can emit to
        # the same openai/whisper-1 upstream (a pure sidecar rewrite, same
        # pattern as the image aliases below). whisper-1 is the correct OpenAI
        # transcription model + /v1/audio/transcriptions the correct multipart
        # endpoint per developers.openai.com/api/docs/guides/speech-to-text.
        for _audio_fallback_id in (
            "gpt-4o-mini-transcribe",
            "gpt-4o-transcribe",
        ):
            model_blocks.append(
                f"  - model_name: {_audio_fallback_id}\n"
                "    litellm_params:\n"
                "      model: openai/whisper-1\n"
                f"      api_key: {whisper_env_ref}"
            )
    if meta_api_key and meta_model:
        # Meta vendor model (internal Llama API) exposed through the sidecar as
        # an OpenAI-compatible upstream. LiteLLM reaches it via the `openai/`
        # provider prefix + an explicit api_base, the same OpenAI-compatible
        # bridge used for any non-OpenAI /v1/chat/completions relay.
        #
        # PARAMETER POLICY (vendor onboarding guide, non-negotiable): keep ALL
        # inference params at their DEFAULTS for this relay — do NOT set
        # reasoning_effort, temperature, top_p, top_k, max_tokens, or
        # response_format here. The relay also documents hard gaps: no
        # structured output, no parallel tool calling, no function tool-call
        # streaming. The global `litellm_settings.drop_params: true` (set below)
        # is what makes this safe end-to-end: any of those params an upstream
        # caller (openclaw, judge, testgen) emits are silently dropped before
        # the request reaches api.ai.meta.com instead of 400-ing the relay.
        # Intentionally NO `stream_options.include_usage` and NO input/output
        # cost overrides — both are non-default request shaping the guide tells
        # us not to add; usage is still recorded post-call by the LiteLLM usage
        # callback from the response body. The harness-facing model id IS
        # `meta_model`, so `--model <meta_model>` routes straight here.
        model_blocks.append(
            f"  - model_name: {meta_model}\n"
            "    litellm_params:\n"
            f"      model: openai/{meta_model}\n"
            f"      api_base: {meta_base_url}\n"
            "      api_key: os.environ/META_API_KEY"
        )
    # OpenClaw's memory tool POSTs model=text-embedding-3-small to the sidecar
    # /v1/embeddings on session-start, on memory search, and from our explicit
    # `openclaw memory index` step. With no embeddings route registered the
    # proxy 400s "Invalid model name passed in model=text-embedding-3-small"
    # (same failure class as whisper-1 above) and memory recall silently dies.
    # Per user decision (m0476: "no need for any embedding models"), we register
    # a MOCK route: litellm reads `mock_response` from litellm_params and short-
    # circuits before any network call (litellm/main.py embedding -> mock_embedding),
    # so the call returns a valid 200 OpenAI-shaped EmbeddingResponse with NO real
    # model, NO OpenAI key dependency, and NO embedding spend. Semantic recall is
    # intentionally non-functional (mock returns a single fixed zero vector); the
    # plain-file persona bootstrap is unaffected (it reads MDs off disk, never
    # hits /v1/embeddings). mode: embedding routes the id to the /embeddings
    # handler. Alias the three current OpenAI embedding ids openclaw may emit.
    for _emb_id in (
        "text-embedding-3-small",
        "text-embedding-3-large",
        "text-embedding-ada-002",
    ):
        model_blocks.append(
            f"  - model_name: {_emb_id}\n"
            "    litellm_params:\n"
            f"      model: openai/{_emb_id}\n"
            "      mock_response: [0.0]\n"
            "    model_info:\n"
            "      mode: embedding"
        )
    # OpenClaw's image tool falls back to built-in default model ids when its
    # own imageModel override isn't applied inside the container. The openclaw
    # 2026.3.11 dist (verified via grep of /usr/lib/node_modules/openclaw/dist)
    # references BOTH "gpt-4o" (32x) and "gpt-4o-mini" (81x) as defaults, and the
    # image tool emits them under the "anthropic/" provider slot. The gateway
    # doesn't expose those ids, so multimodal calls die with e.g.
    # "Unknown model: anthropic/gpt-4o-mini" (see gateway.log 2026-06-04 06:57).
    # We alias EVERY fallback id openclaw can emit to a real vision-capable model
    # that IS registered, so image tasks resolve instead of erroring. The alias
    # is a pure sidecar rewrite: a request labeled "anthropic/gpt-4o-mini" is
    # transparently served by gpt-5.5 (or the Opus profile) and NEVER reaches a
    # real OpenAI gpt-4o/gpt-4o-mini endpoint -- no extra cost, no egress, no
    # bypass of the --internal sandbox. Prefer GPT-5.5 (OpenAI), else Opus.
    if openai_api_key:
        image_alias = (
            "      model: openai/responses/gpt-5.5\n"
            "      api_key: os.environ/OPENAI_API_KEY"
        )
    elif bedrock_arn:
        image_alias = (
            f"      model: bedrock/converse/{bedrock_arn}\n"
            f"      aws_region_name: {aws_region or 'ap-south-1'}\n"
            + cache_marker.rstrip("\n")
        )
    elif meta_api_key and meta_model:
        # Meta-only run: route openclaw's built-in image fallback ids to the
        # vendor model (Llama is multimodal). Same default-params policy — only
        # routing fields, no inference param overrides.
        image_alias = (
            f"      model: openai/{meta_model}\n"
            f"      api_base: {meta_base_url}\n"
            "      api_key: os.environ/META_API_KEY"
        )
    else:
        image_alias = ""
    if image_alias:
        for _img_fallback_id in (
            "anthropic/gpt-4o",
            "anthropic/gpt-4o-mini",
            "gpt-4o",
            "gpt-4o-mini",
        ):
            model_blocks.append(
                f"  - model_name: {_img_fallback_id}\n"
                "    litellm_params:\n"
                + image_alias
            )
    if not model_blocks:
        return ""
    # Real per-call usage from the proxy itself (not the agent's chat.jsonl
    # which openclaw writes with all-zero usage). Loaded by the LiteLLM
    # callback file mounted at /app/litellm_usage_callback.py.
    #
    # When `enable_headroom_callback=True`, mount the Headroom pre-call
    # compressor AFTER the usage callback. Ordering rationale: LiteLLM iterates
    # `for cb in litellm.callbacks` for the pre-call dispatch. The usage
    # callback does NOT override `async_pre_call_hook` so LiteLLM auto-skips
    # it in that loop (litellm/proxy/utils.py skip-rule: `if cb.async_pre_call_hook
    # != CustomLogger.async_pre_call_hook`), which means the headroom callback
    # is effectively first in the pre-call phase regardless of list position.
    # Post-call, the usage logger sees `kwargs["messages"]` AS COMPRESSED, so
    # it records the post-compression token count — exactly what Bedrock/OpenAI
    # billed — preserving the existing 11-key JSONL schema unchanged.
    _cbs: list[str] = []
    if enable_usage_callback:
        _cbs.append("litellm_usage_callback.proxy_handler_instance")
    if enable_headroom_callback:
        _cbs.append("litellm_headroom_callback.headroom_callback_instance")
    if enable_oauth_usage_callback:
        _cbs.append("litellm_usage_oauth_callback.oauth_usage_callback_instance")
    if enable_stream_callback:
        # Live-token observability tap (docs/STREAMING_PLAN.md): pure
        # pass-through iterator hook writing to its OWN sink
        # (/var/litellm_stream/stream.jsonl) — never usage.jsonl NOR
        # usage_oauth.jsonl (m0130 sink separation). Batch-scoped: registered
        # only when WCB_STREAM was on at setup (R6). NOTE: on the OAuth agent
        # path callers pass enable_stream_callback=False — the cc-bridge tee
        # is the real-time tap there; the sidecar would only see the bridge's
        # end-of-turn burst (docs/STREAMING_PLAN.md §1.5).
        _cbs.append("litellm_stream_callback.stream_handler_instance")
    if _cbs:
        callback_line = "  callbacks: [" + ", ".join(f'"{c}"' for c in _cbs) + "]\n"
    else:
        callback_line = ""
    return (
        "model_list:\n"
        + "\n".join(model_blocks)
        + "\n"
        "litellm_settings:\n"
        "  drop_params: true\n"
        "  modify_params: true\n"
        "  telemetry: false\n"
        # User policy m1386 2026-06-02: maximum extension on the LiteLLM-side
        # timeouts. 86400s = 24h is the largest value httpx will accept as a
        # positive float without overflow concerns; LiteLLM rejects null/-1/0/
        # 'infinity' so this is the de-facto 'indefinite' value. num_retries
        # bumped to 10 for non-openclaw paths (testgen, judge council) which
        # call LiteLLM directly. CAVEAT: for the openclaw agent backend, the
        # openclaw npm package has its OWN hardcoded ~22s 'LLM request timed
        # out' ceiling on /v1/messages and /chat/completions — raising these
        # numbers does NOT help openclaw runs hit by that ceiling. Do not
        # 'normalize' these values back down without rereading b66 and m1386.
        "  num_retries: 10\n"
        "  request_timeout: 86400\n"
        "  stream_timeout: 86400\n"
        "  reasoning_auto_summary: true\n"
        # Transcription response cache: LiteLLM keys on the audio BYTE hash
        # (auto-injected metadata.file_checksum), NOT the filename, so distinct
        # recordings never collide. supported_call_types is scoped to ONLY
        # (a)transcription so chat/judge/opus caching is unaffected; do not widen
        # it without re-checking judge-council determinism.
        "  cache: true\n"
        "  cache_params:\n"
        "    type: local\n"
        "    supported_call_types: [\"transcription\", \"atranscription\"]\n"
        + callback_line
        + "general_settings:\n"
        "  master_key: os.environ/LITELLM_MASTER_KEY\n"
        "  store_model_in_db: false\n"
    )


def _image_present_locally(image: str) -> bool:
    return subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
    ).returncode == 0


def pull_litellm_image(image: str = LITELLM_IMAGE) -> None:
    # `:main-stable` is a moving registry tag; we explicitly pull at batch
    # startup so registry/network failures surface here instead of inside the
    # first `docker run` and being misattributed to a task error.
    #
    # The pull is a registry round-trip even when the image is already cached
    # locally (moving tag), so a slow/blocked/unauthenticated ghcr.io connection
    # can hang the whole batch at startup. To stay robust:
    #   * WILDCLAW_SKIP_LITELLM_PULL=1 skips the pull entirely when the image is
    #     present locally (offline / pinned-image runs).
    #   * the pull is time-bounded (WILDCLAW_LITELLM_PULL_TIMEOUT, default 180s).
    #   * on timeout/failure we fall back to the local image if present, only
    #     raising when there is genuinely no image to run.
    if os.environ.get("WILDCLAW_SKIP_LITELLM_PULL") and _image_present_locally(image):
        logger.info("Skipping LiteLLM pull (WILDCLAW_SKIP_LITELLM_PULL set); using local %s", image)
        return

    timeout = int(os.environ.get("WILDCLAW_LITELLM_PULL_TIMEOUT", "180"))
    logger.info("Pulling LiteLLM image %s (timeout %ss)", image, timeout)
    try:
        r = subprocess.run(
            ["docker", "pull", image],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        if _image_present_locally(image):
            logger.warning(
                "LiteLLM pull timed out after %ss; falling back to the local "
                "image %s. Set WILDCLAW_SKIP_LITELLM_PULL=1 to skip the pull.",
                timeout, image,
            )
            return
        raise RuntimeError(
            f"LiteLLM pull of {image} timed out after {timeout}s and no local "
            f"copy exists. Pre-pull it or set WILDCLAW_LITELLM_PULL_TIMEOUT higher."
        )
    if r.returncode != 0:
        if _image_present_locally(image):
            logger.warning(
                "LiteLLM pull failed (%s); falling back to the local image %s.",
                (r.stderr or "").strip(), image,
            )
            return
        raise RuntimeError(
            f"Failed to pull LiteLLM image {image}: {(r.stderr or '').strip()}"
        )
    logger.info("LiteLLM image %s ready", image)


# docker/litellm-headroom.Dockerfile, relative to repo root. The image is a
# LOCAL build (headroom-ai baked into the stock LiteLLM image); it lives in no
# registry, so `docker run` would try to PULL it and fail with access-denied on
# a fresh host. We build it here at batch startup instead.
_HEADROOM_DOCKERFILE = "docker/litellm-headroom.Dockerfile"


def _repo_root() -> str:
    # litellm_sidecar.py lives at <repo>/src/utils/; repo root is two levels up.
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def ensure_litellm_headroom_image(image: str = LITELLM_HEADROOM_IMAGE) -> None:
    # Mirror pull_litellm_image()'s early-surface contract for the headroom
    # image: surface a missing/un-buildable image at batch startup, not deep
    # inside the first `docker run` where it gets misattributed to a task error.
    # The image is local-build-only, so we auto-build from the committed
    # Dockerfile when absent (build is deterministic + context-independent).
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True, text=True,
    )
    if inspect.returncode == 0:
        logger.info("LiteLLM headroom image %s present", image)
        return

    repo_root = _repo_root()
    dockerfile = os.path.join(repo_root, _HEADROOM_DOCKERFILE)
    build_cmd = [
        "docker", "build",
        "-f", dockerfile,
        "-t", image,
        repo_root,
    ]
    manual = f"docker build -f {_HEADROOM_DOCKERFILE} -t {image} ."
    if not os.path.isfile(dockerfile):
        raise RuntimeError(
            f"LiteLLM headroom image {image} is missing and its Dockerfile "
            f"was not found at {dockerfile}. Build it manually from the repo "
            f"root with: {manual}"
        )
    logger.info(
        "LiteLLM headroom image %s not found locally; building from %s",
        image, _HEADROOM_DOCKERFILE,
    )
    r = subprocess.run(build_cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"Failed to build LiteLLM headroom image {image} from {dockerfile}: "
            f"{(r.stderr or '').strip()}\n"
            f"Build it manually from the repo root with: {manual}"
        )
    logger.info("LiteLLM headroom image %s built and ready", image)


def create_network(name: str, internal: bool = True) -> None:
    # internal=True creates an --internal bridge with no NAT to the host's
    # default route, so containers attached to ONLY this network cannot
    # reach the public internet. Agent containers MUST attach to an
    # internal-only bridge to keep them sandboxed. The LiteLLM sidecar
    # needs Bedrock/OpenAI access, so it's dual-homed (this internal
    # bridge + the default bridge) via connect_default_bridge() below.
    r = subprocess.run(
        ["docker", "network", "inspect", name],
        capture_output=True,
    )
    if r.returncode == 0:
        return
    cmd = ["docker", "network", "create"]
    if internal:
        cmd.append("--internal")
    cmd.append(name)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Failed to create network {name}: {r.stderr}")
    logger.info("Network %s created (internal=%s)", name, internal)


def connect_default_bridge(container_name: str) -> None:
    # Attach a second NIC on the default bridge so this container can reach
    # the public internet (needed for the LiteLLM sidecar to talk to
    # Bedrock/OpenAI). Idempotent: ignores the 'already exists' error.
    r = subprocess.run(
        ["docker", "network", "connect", "bridge", container_name],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 and "already exists" not in (r.stderr or ""):
        raise RuntimeError(
            f"Failed to attach {container_name} to default bridge: {r.stderr}"
        )


def remove_network(name: str) -> None:
    subprocess.run(["docker", "network", "rm", name], capture_output=True)


def start_litellm(
    container_name: str,
    network: str,
    host_config_path: str,
    master_key: str,
    aws_bearer_token: str = "",
    aws_region: str = "ap-south-1",
    openai_api_key: str = "",
    port: int = LITELLM_INTERNAL_PORT,
    usage_callback_host_path: str = "",
    usage_log_host_dir: str = "",
    openai_whisper_api_key: str = "",
    headroom_callback_host_path: str = "",
    headroom_log_host_dir: str = "",
    enable_headroom: bool = False,
    anthropic_api_key: str = "",
    oauth_usage_callback_host_path: str = "",
    meta_api_key: str = "",
) -> None:
    from src.utils.docker_utils import (
        build_env_args,
        _validate_docker_token,
    )
    _validate_docker_token("container_name", container_name)
    _validate_docker_token("network", network)

    env_pairs: list[tuple[str, str]] = [("LITELLM_MASTER_KEY", master_key)]
    _litellm_log = os.environ.get("LITELLM_LOG", "").strip()
    if _litellm_log:
        env_pairs.append(("LITELLM_LOG", _litellm_log))
    if aws_bearer_token:
        env_pairs += [
            ("AWS_BEARER_TOKEN_BEDROCK", aws_bearer_token),
            ("AWS_REGION", aws_region),
        ]
    if openai_api_key:
        env_pairs.append(("OPENAI_API_KEY", openai_api_key))
    if openai_whisper_api_key:
        env_pairs.append(("OPENAI_API_KEY_WHISPER", openai_whisper_api_key))
    if anthropic_api_key:
        env_pairs.append(("ANTHROPIC_API_KEY", anthropic_api_key))
    _cc_secret = os.environ.get("WCB_CC_BRIDGE_SECRET", "").strip()
    if _cc_secret:
        env_pairs.append(("WCB_CC_BRIDGE_SECRET", _cc_secret))
    _cc_stub = os.environ.get("WCB_CC_STUB_KEY", "").strip() or "sk-wcb-oauth-stub"
    env_pairs.append(("WCB_CC_STUB_KEY", _cc_stub))
    # Meta vendor key: read by the meta model block via
    # `api_key: os.environ/META_API_KEY`.
    if meta_api_key:
        env_pairs.append(("META_API_KEY", meta_api_key))
    env_args = build_env_args(env_pairs)

    callback_args: list[str] = []
    if usage_callback_host_path and usage_log_host_dir:
        callback_args = [
            "-v", f"{usage_callback_host_path}:/app/litellm_usage_callback.py:ro",
            "-v", f"{usage_log_host_dir}:/var/litellm_usage",
            *build_env_args([("LITELLM_USAGE_LOG_PATH", "/var/litellm_usage/usage.jsonl")]),
        ]
    if oauth_usage_callback_host_path and usage_log_host_dir:
        callback_args += [
            "-v", f"{oauth_usage_callback_host_path}:/app/litellm_usage_oauth_callback.py:ro",
            *build_env_args([("WCB_OAUTH_USAGE_LOG_PATH", "/var/litellm_usage/usage_oauth.jsonl")]),
        ]

    # Headroom pre-call compressor: writes to a SEPARATE JSONL sink
    # (/var/litellm_headroom/headroom.jsonl). Must never collide with
    # LITELLM_USAGE_LOG_PATH — token-tracking invariant (user m0130).
    # LITELLM_HEADROOM_IMAGE has `headroom-ai` baked in; the stock image
    # cannot `import headroom` at proxy startup (no egress at that point).
    headroom_args: list[str] = []
    image_to_run = LITELLM_IMAGE
    if enable_headroom and headroom_callback_host_path and headroom_log_host_dir:
        image_to_run = LITELLM_HEADROOM_IMAGE
        headroom_pairs: list[tuple[str, str]] = [
            ("KENSEI_AGENT_HEADROOM_LOG_PATH", "/var/litellm_headroom/headroom.jsonl"),
            ("KENSEI_AGENT_HEADROOM_ENABLED",
             os.environ.get("KENSEI_AGENT_HEADROOM_ENABLED", "true")),
        ]
        for _k in ("KENSEI_AGENT_HEADROOM_TARGET_RATIO",
                   "KENSEI_AGENT_HEADROOM_PROTECT_RECENT",
                   "KENSEI_AGENT_HEADROOM_MIN_TOKENS"):
            _v = os.environ.get(_k)
            if _v:
                headroom_pairs.append((_k, _v))
        headroom_args = [
            "-v", f"{headroom_callback_host_path}:/app/litellm_headroom_callback.py:ro",
            "-v", f"{headroom_log_host_dir}:/var/litellm_headroom",
            *build_env_args(headroom_pairs),
        ]

    # Live-token stream tap (docs/STREAMING_PLAN.md): its OWN sink dir,
    # mounted separately from /var/litellm_usage so the feeds can never
    # collide (m0130 sink-separation invariant).
    stream_args: list[str] = []
    if stream_callback_host_path and stream_log_host_dir:
        stream_args = [
            "-v", f"{stream_callback_host_path}:/app/litellm_stream_callback.py:ro",
            "-v", f"{stream_log_host_dir}:/var/litellm_stream",
            *build_env_args([("WCB_STREAM_LOG_PATH", "/var/litellm_stream/stream.jsonl")]),
        ]

    image_to_run = _validate_docker_token("litellm image", image_to_run)
    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--network", network,
        *env_args,
        *callback_args,
        *headroom_args,
        *stream_args,
        "-v", f"{host_config_path}:/app/config.yaml:ro",
        image_to_run,
        "--config", "/app/config.yaml",
        "--port", str(port),
    ]
    logger.info(
        "[%s] Starting LiteLLM sidecar on network %s using image %s",
        container_name, network, image_to_run,
    )
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"LiteLLM container start failed:\n{r.stderr}")
    connect_default_bridge(container_name)
    logger.info("[%s] LiteLLM sidecar dual-homed (internal + default bridge)", container_name)


def wait_for_litellm_healthy(container_name: str, port: int = LITELLM_INTERNAL_PORT,
                             timeout: float | None = None) -> bool:
    # `KENSEI_LITELLM_HEALTH_TIMEOUT` env override exists so slower hosts
    # (cold Docker pulls, qemu-emulated arches) can extend the budget
    # without code edits. Default raised from 60s to 120s after the
    # openclaw.log 2026-06-02 incident where the sidecar booted fine but
    # the agent's first call still produced a bare "Connection error." at
    # the 4-retry/22s mark — the proxy was up, upstream Bedrock was the
    # actual problem (see verify_litellm_upstream_reachable below).
    if timeout is None:
        try:
            timeout = float(os.environ.get("KENSEI_LITELLM_HEALTH_TIMEOUT", "120"))
        except ValueError:
            timeout = 120.0
    probe = (
        "import sys, urllib.request; "
        "urllib.request.urlopen("
        f"'http://localhost:{port}/health/liveliness', timeout=2"
        ")"
    )
    deadline = time.time() + timeout
    interval = 2.0
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "exec", container_name, "python3", "-c", probe],
            capture_output=True,
        )
        if r.returncode == 0:
            logger.info("[%s] LiteLLM healthy", container_name)
            return True
        time.sleep(interval)
    logger.warning(
        "[%s] LiteLLM did not become healthy within %.0fs", container_name, timeout
    )
    return False


def verify_litellm_upstream_reachable(
    container_name: str,
    master_key: str,
    model_name: str,
    port: int = LITELLM_INTERNAL_PORT,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    # Synthetic 1-token round-trip via the proxy's /v1/chat/completions to
    # confirm that the upstream provider (Bedrock/OpenAI) is actually
    # reachable from inside the sidecar — not just that the proxy's own
    # liveliness endpoint answers. This catches the "Connection error." +
    # "LLM request timed out." failure mode seen in openclaw.log on
    # 2026-06-02T10:36:42: 4 retries within 22s, all failing before any
    # token streamed, fallbackConfigured=false. wait_for_litellm_healthy
    # returned True for that batch because /health/liveliness was up; the
    # real problem was Bedrock egress. Surfacing it here as a precise
    # batch-startup RuntimeError beats a misattributed agent timeout.
    body_bytes = json.dumps({
        "model": model_name,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "stream": False,
    }).encode()
    # Run the probe INSIDE the sidecar so we use the same network namespace
    # and hostname resolution path that openclaw will use when it calls the
    # proxy. Catches DNS/routing failures specific to the internal bridge.
    probe = (
        "import sys, urllib.request, urllib.error\n"
        f"req = urllib.request.Request('http://localhost:{port}/v1/chat/completions', "
        f"data={body_bytes!r}, "
        f"headers={{'Authorization': 'Bearer {master_key}', "
        "'Content-Type': 'application/json'}, method='POST')\n"
        "try:\n"
        f"    r = urllib.request.urlopen(req, timeout={int(timeout)})\n"
        "    sys.stdout.write('OK status=' + str(r.status))\n"
        "except urllib.error.HTTPError as e:\n"
        "    detail = e.read().decode('utf-8', errors='ignore')[:400]\n"
        "    sys.stdout.write('HTTP ' + str(e.code) + ': ' + detail)\n"
        "    sys.exit(1)\n"
        "except Exception as e:\n"
        "    sys.stdout.write('ERR: ' + repr(e))\n"
        "    sys.exit(2)\n"
    )
    r = subprocess.run(
        ["docker", "exec", container_name, "python3", "-c", probe],
        capture_output=True,
        text=True,
        timeout=timeout + 10.0,
    )
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode == 0:
        logger.info("[%s] LiteLLM upstream reachable (%s)", container_name, out)
        return True, out
    logger.warning(
        "[%s] LiteLLM upstream UNREACHABLE rc=%s out=%s",
        container_name, r.returncode, out,
    )
    return False, out


def stop_litellm(container_name: str) -> None:
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)


CC_BRIDGE_IMAGE = "wildclawbench-cc-bridge:v1"
CC_BRIDGE_INTERNAL_PORT = 8765


def ensure_cc_bridge_image(image: str = CC_BRIDGE_IMAGE) -> None:
    r = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
    )
    if r.returncode == 0:
        return
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dockerfile = os.path.join(repo_root, "docker", "cc-bridge", "Dockerfile")
    if not os.path.isfile(dockerfile):
        raise RuntimeError(
            f"cc-bridge image {image} not present locally and Dockerfile missing at {dockerfile}. "
            f"Build manually: docker build -t {image} -f {dockerfile} {repo_root}"
        )
    logger.info("Building cc-bridge image %s", image)
    r = subprocess.run(
        ["docker", "build", "-t", image, "-f", dockerfile, repo_root],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"cc-bridge image build failed:\n{r.stderr}\n"
            f"Manual: docker build -t {image} -f {dockerfile} {repo_root}"
        )
    logger.info("cc-bridge image %s built", image)


def start_bridge(
    container_name: str,
    network: str,
    pool_host_dir: str,
    bridge_secret: str,
    port: int = CC_BRIDGE_INTERNAL_PORT,
    image: str = CC_BRIDGE_IMAGE,
    upstream: str = "https://api.anthropic.com",
    account_pool_spec: str = "",
    skip_system_prefix: bool = False,
    stream_log_host_dir: str = "",
) -> None:
    from src.utils.docker_utils import (
        build_env_args,
        _validate_docker_token,
    )
    _validate_docker_token("container_name", container_name)
    _validate_docker_token("network", network)
    if not pool_host_dir or not os.path.isdir(pool_host_dir):
        raise RuntimeError(
            f"start_bridge: pool_host_dir must exist ({pool_host_dir!r})"
        )
    if not bridge_secret:
        raise RuntimeError("start_bridge: bridge_secret required (co-tenant threat)")

    if not account_pool_spec:
        account_pool_spec = ":".join(
            f"/oauth_pool/{f}"
            for f in sorted(os.listdir(pool_host_dir))
            if f.endswith(".json")
        )
    if not account_pool_spec:
        raise RuntimeError(
            f"start_bridge: no *.json OAuth credential files found under {pool_host_dir}"
        )

    env_pairs: list[tuple[str, str]] = [
        ("WCB_CC_ACCOUNT_POOL", account_pool_spec),
        ("WCB_CC_BRIDGE_SECRET", bridge_secret),
        ("WCB_CC_UPSTREAM", upstream),
    ]
    if skip_system_prefix:
        env_pairs.append(("WCB_CC_SKIP_SYSTEM_PREFIX", "1"))
    for _k in (
        "WCB_CC_MAX_INLINE_RETRIES",
        "WCB_CC_MAX_INLINE_WAIT",
        "WCB_CC_UPSTREAM",
        "WCB_CC_DEBUG_LOG_BODY",
        "WCB_CC_USER_AGENT",
        "WCB_CC_X_APP",
    ):
        _v = os.environ.get(_k)
        if _v:
            env_pairs.append((_k, _v))
    env_args = build_env_args(env_pairs)
    image = _validate_docker_token("cc-bridge image", image)

    ensure_cc_bridge_image(image)

    dump_mount: list[str] = []
    _dump_host = os.environ.get("WCB_CC_BODY_DUMP_HOST_DIR")
    if _dump_host:
        os.makedirs(_dump_host, exist_ok=True)
        dump_mount = ["-v", f"{_dump_host}:/wcb_dumps:rw"]
        env_args += build_env_args([("WCB_CC_BODY_DUMP_DIR", "/wcb_dumps")])

    # Live-stream tee sink (docs/STREAMING_PLAN.md §3.2): the bridge is the
    # ONLY real-time token tap on the OAuth path (the sidecar behind it sees
    # just the buffered end-of-turn burst). Same host dir as the batch stream
    # feed so the terminal renderer tails ONE file; mounted rw, separate from
    # every usage sink (m0130). Absent dir ⇒ tee stays inert (R6 default-off).
    stream_mount: list[str] = []
    if stream_log_host_dir:
        stream_mount = ["-v", f"{stream_log_host_dir}:/var/wcb_stream:rw"]
        env_args += build_env_args(
            [("WCB_CC_STREAM_LOG_PATH", "/var/wcb_stream/stream.jsonl")]
        )

    # Publish the bridge on a host loopback port when WCB_CC_BRIDGE_HOST_PORT is
    # set, so the host-side Sonnet judge (grading.py runs on the host, not in the
    # sidecar network) can reach the bridge at http://127.0.0.1:<port>. Bound to
    # 127.0.0.1 only; the x-wcb-bridge-secret still gates every request.
    publish_args: list[str] = []
    _host_port = os.environ.get("WCB_CC_BRIDGE_HOST_PORT", "").strip()
    if _host_port:
        publish_args = ["-p", f"127.0.0.1:{_host_port}:{port}"]

    # Network-attach ordering is load-bearing on Docker Desktop for Mac. When a
    # container is CREATED on a user-defined network and a `-p` publish is
    # requested, the loopback port-forward (docker-proxy/vpnkit) silently fails
    # to bind 127.0.0.1 — `docker inspect` shows the PortBindings but `docker ps`
    # shows no `->` forward and host curl is REFUSED. The fix: when publishing,
    # CREATE the container on the DEFAULT `bridge` network (with `-p`), then
    # attach the sidecar `network` second. That keeps the loopback forward alive
    # AND still resolves the bridge by name on the sidecar net (verified: agent
    # peers reach http://<name>:8765 fine). Without a publish we keep the old
    # order (create on sidecar net, dual-home to default bridge for egress).
    if publish_args:
        create_network_arg = "bridge"
        secondary_network = network
    else:
        create_network_arg = network
        secondary_network = "bridge"

    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--network", create_network_arg,
        *env_args,
        *dump_mount,
        *stream_mount,
        *publish_args,
        "-v", f"{pool_host_dir}:/oauth_pool:rw",
        image,
        "--host", "0.0.0.0",
        "--port", str(port),
    ]
    logger.info(
        "[%s] Starting cc-bridge on network %s (image=%s pool_dir=%s publish=%s)",
        container_name, create_network_arg, image, pool_host_dir, _host_port or "none",
    )
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cc-bridge container start failed:\n{r.stderr}")
    # Attach the second NIC. When we published, this is the sidecar network so
    # the agent/sidecar can resolve the bridge by name; otherwise it's the
    # default bridge for api.anthropic.com egress. connect_default_bridge is
    # idempotent for the 'bridge' case; use a direct connect for the sidecar net.
    if secondary_network == "bridge":
        connect_default_bridge(container_name)
    else:
        cr = subprocess.run(
            ["docker", "network", "connect", secondary_network, container_name],
            capture_output=True, text=True,
        )
        if cr.returncode != 0 and "already exists" not in (cr.stderr or ""):
            raise RuntimeError(
                f"Failed to attach {container_name} to {secondary_network}: {cr.stderr}"
            )
    logger.info(
        "[%s] cc-bridge dual-homed (internal + default bridge for api.anthropic.com egress)",
        container_name,
    )


def wait_for_bridge_healthy(
    container_name: str,
    port: int = CC_BRIDGE_INTERNAL_PORT,
    timeout: float | None = None,
) -> bool:
    if timeout is None:
        try:
            timeout = float(os.environ.get("WCB_CC_BRIDGE_HEALTH_TIMEOUT", "60"))
        except ValueError:
            timeout = 60.0
    probe = (
        "import urllib.request; "
        f"urllib.request.urlopen('http://localhost:{port}/healthz', timeout=2)"
    )
    deadline = time.time() + timeout
    interval = 1.5
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "exec", container_name, "python3", "-c", probe],
            capture_output=True,
        )
        if r.returncode == 0:
            logger.info("[%s] cc-bridge healthy", container_name)
            return True
        time.sleep(interval)
    logger.warning(
        "[%s] cc-bridge did not become healthy within %.0fs", container_name, timeout
    )
    return False


def wait_for_bridge_host_port(host_port: str, timeout: float = 15.0) -> bool:
    """Probe the HOST-published loopback port (127.0.0.1:<host_port>/healthz).

    wait_for_bridge_healthy only checks health from INSIDE the container, which
    passes even when Docker Desktop for Mac silently drops the `-p` loopback
    forward. But the Sonnet judge dials the bridge from the host, so a dropped
    publish surfaces much later as `[Errno 61] Connection refused` at grade time
    (intermittent, load-dependent). This probe catches the dropped publish up
    front so the caller can recreate the bridge instead of failing at grading.
    """
    if not host_port:
        return True
    import urllib.request

    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{host_port}/healthz"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2):
                return True
        except Exception:  # noqa: BLE001
            time.sleep(1.0)
    return False


def stop_bridge(container_name: str) -> None:
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
