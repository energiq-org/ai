import whisper

whisper_model = whisper.load_model("small")

def stt(filepath: str) -> str:
    response = whisper_model.transcribe(filepath, fp16=False)
    return response["text"]


if __name__ == "__main__":
    print(stt("input.wav"))