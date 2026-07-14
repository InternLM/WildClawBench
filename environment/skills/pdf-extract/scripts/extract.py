#!/usr/bin/env python3
"""Extract text (and optionally embedded images) from a PDF using PyMuPDF."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _page_range(spec: str, n: int) -> range:
    if not spec:
        return range(n)
    a, _, b = spec.partition("-")
    start = max(1, int(a)) - 1
    end = int(b) if b else int(a)
    return range(start, min(end, n))


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract text/images from a PDF.")
    ap.add_argument("pdf")
    ap.add_argument("--out", default="-", help="text output file, or '-' for stdout")
    ap.add_argument("--images-dir", default="", help="if set, write embedded images here")
    ap.add_argument("--pages", default="", help="1-based page range, e.g. 1-5")
    args = ap.parse_args()

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("PyMuPDF not installed. Run: pip install pymupdf", file=sys.stderr)
        return 2

    src = Path(args.pdf)
    if not src.is_file():
        print(f"not found: {src}", file=sys.stderr)
        return 1

    doc = fitz.open(src)
    pages = _page_range(args.pages, doc.page_count)
    chunks: list[str] = []
    for i in pages:
        chunks.append(f"\n===== page {i + 1} =====\n{doc[i].get_text()}")
    text = "".join(chunks)

    if args.out == "-":
        sys.stdout.write(text)
    else:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"text: {len(text)} chars -> {args.out}", file=sys.stderr)

    if args.images_dir:
        out_dir = Path(args.images_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for i in pages:
            for img in doc[i].get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha >= 4:  # CMYK -> RGB
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                fp = out_dir / f"p{i + 1}_x{xref}.png"
                pix.save(fp)
                count += 1
        print(f"images: {count} -> {out_dir}", file=sys.stderr)

    print(f"pages: {doc.page_count} (extracted {len(list(pages))})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
