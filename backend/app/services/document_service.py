"""Text extraction for uploaded evidence documents."""

import io
from typing import Optional

SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "image/png",
    "image/jpeg",
}


def extract_text(filename: str, content: bytes, content_type: Optional[str] = None) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        return _extract_pdf(content)
    if lowered.endswith(".docx"):
        return _extract_docx(content)
    if lowered.endswith((".txt", ".md", ".csv", ".log", ".json")):
        return content.decode("utf-8", errors="ignore")
    if lowered.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
        return _extract_image(content)
    return content.decode("utf-8", errors="ignore")


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:  # noqa: BLE001 - unreadable/encrypted PDFs must not break uploads
        return ""


def _extract_docx(content: bytes) -> str:
    try:
        import docx

        document = docx.Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception:  # noqa: BLE001
        return ""


def _extract_image(content: bytes) -> str:
    """OCR an image when pytesseract and the tesseract binary are available."""
    try:
        import pytesseract
        from PIL import Image

        return pytesseract.image_to_string(Image.open(io.BytesIO(content)))
    except Exception:  # noqa: BLE001 - OCR is optional
        return ""
