from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from llama_cpp import Llama
import os

app = FastAPI()

MODEL_PATH = "models/nous-hermes-llama-2-7b-q4_k_m.gguf"

try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=4
    )
except Exception as e:
    print(f"Ошибка при загрузке модели: {e}")
    llm = None

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatCompletionResponse(BaseModel):
    id: str = "chatcmpl-123"
    object: str = "chat.completion"
    created: int = 1677858242
    model: str
    choices: List[dict]
    usage: dict

@app.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    if llm is None:
        raise HTTPException(status_code=500, detail="Модель не загружена")

    # Добавляем системную инструкцию
    system_prompt = "Ты — умный искусственный интеллект, который всегда отвечает на русском языке."
    
    # Формируем полный промпт
    prompt = f"system: {system_prompt}\n"
    for message in request.messages:
        prompt += f"{message.role}: {message.content}\n"
    prompt += "assistant: "

    response = llm(
        prompt,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        stop=["user:", "system:", "assistant:"]
    )

    result = response["choices"][0]["text"].strip()

    return ChatCompletionResponse(
        model=request.model,
        choices=[{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": result
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(result.split()),
            "total_tokens": len(prompt.split()) + len(result.split())
        }
    )

@app.get("/v1/models")
def get_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "nous-hermes-llama-2-7b",
                "object": "model",
                "owned_by": "user"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
