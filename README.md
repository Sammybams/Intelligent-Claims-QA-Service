# Intelligent Claims QA Service

A small, focused service that converts scanned/photographed medical/insurance claim documents into a structured JSON representation and answers natural-language questions about those claims.  
This project uses **Azure Document Intelligence** to make documents searchable/structured and **OpenAI function-calling / structured output** to produce and validate the final JSON and handle question answering.

---

## Table of contents

- [Overview](#overview)  
- [Design & Approach](#design--approach)  
  - [1) Make documents searchable](#1-make-documents-searchable)  
  - [2) Structured extraction (Schema-driven)](#2-structured-extraction-schema-driven)  
  - [3) Question answering over structured output](#3-question-answering-over-structured-output)  
- [Schema & strict JSON requirements (OpenAI)](#schema--strict-json-requirements-openai)  
- [Repository structure (observed)](#repository-structure-observed)  
- [How to run (local)](#how-to-run-local)  
- [Examples & prompts](#examples--prompts)  
- [Troubleshooting & tips](#troubleshooting--tips)  
- [Next steps & improvements](#next-steps--improvements)

---

## Overview

This service processes claims documents (including photo-scanned PDFs) into a normalized JSON representation and answers reviewer or user questions only from that extracted data — no hallucinations. The pipeline aims to be:

- **Accurate**: use Azure Document Intelligence to extract text, key-value pairs and tables.  
- **Deterministic**: schema-first extraction so downstream systems can validate automatically.  
- **Auditable**: every value includes a `confidence`, a `source` and `raw_text_excerpt` where possible.  
- **Safe for structured output**: JSON Schema crafted to meet OpenAI's `json_schema` strict rules (every object node must provide `additionalProperties` and `required` listing property keys).

---

## Design & Approach

### 1) Make documents searchable

- Use **Azure Document Intelligence** (Form Recognizer / Document Intelligence) to process documents and convert image scans into:
  - `raw_text` (page/line/word),
  - `kv_candidates` (key-value pairs),
  - `tables` (array of column headers and rows),
  - optional metadata (page numbers, confidence from Azure).
- Store the document analysis as a JSON blob (this becomes the "ocr_extract" used by the rest of the pipeline).

Why Azure DI? its layout/field/table extraction is robust on photo-scans and returns rich structure that makes later normalization far easier.

### 2) Structured extraction (Schema-driven)

- Define a strict JSON schema / Pydantic model for the claims summary (top-level keys: `document_id`, `patient`, `demographics`, `diagnoses`, `medications`, `procedures`, `admission`, `vitals`, `labs`, `billing`, `tables`, `notes`, `metadata`, `warnings`, etc.).
- Use an LLM (OpenAI) with **function-calling** or `text_format: { type: "json_schema" }` to ask the model to return **only** the structured JSON that matches the schema.
- For maximum determinism with OpenAI’s strict validator:
  - Ensure every object node that declares `properties` includes `additionalProperties` (explicit) and a `required` array listing the property keys (even if you'll accept `null` as values).
  - If you use Pydantic to generate the schema, set `Config.extra = Extra.forbid` (pydantic v1) or `model_config={"extra":"forbid"}` (v2) and post-process the schema to add the `additionalProperties` / `required` keys where needed.
  - Example sanitizer (used when generating the schema) ensures compatibility with OpenAI.

**Important**: Table fields are represented as dictionaries keyed by table IDs (e.g. `table_1`) and each row has `row_id` and `cells`, where `cells` may contain dynamic column names and string values (the schema must explicitly allow `additionalProperties` for `cells` with a string value schema).

### 3) Question answering over structured output

- The QA component is **schema-driven**: instead of asking the LLM to read raw OCR text, pass the *structured JSON extract* (`ocr_extract`) and the user’s question.
- The prompt instructs the model to answer **only from the extract**; if the information is not available, respond with `"I don't know"` or a short negative answer.
- Optionally provide short-form or long-form QnA prompts. For production we recommend a **short-answer-only** prompt for direct answers in the language of the user.

---

## Schema & strict JSON requirements (OpenAI)

OpenAI `json_schema` strict mode enforces extra rules that are easy to trip over:

- Every `type: "object"` node that lists `properties` **must** include:
  - `additionalProperties` (explicit; `false` or a permissive schema), and
  - `required` — an array that lists the property keys declared in `properties`.
- For nested maps with dynamic keys (e.g., `cells` inside a table row), include `additionalProperties: {"type":"string"}` and set `properties: {}` and `required: []`.
- If you generate JSON Schema from Pydantic automatically, either:
  - Use `Config.schema_extra` (Pydantic v1) hook to inject `additionalProperties: False` and `required` lists into the generated schema, or
  - Post-process the generated schema with a small sanitizer function prior to sending to OpenAI.

**Repository Structure**

Intelligent-Claims-QA-Service/

├── README.md                  # (this file — suggested)
├── main.py                    # main entry point for running a demo/service
├── schema.py                  # Pydantic / schema definitions for claims endpoint requests
├── requirements.txt           # Python dependencies
├── .env.example               # example environment variables (keys for Azure, OpenAI)
├── src/                       # (project source / helpers; Contains LLM/azure drivers)
└── other files (experimentation notebooks, tests etc)


