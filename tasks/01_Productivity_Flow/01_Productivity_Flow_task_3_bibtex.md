---
id: 01_Productivity_Flow_task_3_bibtex
name: Recover Official arXiv Titles and BibTeX from Local PDFs
category: 01_Productivity_Flow
timeout_seconds: 900
modality: pure-text
---

## Prompt

A folder contains 21 arXiv papers already downloaded as PDF files, but the filenames are messy and unreliable. Some of the PDFs may be corrupted versions (e.g., missing pages, scribbles, or partial content).


The input PDFs are located directly under:

- `/tmp_workspace/`

Your task is to identify the official arXiv paper corresponding to each PDF, recover its exact official arXiv title, count how many figures appear in the provided PDF, and generate the official BibTeX for every paper.

Save the results into `/tmp_workspace/results/`. Create the following under that directory:
- `paper_manifest.json`
- `renamed_papers/`
- `bibtex/`

Do **not** modify or delete the original input PDFs.

### Output Requirements

You must create exactly the following outputs under `/tmp_workspace/results/`:

- `paper_manifest.json`
- `renamed_papers/`
- `bibtex/`

Do not create any other files or directories.

#### `paper_manifest.json`

Save a JSON array. Each item must contain exactly these fields:

```json
[
  {
    "original_filename": "messy_name_01.pdf",
    "arxiv_id": "2501.07888",
    "title": "Exact Official Paper Title",
    "renamed_filename": "Exact Official Paper Title.pdf",
    "figure_count": 12
  }
]
```

Requirements:

- **Include exactly one item for each input arXiv PDF**
- Do not omit any input PDF
- Do not include extra items
- `original_filename` must be the original filename from `/tmp_workspace/`
- `arxiv_id` must be the exact official arXiv identifier
- `title` must be the exact official arXiv title
- `renamed_filename` must exactly match the filename created under `renamed_papers/`
- `figure_count` must be a non-negative integer equal to the number of figures that appear in the provided PDF. For damaged or truncated PDFs, count only figures that actually appear in the visible provided PDF pages.

#### `renamed_papers/`

- **Create exactly one renamed PDF copy for each input arXiv PDF**
- Do not modify PDF contents; each renamed file must be byte-identical to the corresponding input PDF
- Use the official arXiv title as the filename after applying the sanitization rule below

#### Filename Sanitization Rule

Start from the exact official arXiv title, then:

