from dataclasses import dataclass
from typing import List

@dataclass
class SectionItem:
    doc_name: str
    heading: str
    page: int
    text: str

@dataclass
class PageItem:
    doc_name: str
    page: int
    text: str
    headings: List[str]  # headings detected on this page

@dataclass
class IngestResult:
    markdown: str
    sections: List[SectionItem]
    pages: List[PageItem]
