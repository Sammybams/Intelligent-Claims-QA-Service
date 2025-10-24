import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from typing import Optional, Dict, List
import uuid

from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title = "Intelligent Claims QA Service API",
    description = "API Documenation",
    version = "1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

temp_storage: Dict[str, Dict] = {}

# unique_document_id = str(uuid.uuid4())

# Home
@app.get("/", tags=["Home"])
def index():
    return {"Project": "Intelligent Claims QA Service"}


# OCR Extraction Endpoint
@app.post("/extract", tags=["OCR Extraction"])
def extract_ocr(document: UploadFile = File(...)):

    # Verify if document is image or pdf
    if document.content_type not in ["image/jpeg", "image/jpg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid document type. Only JPEG, JPG, PNG, and PDF are supported.")
    
    return 
