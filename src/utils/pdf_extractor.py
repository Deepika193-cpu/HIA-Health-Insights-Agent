import pdfplumber
import streamlit as st
from config.app_config import MAX_PDF_PAGES
from utils.validators import validate_pdf_file, validate_pdf_content

# Common install location when Tesseract's Windows installer doesn't add
# itself to PATH. Used only as a fallback if the "tesseract" command isn't
# already reachable.
_WINDOWS_TESSERACT_FALLBACK_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _ocr_pdf(pdf):
    """Run OCR on every page of an already-open pdfplumber PDF and return
    the combined text, or None if OCR isn't available/fails."""
    try:
        import pytesseract
    except ImportError:
        return None, (
            "This looks like a scanned/photographed document with no text layer. "
            "OCR support isn't installed — run `pip install pytesseract` and install "
            "the Tesseract OCR engine, then try again."
        )

    # pdfplumber's page.to_image() renders via pypdfium2, which needs no
    # external binary — only Tesseract itself (used below) is external.
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        import os
        if os.path.exists(_WINDOWS_TESSERACT_FALLBACK_PATH):
            pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT_FALLBACK_PATH
        else:
            return None, (
                "This looks like a scanned/photographed document. OCR needs the "
                "Tesseract OCR engine installed on your computer (this is separate "
                "from the Python packages) — see the setup guide for the download link."
            )

    text = ""
    with st.spinner("No text layer found — reading it like a scanned photo (OCR), this can take a moment..."):
        for page in pdf.pages:
            try:
                pil_image = page.to_image(resolution=300).original
                page_text = pytesseract.image_to_string(pil_image)
                if page_text:
                    text += page_text + "\n"
            except Exception:
                continue  # skip a page OCR couldn't handle, keep the rest

    return text, None


def extract_text_from_pdf(pdf_file):
    """Extract and validate text from PDF file, falling back to OCR for
    scanned/photographed documents with no embedded text layer."""
    try:
        # Validate file first
        is_valid, error = validate_pdf_file(pdf_file)
        if not is_valid:
            return error

        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            if len(pdf.pages) > MAX_PDF_PAGES:
                return f"PDF exceeds maximum page limit of {MAX_PDF_PAGES}"

            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                # A single page with no text (blank page, image-only page,
                # cover page) is skipped rather than failing the whole doc.

            if not text.strip():
                # No page had a text layer at all — likely a scanned/photo PDF.
                # Re-open pages for OCR (pdf.pages is still valid within the
                # same `with` block).
                ocr_text, ocr_error = _ocr_pdf(pdf)
                if ocr_error:
                    return ocr_error
                text = ocr_text

        if not text.strip():
            return (
                "Could not extract any readable text from this PDF, even with OCR. "
                "Please try a clearer scan/photo, or a different file."
            )

        # Validate extracted content
        is_valid, error = validate_pdf_content(text)
        if not is_valid:
            return error

        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"