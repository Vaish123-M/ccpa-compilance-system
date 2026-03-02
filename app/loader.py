import re
from pathlib import Path

from pypdf import PdfReader


SECTION_PATTERN = re.compile(r"(Section\s+1798\.\d{3}(?:\.\d+)?)", flags=re.IGNORECASE)


def _read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    page_text = []
    for page in reader.pages:
        page_text.append(page.extract_text() or "")
    return "\n".join(page_text)


def load_ccpa_sections(pdf_path: str) -> list[dict[str, str]]:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"CCPA statute PDF not found at: {path}")

    full_text = _read_pdf_text(path)
    matches = list(SECTION_PATTERN.finditer(full_text))
    if not matches:
        raise ValueError("No CCPA sections matching 'Section 1798.xxx' found in PDF")

    sections: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        section_name = re.sub(r"\s+", " ", match.group(1)).strip()
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(full_text)
        section_text = full_text[start:end].strip()
        if section_text:
            sections.append({"section": section_name, "text": section_text})

    if not sections:
        raise ValueError("Section parsing produced zero sections")

    return sections
