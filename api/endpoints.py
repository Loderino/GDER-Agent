from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
import uuid
import json

from api.utils import make_openai_style_response, make_openai_style_chunk
from agent.agent import Agent
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/v1")

agent=Agent()


@router.get("/models")
async def list_models():
    return JSONResponse({"object": "list",
     "data":[
        {
            "id":"GDER-agent",
            "created":1677610602,
            "owned_by":"Loderino"
        }
    ]
    })

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
        return make_openai_style_response(json.dumps(follow_ups), 50, 100) 

    langchain_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            langchain_messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            langchain_messages.append(AIMessage(content=msg.get("content", "")))

    response = await agent.communicate(1, langchain_messages, verbose=True)
    return make_openai_style_response(response, 50, 100)


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

    yield f"data: {make_openai_style_chunk(answer_id, is_first=True)}\n\n"
    for chunk in split_text(text):
        yield f"data: {make_openai_style_chunk(answer_id, text=chunk)}\n\n"
    yield f"data: {make_openai_style_chunk(answer_id, finish_reason='stop')}\n\n"
    final_chunk = make_openai_style_chunk(
        answer_id, 
        usage={
            "prompt_tokens": 11, 
            "completion_tokens": 14, 
            "total_tokens": 25, 
            "prompt_tokens_details": {
                "cached_tokens": 0, 
                "audio_tokens": 0
                }, 
            "completion_tokens_details": {
                "reasoning_tokens": 0, 
                "audio_tokens": 0, 
                "accepted_prediction_tokens": 0, 
                "rejected_prediction_tokens": 0}
                }
            )
    yield f"data: {final_chunk}\n\n"

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
