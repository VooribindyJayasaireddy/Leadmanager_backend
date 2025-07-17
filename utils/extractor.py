import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from fastapi import UploadFile
import io

async def extract_from_file(file: UploadFile):
    contents = await file.read()
    if file.filename.endswith(".pdf"):
        return extract_from_pdf(contents)
    elif file.filename.endswith(".png") or file.filename.endswith(".jpg"):
        return extract_from_image(contents)
    else:
        return "Unknown", "Unknown", "Unknown"

def extract_from_pdf(contents: bytes):
    doc = fitz.open("pdf", contents)
    text = ""
    for page in doc:
        text += page.get_text()
    return extract_info(text)

def extract_from_image(contents: bytes):
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image)
    return extract_info(text)

def extract_info(text: str):
    import re
    # Try to extract name
    name_match = re.search(r"(Name|Full Name):?\s*([A-Za-z ]+)", text)
    name = name_match.group(2).strip() if name_match else "Unknown"
    # Extract email
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    email = email_match.group(0).strip() if email_match else "unknown@example.com"
    # Extract phone number (simple pattern for 10-15 digits)
    phone_match = re.search(r"(Phone|Mobile|Contact)?\D?(\+?\d[\d\s\-]{8,}\d)", text)
    phone = phone_match.group(2).strip() if phone_match else "Unknown"
    return name, email, phone

