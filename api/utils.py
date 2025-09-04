import json
import uuid
import time

def make_openai_style_response(message, prompt_tokens, completion_tokens):
    return json.dumps({
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "GDER-agent",
        "choices": [
                {
                    "index":0,
                    "message":{
                        "role":"assistant",
                        "content": message,
                        "refusal": None,
                        "annotations":[]
                    },
                    "logprob":None,
                    "finish_reason":"stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens+completion_tokens,
                "prompt_tokens_details": {"cached_tokens": 0, "audio_tokens": 0},
                "completion_tokens_details": {
                    "reasoning_tokens": 0, 
                    "audio_tokens": 0, 
                    "accepted_prediction_tokens": 0, 
                    "rejected_prediction_tokens": 0
                }
            }
        })

def make_openai_style_chunk(answer_id, text='', usage=None, is_first=False, finish_reason=None):
    base_chunk = {
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
                    "content":""
                },
                "logprobs":None,
                "finish_reason":None
            }
        ],
        "usage":None
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
    return json.dumps(base_chunk)


    