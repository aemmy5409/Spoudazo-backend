import pdfplumber
import pytesseract
from PIL import Image
import io
import csv
import json

def parse_timetable(file: bytes, filename: str):
    if filename.endswith(".csv"):
        return parse_csv(file)

    elif filename.endswith(".json"):
        return parse_json(file)

    elif filename.endswith(".pdf"):
        return parse_pdf(file)

    elif filename.endswith((".png", ".jpg", ".jpeg")):
        return parse_image(file)

    else:
        raise ValueError("Unsupported file format")


def parse_csv(file: bytes):
    text = file.decode("utf-8").splitlines()
    reader = csv.DictReader(text)
    timetable = {}
    for row in reader:
        day = row["day"]
        timetable.setdefault(day, []).append({
            "start": row["start_time"],
            "end": row["end_time"],
            "course": row["course"]
        })
    return timetable


def parse_json(file: bytes):
    data = json.loads(file.decode("utf-8"))
    return data  # Already structured


def parse_pdf(file: bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return extract_slots_from_text(text)


def parse_image(file: bytes):
    image = Image.open(io.BytesIO(file))
    text = pytesseract.image_to_string(image)
    return extract_slots_from_text(text)


def extract_slots_from_text(text: str):
    """
    Convert raw OCR text into structured timetable slots.
    This is just a placeholder — adjust depending on the school timetable format.
    """
    timetable = {
        "Monday": [{"start": "09:00", "end": "11:00", "course": "CSC101"}],
        "Tuesday": [{"start": "10:00", "end": "12:00", "course": "MTH102"}],
    }
    return timetable
