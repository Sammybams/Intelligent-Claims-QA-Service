from pydantic import BaseModel

class ClaimExtract(BaseModel):
    document: bytes
    document_id: str
    content: dict

class ClaimQARequest(BaseModel):
    document_id: str
    question: str