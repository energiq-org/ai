from fastapi import FastAPI
from pydantic import BaseModel

from chat_bot import chat_bot

app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat_endpoint(chat: ChatRequest):
    user_id = chat.user_id
    user_input = chat.message

    response = chat_bot(user_id, user_input)
    return {"reply": response}