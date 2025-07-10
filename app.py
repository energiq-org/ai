from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile
import io

from chat_bot import chat_bot
from voice_chat import stt, tts

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


class VoiceRequest(BaseModel):
    user_id: str
    voice_input: UploadFile
    output_voice_type: str = "alloy" # voices = [alloy, echo, fable, onyx, nova, shimmer]
    
@app.post("/voice")
async def voice_endpoint(voice: VoiceRequest):
    user_id = voice.user_id
    file = voice.voice_input
    output_voice_type = voice.output_voice_type
    ext = ".wav"
    
    if not file.filename.endswith(ext):
        return {"error": f"Only {ext} files are supported"}
    
    # Convert from speech to text
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        transcription = stt(tmp_path)
    except Exception as e:
        return {"error": str(e)}
    
    # Get the response 
    response = chat_bot(user_id, transcription)
    
    # Convert the response to voice
    try:
        audio_data = tts(response, output_voice_type, True)
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}