---
id: 01_Productivity_Flow_task_5_wikipedia_biography
name: Extract Biography Sections from Wikipedia
category: 01_Productivity_Flow
timeout_seconds: 900
modality: pure-text
---

## Prompt
Read the **"Biography"** section of **Emperor Huan of Han** (汉桓帝) at:

- https://zh.wikipedia.org/wiki/%E6%B1%89%E6%A1%93%E5%B8%9D

**Use the version of Wikipedia as of 2026-03-20 23:59:59 UTC, not the current live page.**

Identify all the people mentioned in that section, excluding Emperor Huan of Han himself.

For each person who also has a "Biography" section on Wikipedia (in the version as of 2026-03-20), save that section's content as a Markdown file named `{person_name}.md`.

Use each person's **actual name** consistently (not their title or alias).

Save all the Markdown files to `/tmp_workspace/results/`.

Do not generate any other files or directories.

### Wikipedia Version

All Wikipedia content used in this task, including the Emperor Huan of Han page and every other person's page, must come from the latest revision made at or before **2026-03-20 23:59:59 UTC**. Ignore any edit made after that time. Whether a person has a "Biography" section is also judged on that version.

### Output Requirements

You must create the following outputs under `/tmp_workspace/results/`:

- One or more Markdown files: `{person_name}.md` (each in the results directory)

Each file must:

- Be named using the person's actual name
- Contain the full content of that person's "Biography" section from Wikipedia
- Be encoded in UTF-8
- Use Markdown format as it appears on Wikipedia (including section headers, paragraphs, etc.)
- Contain only text — do not include URLs or hyperlinks
- Use simplified Chinese characters consistently
- Not include explanations, comments, or extra prose beyond the Biography section content

Do not create any other files or directories in the results directory.

### Notes

- Only include people who have a dedicated "Biography" (生平 / 传记) section on their Wikipedia page
- Exclude Emperor Huan of Han (汉桓帝) himself
- Use the person's name as it appears in standard historical sources (e.g. 刘保, not 汉顺帝)
- For quoted text, use curved double quotation marks `"` `"` (U+201C/U+201D), not corner brackets `「` `」` (U+300C/U+300D)


## Expected Behavior

The agent should:

1. Navigate to the Wikipedia page for Emperor Huan of Han and locate its revision as of 2026-03-20 23:59:59 UTC
2. Read and parse the "Biography" section to extract all mentioned persons
3. For each mentioned person, locate their page's revision as of 2026-03-20 23:59:59 UTC and check whether it has a "Biography" section
4. For those who do, extract the full Biography section content from that revision
5. Save each extracted Biography as `results/{person_name}.md` using the person's actual name

The agent may use web browsing, Wikipedia API, or other tools. The final score depends only on the generated Markdown files.

## Grading Criteria

- [ ] `results/` directory exists
- [ ] All expected person Markdown files are created under `results/`
- [ ] No unexpected or extra files are created under `results/`
- [ ] Each file is named with the correct person name (e.g. `刘协.md`, `梁冀.md`)
- [ ] The content of each file matches the ground-truth Biography section after normalization
- [ ] Reference markers (e.g. `[1]`, `[2]`) are not required in model output; comparison ignores them
- [ ] Straight and curved quotation marks are treated as equivalent when comparing (`"` `"` `「` `」` → same)
- [ ] Leading "生平" / "传记" section headers are ignored when comparing
- [ ] Markdown ATX headers (`##` 标题) are converted to plain text before comparing; both formats count as correct
- [ ] Agent output should contain only text (no URLs); URLs in output will cause content mismatch

## Automated Checks

```python
def grade(**kwargs) -> dict:
    """
    Grade the Wikipedia Biography extraction task.
    """
    from pathlib import Path
    import re
    import unicodedata

    workspace = Path("/tmp_workspace")

    ALL_CRITERIA = [
        "results_dir_exists",
        "coverage_ratio",
        "content_match_ratio",
        "no_extra_files",
        "hard_constraint_pass",
        "overall_score",
    ]

    ZERO = {k: 0.0 for k in ALL_CRITERIA}
    results_dir = workspace / "results"
    gt_dir = workspace / "gt"

    if not gt_dir.exists() or not gt_dir.is_dir():
        return ZERO

    gt_files = sorted(
        p for p in gt_dir.iterdir()
        if p.is_file() and p.suffix.lower() == ".md"
    )
    if len(gt_files) == 0:
        return ZERO

    expected_names = {p.stem for p in gt_files}
    if not expected_names:
        return ZERO

    def normalize_md_content(text: str) -> str:
        """Normalize markdown content for comparison."""
        text = unicodedata.normalize("NFKC", str(text))
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove reference markers: [1], [2], etc.
        text = re.sub(r"\[\d+\]", "", text)
        # Treat straight and curved quotes as equivalent: " " 「」 -> "
        text = text.replace("\u201c", '"').replace("\u201d", '"')  # " "
        text = text.replace("\u300c", '"').replace("\u300d", '"')  # 「」
        # Do NOT strip URLs — their presence/absence is part of the evaluation
        # Ignore leading "生平" / "传记" section headers (e.g. "## 生平" or "生平" at start)
        text = re.sub(r"^\s*(#{1,6}\s*)?(生平|传记)\s*\n*", "", text, flags=re.IGNORECASE)
        # Convert markdown ATX headers to normal text: ## 标题 -> 标题 (keep title as plain text for comparison)
        text = re.sub(r"^\s*#{1,6}\s*([^\n]*)", r"\1", text, flags=re.MULTILINE)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        return text.strip()

    def read_and_normalize(path: Path) -> str | None:
        try:
            return normalize_md_content(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return None

    scores = dict(ZERO)
    scores["results_dir_exists"] = 1.0 if results_dir.exists() and results_dir.is_dir() else 0.0

    if not results_dir.exists() or not results_dir.is_dir():
        return scores

    pred_md_files = [p for p in results_dir.iterdir() if p.is_file() and p.suffix.lower() == ".md"]
    pred_names = {p.stem for p in pred_md_files}

    coverage = 0
    content_match = 0

    for gt_path in gt_files:
        name = gt_path.stem
        gt_content = read_and_normalize(gt_path)
        if gt_content is None:
            continue

        pred_path = results_dir / f"{name}.md"
        if pred_path.exists() and pred_path.is_file():
            coverage += 1
            pred_content = read_and_normalize(pred_path)
            if pred_content is not None and pred_content == gt_content:
                content_match += 1

    total = len(gt_files)
    scores["coverage_ratio"] = round(coverage / total, 4) if total > 0 else 0.0
    scores["content_match_ratio"] = round(content_match / total, 4) if total > 0 else 0.0

    extra_names = pred_names - expected_names
    extra_count = len(extra_names)
    scores["no_extra_files"] = round(max(0.0, 1.0 - 0.1 * extra_count), 4)

    hard_checks = ["results_dir_exists"]
    hard_pass = all(scores[k] == 1.0 for k in hard_checks)
    scores["hard_constraint_pass"] = 1.0 if hard_pass else 0.0

    if not hard_pass:
        scores["overall_score"] = 0.0
        return scores

    base_score = round(
        0.3 * scores["coverage_ratio"] + 0.7 * scores["content_match_ratio"],
        4,
    )
    scores["overall_score"] = round(base_score * scores["no_extra_files"], 4)
    return scores
```

## Workspace Path

```
workspace/01_Productivity_Flow/task_5_wikipedia_biography
```

## Skills

```
agent-browser
```

## Env

```
```

## Warmup

```
npm install -g agent-browser
```
