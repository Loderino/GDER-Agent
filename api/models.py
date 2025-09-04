from typing import Optional
from pydantic import BaseModel

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelsResponse(BaseModel):
    object: str = "list"
    data: list[Model]

class Message(BaseModel):
    role: Optional[str]
    content: Optional[str]
    refusal: Optional[str]
    annotations: Optional[list]

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    logprob: Optional[float]
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: dict[str, int|dict]

class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: dict[str, str]
    logprob: Optional[float]
    finish_reason: Optional[str]

class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: Optional[dict]