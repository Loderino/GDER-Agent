from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import uuid
import json

from agent.agent import Agent
from langchain_core.messages import HumanMessage, AIMessage

mail_agent = Agent()
mail_agent.api_key = ""
mail_agent.api_base = ""
mail_agent.model = "gpt-4o-2024-11-20"



app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int]

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[Model]

# Эндпоинт для списка моделей
@app.get("/v1/models")
async def list_models():
    models = [
        Model(
            id="realtycalendar-agent",
            created=1677610602,
            owned_by="realtycalendar"
        )
    ]
    return ModelsResponse(data=models)

# Эндпоинт для генерации ответа
@app.post("/v1/chat/completions")
async def create_chat_completion(request: Request):
    try:
        data = await request.json()
        messages = data.get("messages", [])

        # Проверка на запрос follow-up вопросов
        user_message = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
        if "### Task:\n" in user_message:
            follow_ups = {
                "follow_ups": [
                    "Расскажите о шахматке бронирования",
                    "Какие инструменты доступны на realtycalendar.ru?",
                    "Как использовать календарь событий?"
                ]
            }

            return {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": data.get("model", "realtycalendar-agent"),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": json.dumps(follow_ups),
                            "refusal": None,
                            "annotations": []
                        },
                        "logprobs": None,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 50,
                    "total_tokens": 100,
                    "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
                    "completion_tokens_details": {
                        "reasoning_tokens": 0, 
                        "audio_tokens": 0, 
                        "accepted_prediction_tokens": 0, 
                        "rejected_prediction_tokens": 0
                    }
                },
                "service_tier": "default",
                "system_fingerprint": None
            }

        # Обычный запрос - преобразуем сообщения
        langchain_messages = []
        for msg in messages:
            if msg.get("role") == "user":
                langchain_messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                langchain_messages.append(AIMessage(content=msg.get("content", "")))

        print(langchain_messages)
        response = await mail_agent.communicate(1, langchain_messages, verbose=True)

        # Формируем ответ в формате OpenAI API
        return {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": data.get("model", "realtycalendar-agent"),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response,
                        "refusal": None,
                        "annotations": []
                    },
                    "logprobs": None,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": len(response) // 4,
                "total_tokens": 50 + (len(response) // 4),
                "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
                "completion_tokens_details": {
                    "reasoning_tokens": 0, 
                    "audio_tokens": 0, 
                    "accepted_prediction_tokens": 0, 
                    "rejected_prediction_tokens": 0
                }
            },
            "service_tier": "default",
            "system_fingerprint": None
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555, reload=False)
