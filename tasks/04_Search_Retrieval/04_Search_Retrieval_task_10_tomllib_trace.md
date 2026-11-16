---
id: 04_Search_Retrieval_task_10_tomllib_trace
name: Search Traceability Test
category: 04_Search_Retrieval
timeout_seconds: 600
modality: pure-text
---

## Prompt

Question:
In which Python version was `tomllib` first added to the standard library?
Please further determine: what is the CPython GitHub Pull Request number that introduced it?
Please provide the final answer and output a complete evidence chain proving your conclusion.

Mandatory Requirements:

1. The total number of searches must not exceed 5.

2. The answer may only be based on publicly searchable webpages.

3. The answer must explicitly state:
    (1) the total number of searches performed;
    (2) the query used for each search.

4. A complete evidence chain must be provided, and each evidence item must include page title, key claim, and URL.

5. If the answer cannot be confirmed within the search budget, the task must be terminated, and you must explicitly state "Unable to confirm." Do not guess.

6. Write your results into `/tmp_workspace/results/results.md`.

Output Format (Please strictly follow the format below):
```
Total number of searches: <number>

Search 1: <query>
Finding: <one-sentence summary>

Search 2: <query>
Finding: <one-sentence summary>

...

Final Answer:

First introduced in version: <version>

Corresponding PR: <PR number>

Evidence Chain:

<Evidence 1: page title + key conclusion + URL>

<Evidence 2: page title + key conclusion + URL>

Reasoning:
<Use 3-5 sentences to explain why these pieces of evidence are sufficient to support the final answer>
```

## Expected Behavior

The agent should complete the following tasks:

1. Find the corresponding Python version on the web.

2. Find the corresponding CPython PR number on the web.

3. Use no more than 5 searches.

4. Write the detailed search process and the final answer into a Markdown (.md) file.

## Grading Criteria

- [ ] Finding the correct answer earns 0.3 points.
- [ ] If the answer is found in 1-2 searches, the remaining 0.7 points are awarded.
- [ ] If it takes 3 searches, the remaining 0.5 points are awarded.
- [ ] If it takes 4 searches, the remaining 0.2 points are awarded.
- [ ] If it takes 5 searches, no remaining points are awarded.

## Automated Checks

```python
def grade(**kwargs) -> dict:
    """
    04_Search_Retrieval_task_10_tomllib_trace

    Returns:
        0 - 1
    """
    import os
    import json
    import logging
    from pathlib import Path

    log = logging.getLogger("04_Search_Retrieval_task_10_tomllib_trace Grading Start!")
    logging.basicConfig(level=logging.INFO, format="[%(name)s] %(message)s")

    description_file = Path("/tmp_workspace/results/results.md")
    scores = {}

    if not description_file.exists():
        log.warning("results.md not found: %s", description_file)
        scores["overall_score"] = 0.0
        return scores

    pred_description = description_file.read_text(encoding="utf-8").strip()
    if not pred_description:
        log.warning("results.md is empty")
        scores["overall_score"] = 0.0
        return scores

    log.info("Content in MD: %s", pred_description[:200])

    llm_succeeded = False
    last_error = None

    try:
        import time
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url=os.environ["OPENROUTER_BASE_URL"],
        )

        gt_description = "\n".join([
            "Python Version: 3.11",
            "CPython PR: #31498"
        ])
        judge_prompt = f"""你是一位评分裁判。请你依据标准答案和待评估回答进行打分。

具体要求是：
1. 如果待评估回答中的 Python 版本不是 3.11，或未明确说出 CPython PR 的数字为 31498，直接返回 score 为0。PR 数字前是否带 `#` 不影响判定。
2. 如果待评估回答中的 Python 版本为 3.11，且明确说出 CPython PR 的数字为 31498（例如 `31498`、`#31498` 或 `PR 31498`），获得初始0.3分，并进一步依据2.1-2.4的要求打分：
    2.1. 如果待评估回答中给出的搜索过程使用了1次或2次搜索，则额外获得0.7分，最终返回的 score 为 1.0。
    2.2. 如果待评估回答中给出的搜索过程使用了3次搜索，则额外获得0.5分，最终返回的 score 为 0.8。
    2.3. 如果待评估回答中给出的搜索过程使用了4次搜索，则额外获得0.2分，最终返回的 score 为 0.5。
    2.4. 如果待评估回答中给出的搜索过程使用了5次搜索，则额外获得0.0分，最终返回的 score 为 0.3。

【标准答案】
{gt_description}

【待评估回答】
{pred_description}

请只返回一个 JSON 对象，格式：{{"score": <0-1>, "reason": "<简要理由>"}}"""

        max_retries = 3
        for attempt in range(max_retries):
            log.info("LLM Judge request %d/%d...", attempt + 1, max_retries)
            try:
                response = client.chat.completions.create(
                    model=os.environ.get("JUDGE_MODEL", "openai/gpt-5.4"),
                    messages=[{"role": "user", "content": judge_prompt}],
                    temperature=0,
                )

                result_text = response.choices[0].message.content.strip()
                log.info("LLM raw response: %s", result_text[:300])

                if result_text.startswith("```"):
                    result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

                result_json = json.loads(result_text)
                raw_score = float(result_json.get("score", 0))
                raw_score = max(0.0, min(1.0, raw_score))
                scores["overall_score"] = raw_score
                scores["judge_reason"] = result_json.get("reason", "")
                llm_succeeded = True
                log.info("LLM Judge succeeded — score: %s, reason: %s",
                         raw_score, scores["judge_reason"])
                break

            except Exception as e:
                last_error = e
                log.warning("LLM Judge attempt %d failed: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

    except Exception as e:
        last_error = e
        log.error("OpenAI client initialization failed: %s", e)

    if not llm_succeeded and last_error:
        scores["judge_error"] = str(last_error)

    # ---- Fall back to keyword matching when all LLM attempts fail ----
    if not llm_succeeded:
        log.warning("LLM Judge failed all 3 attempts, scoring 0")
        scores["overall_score"] = 0

    log.info("Final score: overall_score=%s", scores["overall_score"])
    return scores
```

## Workspace Path

```
workspace/04_Search_Retrieval/task_10_tomllib_trace
```

## Skills

```
```

## Env

```
OPENROUTER_API_KEY
OPENROUTER_BASE_URL
JUDGE_MODEL
```

## Warmup

```

```

