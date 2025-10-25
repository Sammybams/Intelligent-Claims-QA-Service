from pydantic import BaseModel

class ClaimExtract(BaseModel):
    document_id: str
    content: dict

class ClaimQARequest(BaseModel):
    document_id: str
    question: str


class ClaimQAResponse(BaseModel):
    answer: str