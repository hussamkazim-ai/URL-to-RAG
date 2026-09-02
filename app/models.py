from pydantic import BaseModel

class URLRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

class DeleteRequest(BaseModel):
    domain: str