from pydantic import BaseModel

class AOAIConfig(BaseModel):
    endpoint: str
    key: str
    deployment: str
    api_version: str

class QueryRequest(BaseModel):
    user_query: str

class AOAIMessage(BaseModel):
    role: str
    content: str

class AOAIRequest(BaseModel):
    model: str
    messages: list[AOAIMessage]

class AOAIResponseChoice(BaseModel):
    message: AOAIMessage

class AOAIResponse(BaseModel):
    choices: list[AOAIResponseChoice]