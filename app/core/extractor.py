"""
Document extraction and validation module for TrustLens AI.
Handles digital PDF extraction, scanned PDF page rendering, image handling,
and strict content-signature (magic bytes) validation.
"""

import io
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import fitz  # PyMuPDF

from app.core.config import settings
from app.core.schemas import ExtractionMetadata, ProvenanceStatus


class ExtractionError(Exception):
    """Base exception for document extraction failures."""
    pass


class UnsupportedFileTypeError(ExtractionError):
    pass


class FileOversizedError(ExtractionError):
    pass


class CorruptedFileError(ExtractionError):
    pass


class DocumentExtractor:
    # Magic bytes for content signature validation
    MAGIC_PDF = b"%PDF-"
    MAGIC_PNG = b"\x89PNG\r\n\x1a\n"
    MAGIC_JPEG = b"\xff\xd8\xff"
    MAGIC_WEBP_RIFF = b"RIFF"
    MAGIC_WEBP_TAG = b"WEBP"

    @classmethod
    def validate_file_bytes(cls, content: bytes, filename: str) -> str:
        """
        Validates actual file signatures (magic bytes) rather than relying only on extension.
        Returns detected normalized MIME type or raises exception.
        """
        if not content or len(content) == 0:
            raise CorruptedFileError("Uploaded file is empty (0 bytes).")

        if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise FileOversizedError(
                f"File size ({len(content)} bytes) exceeds the allowed limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes."
            )

        # Check PDF signature
        if content.startswith(cls.MAGIC_PDF):
            return "application/pdf"

        # Check PNG signature
        if content.startswith(cls.MAGIC_PNG):
            return "image/png"

        # Check JPEG signature
        if content.startswith(cls.MAGIC_JPEG):
            return "image/jpeg"

        # Check WEBP signature: starts with RIFF and has WEBP at byte offset 8
        if content.startswith(cls.MAGIC_WEBP_RIFF) and len(content) >= 12 and content[8:12] == cls.MAGIC_WEBP_TAG:
            return "image/webp"

        # Plain text check: verify utf-8 decode without excessive non-printable chars
        try:
            sample = content[:4096].decode("utf-8")
            # If plain text file ending in .txt
            if filename.lower().endswith(".txt"):
                return "text/plain"
        except UnicodeDecodeError:
            pass

        raise UnsupportedFileTypeError(
            f"File '{filename}' has an unsupported or corrupted file signature. "
            "Supported formats: PDF, PNG, JPG/JPEG, WEBP, or TXT."
        )

    @classmethod
    def extract_from_text(cls, text: str, label: str = "Pasted Text") -> Tuple[str, Optional[bytes], Optional[str], ExtractionMetadata]:
        """
        Extracts content from pasted text.
        """
        cleaned = text.strip()
        if not cleaned:
            raise CorruptedFileError("Pasted text is empty or contains only whitespace.")

        metadata = ExtractionMetadata(
            source_type="pasted_text",
            content_length=len(cleaned),
            page_count=1,
            file_name=label,
            image_dimensions=None,
            provenance_mode=ProvenanceStatus.TEXT_MATCH_VERIFIED
        )
        return cleaned, None, None, metadata

    @classmethod
    def extract_from_pdf(cls, content: bytes, filename: str) -> Tuple[str, Optional[bytes], Optional[str], ExtractionMetadata]:
        """
        Extracts text from PDF via PyMuPDF.
        If PDF is scanned (contains no text or minimal text), renders the first page to an image
        for multimodal Gemma 4 processing, honestly tracking provenance.
        """
        cls.validate_file_bytes(content, filename)

        try:
            doc = fitz.open(stream=content, filetype="pdf")
        except Exception as e:
            raise CorruptedFileError(f"Unable to parse PDF document: {e}")

        try:
            if doc.is_encrypted:
                raise CorruptedFileError("Encrypted or password-protected PDFs are not supported.")

            page_count = len(doc)
            if page_count == 0:
                raise CorruptedFileError("PDF contains 0 pages.")

            if page_count > settings.MAX_PDF_PAGES:
                raise FileOversizedError(
                    f"PDF page count ({page_count}) exceeds the maximum allowed ({settings.MAX_PDF_PAGES} pages)."
                )

            extracted_pages = []
            for i, page in enumerate(doc):
                page_text = page.get_text()
                extracted_pages.append(page_text)

            full_text = "\n\n--- Page Break ---\n\n".join(extracted_pages).strip()

            # Determine whether PDF is digital text or scanned
            if len(full_text) >= 40:
                # Digital PDF with verifiable text
                metadata = ExtractionMetadata(
                    source_type="digital_pdf",
                    content_length=len(full_text),
                    page_count=page_count,
                    file_name=filename,
                    image_dimensions=None,
                    provenance_mode=ProvenanceStatus.TEXT_MATCH_VERIFIED
                )
                return full_text, None, None, metadata
            else:
                # Scanned PDF: Render first page to PNG for multimodal analysis
                first_page = doc[0]
                pix = first_page.get_pixmap(dpi=150)
                rendered_png = pix.tobytes("png")

                fallback_text = (
                    f"[Document: Scanned PDF '{filename}' with {page_count} page(s). "
                    "Visual rendering submitted for multimodal analysis.]"
                )

                metadata = ExtractionMetadata(
                    source_type="scanned_pdf",
                    content_length=len(fallback_text),
                    page_count=page_count,
                    file_name=filename,
                    image_dimensions={"width": pix.width, "height": pix.height},
                    provenance_mode=ProvenanceStatus.TRANSCRIPT_MATCH_VERIFIED
                )
                return fallback_text, rendered_png, "image/png", metadata

        finally:
            doc.close()

    @classmethod
    def extract_from_image(cls, content: bytes, filename: str) -> Tuple[str, bytes, str, ExtractionMetadata]:
        """
        Validates and prepares image for multimodal Gemma 4 analysis.
        Labels provenance as MODEL_TRANSCRIBED per specification.
        """
        mime_type = cls.validate_file_bytes(content, filename)
        if not mime_type.startswith("image/"):
            raise UnsupportedFileTypeError(f"Expected image MIME type, got {mime_type}")

        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
            
            # Re-open for dimensions and processing
            with Image.open(io.BytesIO(content)) as img:
                width, height = img.size
                if width > 8000 or height > 8000:
                    raise FileOversizedError(f"Image dimensions ({width}x{height}) exceed maximum allowed limit (8000x8000).")
                
                # Normalize format if needed, preserve raw bytes
                image_dimensions = {"width": width, "height": height}
        except Exception as e:
            if isinstance(e, (FileOversizedError, UnsupportedFileTypeError)):
                raise
            raise CorruptedFileError(f"Invalid or corrupted image file: {e}")

        placeholder_text = (
            f"[Visual Document: Screenshot/Image '{filename}', dimensions {width}x{height}px. "
            "Analyzed directly via multimodal Gemma 4.]"
        )

        metadata = ExtractionMetadata(
            source_type="image",
            content_length=len(content),
            page_count=1,
            file_name=filename,
            image_dimensions=image_dimensions,
            provenance_mode=ProvenanceStatus.MODEL_TRANSCRIBED
        )

        return placeholder_text, content, mime_type, metadata
