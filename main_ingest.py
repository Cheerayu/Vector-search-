import argparse
from pathlib import Path
from typing import List
from tqdm import tqdm
import os

from .docling_convert import convert_to_markdown_and_sections
from .fs_utils import ensure_dir, write_text

SUPPORTED_EXT = (".pdf", ".docx", ".pptx", ".html")

def page_block(doc_name: str, page: int, headings: List[str], text: str) -> str:
    head_str = ", ".join(headings) if headings else "None"
    return "\n".join([
        "---------",
        "meta data",
        "---------",
        f"Doc: {doc_name}",
        f"Page: {page}",
        f"Headings: {head_str}",
        "",
        "---------",
        "respective text",
        "---------",
        text.strip(),
        ""
    ])

def main():
    ap = argparse.ArgumentParser(description="Docling ingest -> ONE consolidated TXT (page-wise with headings)")
    ap.add_argument("--files", nargs="+", required=True, help="Explicit file paths to process (space-separated)")
    ap.add_argument("--out", dest="out", default="out_txt", help="Output folder (combined.txt)")
    ap.add_argument("--cpu-only", action="store_true", help="Force CPU and suppress pin_memory warnings")
    args = ap.parse_args()

    if args.cpu_only:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    out_dir = ensure_dir(args.out)
    combined_path = out_dir / "combined.txt"
    log_path = out_dir / "_errors.txt"

    candidates = [Path(f) for f in args.files if Path(f).suffix.lower() in SUPPORTED_EXT]
    if not candidates:
        write_text(log_path, "No supported files given.")
        write_text(combined_path, "No content.")
        print("No supported files given.")
        return

    out_lines: List[str] = []
    errors: List[str] = []

    out_lines.append("# Combined page-wise export with headings")
    out_lines.append(f"# Files: {len(candidates)}")
    out_lines.append("")

    for f in tqdm(candidates, desc="Processing files", unit="file"):
        res, err = convert_to_markdown_and_sections(f)
        if err:
            errors.append(err)
            continue

        if not res.pages:
            # fallback single-page with markdown
            txt = (res.markdown or "").strip()
            out_lines.append(page_block(f.name, 1, [], txt))
            continue

        for p in res.pages:
            out_lines.append(page_block(p.doc_name, p.page, p.headings, p.text))

    out_lines.append("# End")
    if errors:
        out_lines.append(f"# Errors: {len(errors)} (see _errors.txt)")

    write_text(combined_path, "\n".join(out_lines))
    write_text(log_path, "\n".join(errors) if errors else "No errors.")
    print(f"Wrote: {combined_path.name}, {log_path.name} ({'errors' if errors else 'no errors'})")

if __name__ == "__main__":
    main()
