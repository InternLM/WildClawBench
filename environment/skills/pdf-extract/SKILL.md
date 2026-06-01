---
name: pdf-extract
description: Extract text and embedded images from PDF files using PyMuPDF (fitz).
metadata: {"clawdbot":{"emoji":"📄","requires":{"bins":["python3"]},"pip":["pymupdf"]}}
---

# PDF Extract (PyMuPDF)

Pull plain text and/or embedded images out of a PDF for downstream reasoning.

## Quick start

Extract all text to stdout:

```bash
python3 {baseDir}/scripts/extract.py /path/to/doc.pdf
```

Text to a file, images to a folder, a page range:

```bash
python3 {baseDir}/scripts/extract.py /path/to/doc.pdf \
  --out /tmp_workspace/results/doc.txt \
  --images-dir /tmp_workspace/results/imgs \
  --pages 1-5
```

Outputs the page count and per-page text. Requires `pymupdf` (already in requirements.txt).
