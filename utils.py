# utils.py
# Small helper to read the text from a PDF resume.

from pypdf import PdfReader


def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text = text + page_text + "\n"

    if text.strip() == "":
        raise Exception("No text found in this PDF. It may be a scanned image.")
    return text