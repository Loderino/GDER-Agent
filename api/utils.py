import json
import time
import uuid


def make_openai_style_response(
    message: str, prompt_tokens: int, completion_tokens: int
) -> dict:
    """
    Makes OpenAi style response format.

    Args:
        message (str): response from llm.
        prompt_tokens (int): tokens number in prompt.
        completion_tokens (int): tokens_number in message.

    Returns:
        dict: dict with data in OpenAI response style format.
    """
    return {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "GDER-agent",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": message,
                    "refusal": None,
                    "annotations": [],
                },
                "logprob": None,
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
            "completion_tokens_details": {
                "reasoning_tokens": 0,
                "audio_tokens": 0,
                "accepted_prediction_tokens": 0,
                "rejected_prediction_tokens": 0,
            },
        },
    }


def make_openai_style_chunk(
    answer_id: str,
    text: str = "",
    usage: dict = None,
    is_first: bool = False,
    finish_reason: str = None,
) -> str:
    """
    Makes OpenAI style response chunk.

    Args:
        answer_id (str): value for `id` field in chunk body.
        text (str, optional): text chunk of llm response. Defaults to ''.
        usage (dict, optional): usage info for last chunk. Defaults to None. Else text parameter will be ignored.
        is_first (bool, optional): flag for first chunk, that differs from other. Defaults to False.
        finish_reason (str, optional): value for `finish reason` field in chunk body. Defaults to None. Else text parameter will be ignored.

    Returns:
        str: JSON string in OpenAI response chunk style format.
    """
    base_chunk = {
        "id": answer_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "GDER-agent",
        "service_tier": "default",
        "system_fingerprint": None,
        "choices": [
            {
                "index": 0,
                "delta": {"content": ""},
                "logprobs": None,
                "finish_reason": None,
            }
        ],
        "usage": None,
    }

    if is_first:
        base_chunk["choices"][0]["delta"]["role"] = "assistant"
        base_chunk["choices"][0]["delta"]["refusal"] = None
        return json.dumps(base_chunk)

    if finish_reason:
        base_chunk["choices"][0]["finish_reason"] = finish_reason
        base_chunk["choices"][0]["delta"] = {}
        return json.dumps(base_chunk)

    if usage:
        base_chunk["choices"] = []
        base_chunk["usage"] = usage
        return json.dumps(base_chunk)

    base_chunk["choices"][0]["delta"]["content"] = text
    return json.dumps(base_chunk, ensure_ascii=False)
