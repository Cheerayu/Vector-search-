from pathlib import Path
from typing import List, Tuple, Dict, Set
from .doc_models import SectionItem, PageItem, IngestResult
from docling.document_converter import DocumentConverter

def _page_from_item(item) -> int:
    try:
        if getattr(item, "prov", None):
            p = item.prov[0]
            if hasattr(p, "page_no") and p.page_no is not None:
                return int(p.page_no)
    except Exception:
        pass
    return 1

def _is_heading(item) -> bool:
    try:
        labels = getattr(item, "labels", None)
        if labels and ("heading" in {str(l).lower() for l in labels}):
            return True
    except Exception:
        pass
    try:
        meta = getattr(item, "dl_meta", None) or getattr(item, "meta", None)
        if meta and isinstance(getattr(meta, "headings", None), list) and meta.headings:
            return True
    except Exception:
        pass
    return False

def _heading_level_guess(text: str) -> str:
    # Simple heuristic: numbers/prefixes map to H2/H3; short uppercase to H1
    t = (text or "").strip()
    if not t:
        return "H2"
    if len(t) <= 40 and t.upper() == t and any(c.isalpha() for c in t):
        return "H1"
    if t[:3].strip().split(" ")[0].rstrip(".").isdigit():
        return "H2"
    if t[:1].isdigit():
        return "H3"
    return "H2"

def convert_to_markdown_and_sections(path: str | Path) -> Tuple[IngestResult, str | None]:
    path = Path(path)
    try:
        converter = DocumentConverter()
        result = converter.convert(path)
        doc = result.document
    except Exception as e:
        return IngestResult(markdown="", sections=[], pages=[]), f"{path.name}: {e}"

    try:
        markdown_text = doc.export_to_markdown()
    except Exception:
        markdown_text = ""

    # Section grouping (preserved for potential use later)
    sections: List[SectionItem] = []
    current_heading = "Untitled"
    current_page = 1
    buf: List[str] = []

    def flush_section():
        nonlocal buf
        if buf:
            sections.append(SectionItem(doc_name=path.name, heading=current_heading, page=current_page, text="\n".join(buf).strip()))
            buf = []

    try:
        iterator = doc.iterate_items(doc.body, with_groups=True)
    except Exception:
        iterator = []

    # Page aggregation: text and headings per page
    page_text: Dict[int, List[str]] = {}
    page_headings: Dict[int, Set[str]] = {}

    for item, _lvl in iterator:
        pg = _page_from_item(item)
        current_page = pg or current_page

        # Detect headings (from labels or dl_meta.headings)
        is_head = _is_heading(item)
        heading_text = None

        if is_head:
            # Prefer item text; else use dl_meta.headings[0]
            t = getattr(item, "text", None)
            if t and t.strip():
                heading_text = t.strip()
            else:
                try:
                    meta = getattr(item, "dl_meta", None) or getattr(item, "meta", None)
                    if meta and getattr(meta, "headings", None):
                        heading_text = str(meta.headings[0]).strip()
                except Exception:
                    pass

            if heading_text:
                level = _heading_level_guess(heading_text)
                page_headings.setdefault(current_page, set()).add(f"{level}: {heading_text}")
                # For sections stream
                flush_section()
                current_heading = heading_text

        # Accumulate text for section and page
        label = getattr(item, "label", None)
        is_table = str(label).lower() == "table" if label else False
        if is_table:
            try:
                md = item.export_to_markdown(doc)
            except Exception:
                md = None
            if md:
                buf.append(md.strip())
                page_text.setdefault(current_page, []).append(md.strip())
        else:
            t = getattr(item, "text", None)
            if t and t.strip():
                buf.append(t.strip())
                page_text.setdefault(current_page, []).append(t.strip())

    flush_section()

    # Build ordered pages
    pages: List[PageItem] = []
    for pg in sorted(page_text.keys()):
        pages.append(
            PageItem(
                doc_name=path.name,
                page=pg,
                text="\n".join(page_text.get(pg, [])).strip(),
                headings=sorted(list(page_headings.get(pg, set())))
            )
        )

    return IngestResult(markdown=markdown_text, sections=sections, pages=pages), None
