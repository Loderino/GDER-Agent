from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import time
import uuid
import json

from agent.agent import Agent
from langchain_core.messages import HumanMessage, AIMessage
from api.models import *

router = APIRouter(prefix="/v1")

agent=Agent()


@router.get("/models")
async def list_models():
    models = [
        Model(
            id="GDER-agent",
            created=1677610602,
            owned_by="Loderino"
        )
    ]
    return ModelsResponse(data=models)

async def chat_completion(messages):
    user_message = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
    if "### Task:\n" in user_message:
        follow_ups = {
            "follow_ups": [
                "Расскажите о шахматке бронирования",
                "Какие инструменты доступны на realtycalendar.ru?",
                "Как использовать календарь событий?"
            ]
        }

        return ChatCompletionResponse(
            id = f"chatcmpl-{uuid.uuid4()}",
            object = "chat.completion",
            created = int(time.time()),
            model= "GDER-agent",
            choices= [
                ChatCompletionChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=json.dumps(follow_ups),
                        refusal=None,
                        annotations=[]
                    ),
                    logprob=None,
                    finish_reason="stop"
                )
            ],
            usage= {
                "prompt_tokens": 50,
                "completion_tokens": len(json.dumps(follow_ups)) // 4,
                "total_tokens": 50 + (len(json.dumps(follow_ups)) // 4),
                "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
                "completion_tokens_details": {
                    "reasoning_tokens": 0, 
                    "audio_tokens": 0, 
                    "accepted_prediction_tokens": 0, 
                    "rejected_prediction_tokens": 0
                }
            }
        ) 

    # Обычный запрос - преобразуем сообщения
    langchain_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            langchain_messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            langchain_messages.append(AIMessage(content=msg.get("content", "")))

    response = await agent.communicate(1, langchain_messages, verbose=True)

    return ChatCompletionResponse(
        id = f"chatcmpl-{uuid.uuid4()}",
        object = "chat.completion",
        created = int(time.time()),
        model= "GDER-agent",
        choices= [
            ChatCompletionChoice(
                index=0,
                message=Message(
                    role="assistant",
                    content=response,
                    refusal=None,
                    annotations=[]
                ),
                logprob=None,
                finish_reason="stop"
            )
        ],
        usage= {
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
        }
    )

def split_text(text, chunk_size=8):
    """
    Разбивает текст на равные чанки

    Args:
        text: исходный текст
        chunk_size: размер чанка в символах

    Returns:
        list: список чанков
    """
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]


def stream_imitation(text):
    answer_id = f"chatcmpl-{uuid.uuid4()}"

    first_chunk = {
        "id":answer_id,
        "object":"chat.completion.chunk",
        "created": int(time.time()),
        "model": "GDER-agent",
        "service_tier": "default", 
        "system_fingerprint": None,
        "choices":[
            {
                "index":0,
                "delta": {
                    "role":"assistant",
                    "content":"",
                    "refusal": None
                },
                "logprobs":None,
                "finish_reason":None
            }
        ],
        "usage":None
    }
    yield f"data: {first_chunk}\n\n"
    for chunk in split_text(text):
        openai_style_chunk = {
        "id":answer_id,
        "object":"chat.completion.chunk",
        "created": int(time.time()),
        "model": "GDER-agent",
        "service_tier": "default", 
        "system_fingerprint": None,
        "choices":[
            {
                "index":0,
                "delta": {
                    "content":chunk
                },
                "logprobs":None,
                "finish_reason":None
            }
        ],
        "usage":None
    }
        yield f"data: {json.dumps(openai_style_chunk)}\n\n"

    chunk = {
        "id":answer_id,
        "object":"chat.completion.chunk",
        "created": int(time.time()),
        "model": "GDER-agent",
        "service_tier": "default", 
        "system_fingerprint": None,
        "choices":[
            {
                "index":0,
                "delta": {},
                "logprobs":None,
                "finish_reason":"stop"
            }
        ],
        "usage":None
    }
    yield f"data: {json.dumps(chunk)}\n\n"

    chunk = {
        "id":answer_id,
        "object":"chat.completion.chunk",
        "created": int(time.time()),
        "model": "GDER-agent",
        "service_tier": "default", 
        "system_fingerprint": None,
        "choices":[],
        "usage":{"prompt_tokens": 11, "completion_tokens": 14, "total_tokens": 25, "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 0, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}}
    }    
    yield f"data: {json.dumps(chunk)}\n\n"

    yield "data: [DONE]"

async def chat_completion_stream(messages):
    langchain_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            langchain_messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            langchain_messages.append(AIMessage(content=msg.get("content", "")))

    response = await agent.communicate(1, langchain_messages, verbose=True)
    return StreamingResponse(stream_imitation(response), media_type="text/plain")

@router.post("/chat/completions")
async def create_chat_completion(request: Request):
    try:
        data = await request.json()
        messages = data.get("messages", [])
        if data["stream"]:
            return await chat_completion_stream(messages)
        return await chat_completion(messages)    

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
