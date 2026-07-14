# system_prompts/

All LLM system prompts and user-prompt templates used by the WildClawBench harness live here. Loader is `src/utils/prompt_loader.py:load_prompt(name, **fmt)`.

## Files

| File | Used by | Role |
|---|---|---|
| `judge_system.md` | `grading._judge_system_prompt` | Walkthrough Yes/No verdict format (b78). |
| `judge_user.md` | `grading._judge_user_prompt` | Template; placeholders: `{task_description}`, `{transcript}`, `{output_files}`, `{rubrics_block}`, `{n_criteria}`. |
| `testgen_system.md` | `testgen.generator._prompt('testgen_system')` | Test-generation system prompt. |
| `testgen_user.md` | reference (not currently loaded) | Test-generation user prompt template. |
| `testgen_weights_system.md` | reference (not currently loaded) | Weight assignment system prompt. |
| `testgen_intent.md` | `testgen.intent._load_intent_system_prompt` | Intent extraction. |
| `testgen_rubric_overlap.md` | reference (not currently loaded) | Rubric/test overlap heuristics. |

## Loader contract

- `load_prompt('judge_system')` — returns the file's text verbatim. Cached after first read.
- `load_prompt('judge_user', task_description='...', transcript='...', output_files='...', rubrics_block='...', n_criteria=12)` — returns the file's text with `.format(**fmt)` applied. Placeholders are Python `str.format` style.
- `.md` suffix optional: both `'judge_system'` and `'judge_system.md'` work.
- Repo-root anchored — works regardless of `cwd` (test_executor subprocesses, CI runners, etc.).
- Missing file raises `PromptNotFoundError`.

## Editing

Hot-edit a prompt and re-run? Set `WCB_PROMPT_NOCACHE=1` to bypass the LRU cache. Otherwise restart the Python process.

## Format-string footgun

Files loaded with `**fmt` are treated as Python format strings. Any literal `{` or `}` characters MUST be doubled (`{{`, `}}`). This is why judge user prompt's XML wrapper `<judgment>...</judgment>` is safe (no braces) but a prompt containing literal `{json: "..."}` would break unless escaped.

Files loaded with NO `**fmt` (e.g. `load_prompt('judge_system')`) skip `.format()` entirely — braces pass through unchanged.

## Adding a new prompt

1. Drop the .md file in this directory.
2. Update the table above.
3. Call `load_prompt('your_new_name', **fmt)` from code.

No code change required to the loader itself.
