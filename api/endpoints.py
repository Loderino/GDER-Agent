import json
import uuid
from typing import Generator
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agent.agent import Agent
from api.utils import make_openai_style_chunk, make_openai_style_response


router = APIRouter(prefix="/v1")
agent=Agent()

@router.get("/models")
async def list_models():
    """
    Get available models information.
    """
    return JSONResponse(
        {
            "object": "list", 
            "data":[
                {
                    "id":"GDER-agent",
                    "created":1677610602,
                    "owned_by":"Loderino"
                }
            ]
        }
    )

async def chat_completion(messages: list[BaseMessage]) -> str:
    """
        Handles requests from user client.

        Args:
            messages (list[BaseMessage]): chat history.
        
        Returns:
            str: JSON string in OpenAI response style format. 
    """
    user_message = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
    if "### Task:\n" in user_message:
        follow_ups = {
            "follow_ups": [
                "Какие файлы можно открыть?",
                "Что находится в ячейке A1?",
                "Какая информация есть в открытом файле?"
            ]
        }
        return JSONResponse(make_openai_style_response(json.dumps(follow_ups), 50, 100))

    langchain_messages = []
    for msg in messages:
        if msg.get("role") == "user":
            langchain_messages.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "assistant":
            langchain_messages.append(AIMessage(content=msg.get("content", "")))

    response = await agent.communicate(1, langchain_messages, verbose=True)
    return JSONResponse(make_openai_style_response(response, 50, 100))


def split_text(text: str, chunk_size: int = 8) -> Generator[str, None, None]:
    """
    Splits text to chunks.

    Args:
        text (str): text to split.
        chunk_size (int): symbols per chunk. Defaults to 8.

    Yields:
        str: chunk stream.
    """
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]


def stream_imitation(text: str) -> Generator[str, None, None]:
    """
    Imitate of stream mode answer.

    Args:
        text (str): text to split to chunks.

    Yields:
        Generator[str]: chunk text to send as stream in OpenAI style format.
    """
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

async def chat_completion_stream(messages: list[BaseMessage]) -> StreamingResponse:
    """
        Handles requests with stream mode from user client.

        Args:
            messages (list[BaseMessage]): chat history.
        
        Returns:
            str: JSON string in OpenAI response style format 
    """
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
    """
    Chat completion endpoint.
    """
    try:
        data = await request.json()
        messages = data.get("messages", [])
        if data["stream"]:
            return await chat_completion_stream(messages)
        return await chat_completion(messages)
    except Exception as exc:
        print(f"Error: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
