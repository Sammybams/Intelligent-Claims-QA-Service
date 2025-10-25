import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
from schema import ClaimExtract, ClaimQARequest
from src.ocr_extract import make_pdf_searchable

# Import Functions and Models
from src.llm_extract import structure_ocr_extraction
import json
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


# Home
@app.get("/", tags=["Home"])
async def index():
    return {"Project": "Intelligent Claims QA Service"}


@app.get("/extract_history", tags=["OCR Extraction"])
async def extract_history():
    payload = jsonable_encoder(temp_storage)
    return JSONResponse(content=payload)


         
# OCR Extraction Endpoint
@app.post("/extract", tags=["OCR Extraction"])
async def extract_ocr(document: UploadFile = File(...)):

    # Verify if document is image or pdf
    if document.content_type not in ["image/jpeg", "image/jpg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid document type. Only JPEG, JPG, PNG, and PDF are supported.")
    
    # Load file
    
    doc_bytes = await document.read()
    unique_document_id = str(uuid.uuid4()) # Unique ID document using uuid
    searchable_pdf = make_pdf_searchable(doc_bytes, unique_document_id)

    result = structure_ocr_extraction(searchable_pdf)
    # print(result)


    new_extract = ClaimExtract(
        document_id = unique_document_id,
        # Load string-like json as JSON
        content = json.loads(result)
    )
    temp_storage[unique_document_id] = new_extract.dict()
    return new_extract


@app.post("/ask", tags=["Question Answering"])
async def ask_question(request: ClaimQARequest):
    document_id = request.document_id
    question = request.question

    if document_id not in temp_storage:
        raise HTTPException(status_code=404, detail="Document ID not found.")

    return