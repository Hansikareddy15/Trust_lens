"""
Unit tests for DocumentExtractor and file validation.
"""

import io
import pytest
from PIL import Image
import fitz

from app.core.extractor import (
    DocumentExtractor,
    UnsupportedFileTypeError,
    FileOversizedError,
    CorruptedFileError,
)
from app.core.schemas import ProvenanceStatus


def create_minimal_pdf_bytes(text: str = "Test document content") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_minimal_png_bytes(width: int = 100, height: int = 100) -> bytes:
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_text_extraction():
    text = "Here is a sample offer letter for software engineering."
    extracted, img, mime, meta = DocumentExtractor.extract_from_text(text)
    assert extracted == text
    assert img is None
    assert mime is None
    assert meta.source_type == "pasted_text"
    assert meta.provenance_mode == ProvenanceStatus.TEXT_MATCH_VERIFIED


def test_empty_text_rejection():
    with pytest.raises(CorruptedFileError):
        DocumentExtractor.extract_from_text("   \n\t  ")


def test_pdf_extraction_digital():
    pdf_content = (
        "Decode Labs Internship Offer\n"
        "We are pleased to extend an offer for Software Trainee.\n"
        "No registration fee is required."
    )
    pdf_bytes = create_minimal_pdf_bytes(pdf_content)
    extracted, img, mime, meta = DocumentExtractor.extract_from_pdf(pdf_bytes, "offer.pdf")
    assert "Decode Labs Internship Offer" in extracted
    assert meta.source_type == "digital_pdf"
    assert meta.page_count == 1
    assert meta.provenance_mode == ProvenanceStatus.TEXT_MATCH_VERIFIED


def test_image_extraction():
    png_bytes = create_minimal_png_bytes(200, 200)
    text, img, mime, meta = DocumentExtractor.extract_from_image(png_bytes, "screenshot.png")
    assert mime == "image/png"
    assert img == png_bytes
    assert meta.source_type == "image"
    assert meta.provenance_mode == ProvenanceStatus.MODEL_TRANSCRIBED
    assert meta.image_dimensions == {"width": 200, "height": 200}


def test_empty_file_rejection():
    with pytest.raises(CorruptedFileError):
        DocumentExtractor.validate_file_bytes(b"", "empty.pdf")


def test_corrupted_signature_rejection():
    fake_pdf = b"NOT_A_REAL_PDF_HEADER"
    with pytest.raises(UnsupportedFileTypeError):
        DocumentExtractor.validate_file_bytes(fake_pdf, "fake.pdf")
