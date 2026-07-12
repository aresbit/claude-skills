#!/usr/bin/env bash
# Batch-convert PDFs to layout-preserving text so translation agents can read them.
#
# Why: the Read tool renders PDF pages as images; papers over ~20MB or image-heavy
# slides exceed limits and the agent silently gets nothing. Converting to .txt
# first is reliable and lets agents Grep/Read the content directly.
#
# Usage:
#   scripts/extract_pdfs.sh path/to/pdf_dir      # writes <name>.txt next to each PDF
#   scripts/extract_pdfs.sh paper.pdf            # single file
set -euo pipefail

if ! command -v pdftotext >/dev/null 2>&1; then
  echo "pdftotext not found. Install poppler-utils (apt) or poppler (brew)." >&2
  exit 1
fi

target="${1:-.}"

convert_one() {
  local pdf="$1"
  local txt="${pdf%.pdf}.txt"
  # -layout preserves columns/tables, which matters for equations and figures.
  if pdftotext -layout "$pdf" "$txt" 2>/dev/null; then
    printf 'ok   %s -> %s (%s)\n' "$pdf" "$txt" "$(wc -l < "$txt") lines"
  else
    printf 'FAIL %s (corrupt or scanned-image PDF — may need OCR)\n' "$pdf" >&2
  fi
}

if [[ -d "$target" ]]; then
  found=0
  while IFS= read -r -d '' pdf; do
    convert_one "$pdf"; found=1
  done < <(find "$target" -type f -iname '*.pdf' -print0)
  [[ "$found" == 1 ]] || echo "no PDFs found under $target"
elif [[ -f "$target" ]]; then
  convert_one "$target"
else
  echo "not found: $target" >&2; exit 1
fi
