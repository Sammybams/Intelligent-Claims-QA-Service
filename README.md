# Intelligent Claims QA Service

Convert scanned/ photographed medical / insurance claim documents into a structured JSON representation and answer natural-language questions about those claims — **only** using the extracted data.  
This repository demonstrates a production-minded pipeline that uses **Azure Document Intelligence** to make scanned documents searchable and an LLM (OpenAI / Azure OpenAI) with **schema-first structured output** to extract validated claims data and run question-answering on the structured extract.

---

## Table of contents

- [Why this design?](#why-this-design)  
- [High-level architecture](#high-level-architecture)  
- [Pipeline: step-by-step](#pipeline-step-by-step)  
- [Schema & OpenAI strict JSON rules](#schema--openai-strict-json-rules)  
- [Repository structure](#repository-structure)  
- [Run locally (quick start)](#run-locally-quick-start)  
- [API / Try it (Swagger UI)](#api--try-it-swagger-ui)  
- [Examples](#examples)  
- [Prompts & YAML snippets](#prompts--yaml-snippets)  
- [Sanitizer & Pydantic tips (schema generation)](#sanitizer--pydantic-tips)  
- [Troubleshooting & FAQ](#troubleshooting--faq)  
- [Next steps & improvements](#next-steps--improvements)  
- [Contributing & License](#contributing--license)

---

## Why this design?

- **Scanned documents are common.** Many claims arrive as photos or scanned PDFs where text is not selectable. Off-the-shelf LLMs perform poorly when asked to parse raw images or OCR blobs directly.
- **Make documents readable for LLMs.** Azure Document Intelligence (Document Analyzer / Form Recognizer) converts image scans into structured outputs (text blocks, key-value pairs, and tables) and can produce a *searchable PDF* which preserves layout + searchable text. That searchable result is far easier and more reliable for LLMs to consume.
- **Deterministic extraction with schema-first output.** Instead of free-text extraction, we drive the LLM to return a strict JSON schema (Pydantic / JSON Schema) so downstream systems can validate, store, or route the results programmatically with minimal manual review.
- **QA only from extracted data.** The QA stage receives the structured JSON extract and the user question. The assistant is instructed to answer **only** from the extract and to reply `"I don't know"` if the extract lacks the information — eliminating hallucinations.

---

## High-level architecture

```

[PDF/Image upload] --> [Azure Document Intelligence]
-> searchabled PDF + OCR output (text, kv_pairs, tables)
-> saved as ocr_extract JSON
--> [Normalizer] (format Azure output to LLM-friendly context)
--> [LLM structured extraction]
-> returns validated JSON (per schema)
--> [QA agent]
-> receives structured JSON + question -> returns short answer

```

- Azure DI = best at handling photo-scans and generating searchable PDF + structured outputs.
- LLM Extraction = uses `text_format: { type: "json_schema" }` or function-calling to return exact JSON matching the schema.
- QA = small prompt that uses only the `ocr_extract` JSON (no external lookups).

---

## Pipeline: step-by-step

1. **Upload Document (PDF / image)**  
   - Accept a PDF or image upload through the API / UI.

2. **Azure Document Intelligence**  
   - Call the Document Analyzer to produce:
     - `raw_text` (paragraphs/lines),  
     - `key_value_pairs` (extracted kv pairs & confidence),  
     - `tables` (header cells and rows),  
     - export a searchable PDF (recommended for archiving and human review).  

3. **Normalize**  
   - Transform Azure results into a smaller, stable context for the LLM:
     - `kv_candidates`, trimmed `raw_text` excerpts, and table previews.
     - Add page/line info where available.

4. **Structured extraction (LLM)**  
   - Load your JSON Schema (generated from Pydantic or hand-written).
   - Sanitize the schema to satisfy OpenAI strict rules (see below).
   - Call the LLM with Structured Output with a defined schema.
   - The model returns a structured `claims_summary` JSON that matches the schema.

5. **Validation & persistence**  
   - Parse the model output with Pydantic (ensures types) and reject/flag low-confidence fields for human review.

6. **Question Answering**  
   - Provide the QA prompt with the validated `claims_summary` (structured JSON) and the user question.
   - Model must answer only from `claims_summary`. If missing, respond `"I don't know"`.

---

## Schema & OpenAI strict JSON rules

OpenAI strict `json_schema` (and some function-calling usage) requires:

- **Every object node** that has `properties` must include:
  - `"additionalProperties"` explicitly (commonly `false`), and  
  - `"required"` — an array listing the property keys present in `properties`.
- If you need dynamic keys (e.g., table `cells` with column names unknown in advance), set:
  - `properties: {}` and `additionalProperties: { "type":"string" }` and `required: []` for that node.

We recommend generating your schema from Pydantic and running a sanitizer that injects `additionalProperties` and correct `required` arrays for every object node before sending it to OpenAI.

---

## Repository structure

```

Intelligent-Claims-QA-Service/
├── README.md                  # (this file)
├── main.py                    # main entry point for running the FastAPI demo/service
├── schema.py                  # Pydantic / schema definitions for claims summary + sanitizer helpers
├── requirements.txt           # Python dependencies
├── .env.example               # example environment variables (keys for Azure, OpenAI)
├── src/                       # project source / helpers (LLM/azure connectors, utilities)
└── tests/                     # unit tests (optional / recommended)

````

- `.env.example` already contains the sample keys layout. **Do not commit real secrets** — copy to `.env` and fill your real keys.

---

## Run locally (quick start)

**Prerequisites**
- Python 3.11+  
- Virtual environment tooling (venv or conda)  
- Azure + OpenAI credentials (if calling those services)

**Install**
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
````

**Environment**

```bash
cp .env.example .env
# Edit .env and fill in your actual keys:
# AZURE_ENDPOINT=...
# AZURE_KEY=...
# OPENAI_API_KEY=...  OR
# AZURE_OPENAI_KEY=... and AZURE_OPENAI_ENDPOINT=...
```

**Start the app**

```bash
python -m uvicorn main:app --reload
```

**Open the docs**

* Swagger UI: `http://127.0.0.1:8000/docs` — use this to interact with endpoints and try uploads/questions.

---

## API / Example endpoints

> Exact paths depend on `main.py` implementation. Typical endpoints:

* `POST /extract` — upload a PDF or image file; returns `ocr_extract` (Document Intelligence analyzer output + LLM normalized extract).
* `POST /qa` — send `{ "document_id": <string>, "question": "<text>" }` and get back a short answer.