1. normalize Unicode to NFKC
2. replace `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `-`
3. collapse consecutive whitespace into a single space
4. trim leading and trailing whitespace
5. remove trailing `.`
6. append `.pdf`

#### `bibtex/`

- Save exactly one BibTeX file per paper
- Name each file `<arxiv_id>.bib`
- Each file must contain exactly one BibTeX entry
- The BibTeX must match the official BibTeX shown on the arXiv page for that paper
- Do not add explanations, markdown, or extra prose

If you need image understanding or multimodal capabilities, you can call the OpenRouter API (base_url available via the `OPENROUTER_BASE_URL` environment variable, API key available via the `OPENROUTER_API_KEY` environment variable).

## Expected Behavior

The agent should:

1. Inspect each local PDF and determine which arXiv paper it is (for corrupted PDFs, use metadata or web search to identify the paper)
2. Recover the exact official arXiv title and arXiv ID
3. Count how many figures appear in the provided PDF for each paper
4. Create a renamed copy of each PDF using the required filename rule
5. Save one BibTeX file per paper under `bibtex/`
6. Produce a complete and internally consistent `paper_manifest.json`

The agent may use local PDF inspection, web access, shell commands, scripts, or arXiv pages, but the final score depends only on the generated files.

## Grading Criteria

- [ ] `paper_manifest.json` exists and is structurally valid
- [ ] `renamed_papers/` and `bibtex/` are created
- [ ] The manifest covers all expected arXiv inputs exactly once with no duplicates
- [ ] No extra unexpected outputs are produced
- [ ] `results/` contains only `paper_manifest.json`, `renamed_papers/`, and `bibtex/` at top level
- [ ] Every renamed arXiv PDF is byte-identical to the corresponding input PDF
- [ ] The predicted arXiv ID for each expected paper is correct
- [ ] The recovered title for each expected paper matches the official arXiv title up to case differences
- [ ] The renamed PDF filenames match the required sanitization rule up to case differences
- [ ] The recovered `figure_count` matches the number of figures appearing in the provided PDF, with higher weight on corrupted PDFs
- [ ] Each expected BibTeX file is created under `bibtex/`
- [ ] The BibTeX content matches the official ground truth after whitespace normalization
- [ ] Corrupted PDFs (missing pages, scribbles, etc.) are correctly identified and processed with high weight in scoring

## Automated Checks

```python
def grade(**kwargs) -> dict:
    """
    Grade the local arXiv rename-and-bibtex task.
    """
    from pathlib import Path
    import hashlib
    import json
    import re
    import unicodedata

    workspace = Path("/tmp_workspace")

    ALL_CRITERIA = [
        "manifest_exists",
        "manifest_json_valid",
        "renamed_dir_exists",
        "bibtex_dir_exists",
        "input_coverage_consistent",
        "pdf_copies_byte_identical",
        "non_arxiv_excluded",
        "workspace_cleanliness",
        "arxiv_id_accuracy",
        "title_accuracy",
        "filename_accuracy",
        "figure_count_accuracy",
        "bibtex_files_created",
        "bibtex_exact_match_ratio",
        "corrupted_paper_accuracy",
        "hard_constraint_pass",
        "overall_score",
    ]

    ZERO = {k: 0.0 for k in ALL_CRITERIA}

    results_dir = workspace / "results"
    manifest_path = results_dir / "paper_manifest.json"
    renamed_dir = results_dir / "renamed_papers"
    bibtex_dir = results_dir / "bibtex"
    gt_dir = workspace / "gt"
    gt_manifest_path = gt_dir / "gt_manifest.json"
    gt_bibtex_dir = gt_dir

    if not gt_manifest_path.exists():
        return ZERO

    def sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def normalize_text(text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def normalize_casefold_text(text: str) -> str:
        return normalize_text(text).casefold()

    def sanitize_title(title: str) -> str:
        title = unicodedata.normalize("NFKC", title)
        title = re.sub(r'[\/\\:*?"<>|]', "-", title)
        title = re.sub(r"\s+", " ", title).strip()
        title = title.rstrip(".").strip()
        return f"{title}.pdf"

    def normalize_bibtex(text: str) -> str:
        text = text.strip().replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = text.strip()
        return text

    def cleanliness_score(extra_count: int) -> float:
        return round(max(0.5, 1.0 - 0.1 * extra_count), 4)

    try:
        gt_items = json.loads(gt_manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return ZERO

    if not isinstance(gt_items, list) or len(gt_items) == 0:
        return ZERO

    required_gt_fields = {"input_sha256", "arxiv_id", "title", "figure_count"}
    gt_by_sha = {}
    corrupted_shas = set()
    for item in gt_items:
        if not isinstance(item, dict):
            return ZERO
        if not required_gt_fields.issubset(item.keys()):
            return ZERO
        if not isinstance(item.get("figure_count"), int) or item["figure_count"] < 0:
            return ZERO
        gt_by_sha[item["input_sha256"]] = item
        if item.get("is_corrupted"):
            corrupted_shas.add(item["input_sha256"])

    input_pdfs = sorted(
        [
            p
            for p in workspace.iterdir()
            if p.is_file() and p.suffix.lower() == ".pdf"
        ]
    )
    if len(input_pdfs) == 0:
        return ZERO

    input_by_name = {p.name: p for p in input_pdfs}
    input_sha_by_name = {p.name: sha256_file(p) for p in input_pdfs}

    gt_shas = set(gt_by_sha.keys())
    input_shas = set(input_sha_by_name.values())
    if not gt_shas.issubset(input_shas):
        return ZERO

    arxiv_input_names = {name for name, sha in input_sha_by_name.items() if sha in gt_by_sha}
    non_arxiv_input_names = {name for name, sha in input_sha_by_name.items() if sha not in gt_by_sha}
    non_arxiv_input_shas = {input_sha_by_name[name] for name in non_arxiv_input_names}

    scores = dict(ZERO)
    scores["manifest_exists"] = 1.0 if manifest_path.exists() else 0.0
    scores["renamed_dir_exists"] = 1.0 if renamed_dir.exists() and renamed_dir.is_dir() else 0.0
    scores["bibtex_dir_exists"] = 1.0 if bibtex_dir.exists() and bibtex_dir.is_dir() else 0.0

    if not manifest_path.exists():
        return scores

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return scores

    if not isinstance(manifest, list):
        return scores

    scores["manifest_json_valid"] = 1.0

    required_pred_fields = {"original_filename", "arxiv_id", "title", "renamed_filename", "figure_count"}
    valid_manifest = True
    original_names = []
    renamed_names = []
    arxiv_ids = []
    per_item_results = []
    non_arxiv_manifest_entries = []

    for item in manifest:
        if not isinstance(item, dict):
            valid_manifest = False
            break
        if set(item.keys()) != required_pred_fields:
            valid_manifest = False
            break
        original_filename = item.get("original_filename")
        arxiv_id = item.get("arxiv_id")
        title = item.get("title")
        renamed_filename = item.get("renamed_filename")
        figure_count = item.get("figure_count")
        if not (isinstance(original_filename, str) and original_filename.strip()):
            valid_manifest = False
            break
        if original_filename not in input_by_name:
            valid_manifest = False
            break
        sha = input_sha_by_name[original_filename]
        gt = gt_by_sha.get(sha)
        if gt is None:
            non_arxiv_manifest_entries.append(item)
            continue
        if not all(isinstance(x, str) and x.strip() for x in [arxiv_id, title, renamed_filename]):
            valid_manifest = False
            break
        if not isinstance(figure_count, int) or figure_count < 0:
            valid_manifest = False
            break
        original_names.append(original_filename)
        renamed_names.append(renamed_filename)
        arxiv_ids.append(arxiv_id)
        per_item_results.append(
            {
                "pred": item,
                "gt": gt,
                "input_path": input_by_name[original_filename],
            }
        )

    if not valid_manifest:
        scores["manifest_json_valid"] = 0.0
        return scores

    no_duplicate_originals = len(set(original_names)) == len(original_names)
    no_duplicate_renamed = len(set(renamed_names)) == len(renamed_names)
    no_duplicate_arxiv_ids = len(set(arxiv_ids)) == len(arxiv_ids)
    full_coverage = set(original_names) == arxiv_input_names and len(per_item_results) == len(arxiv_input_names)
    scores["input_coverage_consistent"] = (
        1.0 if no_duplicate_originals and no_duplicate_renamed and no_duplicate_arxiv_ids and full_coverage else 0.0
    )

    byte_identical_ok = True
    arxiv_correct = 0
    title_correct = 0
    filename_correct = 0
    figure_count_correct = 0
    bib_created = 0
    bib_exact = 0
    corrupted_arxiv = 0
    corrupted_title = 0
    corrupted_filename = 0
    corrupted_figure_count = 0
    corrupted_bib = 0

    for item in per_item_results:
        pred = item["pred"]
        gt = item["gt"]
        input_path = item["input_path"]

        expected_arxiv_id = str(gt["arxiv_id"]).strip()
        expected_title = str(gt["title"]).strip()
        expected_filename = sanitize_title(expected_title)
        expected_figure_count = int(gt["figure_count"])

        renamed_path = renamed_dir / pred["renamed_filename"]
        if not renamed_path.exists() or not renamed_path.is_file():
            byte_identical_ok = False
        else:
            if sha256_file(renamed_path) != sha256_file(input_path):
                byte_identical_ok = False

        is_corrupted = gt.get("input_sha256") in corrupted_shas
        if pred["arxiv_id"].strip() == expected_arxiv_id:
            arxiv_correct += 1
            if is_corrupted:
                corrupted_arxiv += 1

        if normalize_casefold_text(pred["title"]) == normalize_casefold_text(expected_title):
            title_correct += 1
            if is_corrupted:
                corrupted_title += 1

        if normalize_casefold_text(pred["renamed_filename"]) == normalize_casefold_text(expected_filename):
            filename_correct += 1
            if is_corrupted:
                corrupted_filename += 1

        if pred["figure_count"] == expected_figure_count:
            figure_count_correct += 1
            if is_corrupted:
                corrupted_figure_count += 1

        pred_bib = bibtex_dir / f"{expected_arxiv_id}.bib"
        gt_bib = gt_bibtex_dir / f"{expected_arxiv_id}.bib"
        if pred_bib.exists() and pred_bib.is_file():
            bib_created += 1
            try:
                pred_bib_text = normalize_bibtex(pred_bib.read_text(encoding="utf-8"))
                gt_bib_text = normalize_bibtex(gt_bib.read_text(encoding="utf-8"))
                if pred_bib_text == gt_bib_text:
                    bib_exact += 1
                    if is_corrupted:
                        corrupted_bib += 1
            except Exception:
                pass

    non_arxiv_manifest_ok = len(non_arxiv_manifest_entries) == 0
    non_arxiv_renamed_ok = True
    if renamed_dir.exists() and renamed_dir.is_dir():
        for path in renamed_dir.iterdir():
            if not path.is_file() or path.suffix.lower() != ".pdf":
                continue
            try:
                if sha256_file(path) in non_arxiv_input_shas:
                    non_arxiv_renamed_ok = False
                    break
            except Exception:
                non_arxiv_renamed_ok = False
                break

    expected_bib_ids = {str(item["arxiv_id"]).strip() for item in gt_items}
    produced_bib_ids = set()
    if bibtex_dir.exists() and bibtex_dir.is_dir():
        for path in bibtex_dir.iterdir():
            if path.is_file() and path.suffix.lower() == ".bib":
                produced_bib_ids.add(path.stem)
    non_arxiv_bib_ok = produced_bib_ids.issubset(expected_bib_ids)

    results_entries = (
        [p.name for p in results_dir.iterdir()]
        if results_dir.exists() and results_dir.is_dir()
        else []
    )
    extra_results_entries = [
        name
        for name in results_entries
        if name not in {"paper_manifest.json", "renamed_papers", "bibtex"}
    ]
    extra_workspace_count = len(extra_results_entries)

    total = len(gt_items)
    scores["pdf_copies_byte_identical"] = 1.0 if byte_identical_ok and total > 0 else 0.0
    scores["non_arxiv_excluded"] = (
        1.0 if non_arxiv_manifest_ok and non_arxiv_renamed_ok and non_arxiv_bib_ok else 0.0
    )
    scores["workspace_cleanliness"] = cleanliness_score(extra_workspace_count)
    corrupted_count = len(corrupted_shas)
    scores["arxiv_id_accuracy"] = round(arxiv_correct / total, 4) if total > 0 else 0.0
    scores["title_accuracy"] = round(title_correct / total, 4) if total > 0 else 0.0
    scores["filename_accuracy"] = round(filename_correct / total, 4) if total > 0 else 0.0
    normal_figure_count_correct = figure_count_correct - corrupted_figure_count
    normal_count = total - corrupted_count
    weighted_figure_total = normal_count + 5 * corrupted_count
    weighted_figure_correct = normal_figure_count_correct + 5 * corrupted_figure_count
    scores["figure_count_accuracy"] = (
        round(weighted_figure_correct / weighted_figure_total, 4)
        if weighted_figure_total > 0
        else 0.0
    )
    scores["bibtex_files_created"] = round(bib_created / total, 4) if total > 0 else 0.0
    scores["bibtex_exact_match_ratio"] = round(bib_exact / total, 4) if total > 0 else 0.0

    if corrupted_count > 0:
        corrupted_accuracy = (
            corrupted_arxiv / corrupted_count
            + corrupted_title / corrupted_count
            + corrupted_filename / corrupted_count
            + corrupted_figure_count / corrupted_count
            + corrupted_bib / corrupted_count
        ) / 5.0
        scores["corrupted_paper_accuracy"] = round(corrupted_accuracy, 4)
    else:
        scores["corrupted_paper_accuracy"] = 1.0

    hard_checks = [
        "manifest_exists",
        "manifest_json_valid",
        "renamed_dir_exists",
        "bibtex_dir_exists",
        "input_coverage_consistent",
        "pdf_copies_byte_identical",
    ]
    hard_pass = all(scores[k] == 1.0 for k in hard_checks)
    scores["hard_constraint_pass"] = 1.0 if hard_pass else 0.0

    if not hard_pass:
        scores["overall_score"] = 0.0
        return scores

    base_score = round(
        0.05 * scores["arxiv_id_accuracy"]
        + 0.05 * scores["title_accuracy"]
        + 0.05 * scores["filename_accuracy"]
        + 0.15 * scores["figure_count_accuracy"]
        + 0.20 * scores["bibtex_exact_match_ratio"]
        + 0.25 * scores["non_arxiv_excluded"]
        + 0.25 * scores["corrupted_paper_accuracy"],
        4,
    )
    scores["overall_score"] = round(base_score * scores["workspace_cleanliness"], 4)
    return scores
```

## Workspace Path

```
workspace/01_Productivity_Flow/task_3_bibtex
```


## Skills

```
```

## Env

```
OPENROUTER_API_KEY
OPENROUTER_BASE_URL
```

## Warmup

```
apt update
apt install poppler-utils -y
```
