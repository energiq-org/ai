from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile
import io
import os
from chat_bot import chat_bot
from voice_chat import stt, tts

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

@app.post("/chat")
def chat_endpoint(chat: ChatRequest):
    user_id = chat.user_id
    user_input = chat.message
    context = chat.context
    
    response = chat_bot(user_id, user_input, context)
    return {"reply": response}

@app.post("/voice")
async def voice_endpoint(
    user_id: str = Form(),
    voice_input: UploadFile = File(),
    output_voice_type: str = Form(default="alloy"),  # voices = [alloy, echo, fable, onyx, nova, shimmer]
    context: Optional[Dict[str, Any]] = None
):
    file = voice_input
    ext = ".wav"
    
    if not file.filename.endswith(ext):
        return {"error": f"Only {ext} files are supported"}
    
    # Convert from speech to text
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        
        transcription = stt(tmp_path)
        
        # Clean up the temporary file
        os.unlink(tmp_path)
        
    except Exception as e:
        return {"error": str(e)}
    
    # Get the response 
    response = chat_bot(user_id, transcription, context)
    
    # Convert the response to voice
    try:
        audio_data = tts(response, output_voice_type, True)
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}
