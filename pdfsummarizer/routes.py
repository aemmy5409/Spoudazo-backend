# pdfsummarizer/routes.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from pdfsummarizer.controller import summarize_pdf_with_gemini

router = APIRouter(prefix="/pdf", tags=["PDF Summarizer"])

@router.post("/summarize")
async def summarize_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file and returns a student-friendly summary.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()

    summary = summarize_pdf_with_gemini(file_bytes, filename=file.filename)

    if summary.startswith("⚠️"):
        raise HTTPException(status_code=500, detail=summary)

    return {
        "summary": summary,
        "meta": {
            "filename": file.filename,
            "size_kb": round(len(file_bytes) / 1024, 2),
        },
    }
