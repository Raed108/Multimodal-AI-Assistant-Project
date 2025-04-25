from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from TTS_service import text_to_speech
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextToSpeechRequest(BaseModel):
    text: str
    maleSpeaker: bool

# @app.post("/api/text-to-speech/")
# def text_to_speech_api(request: TextToSpeechRequest):
#     try:
#         audio_bytes = text_to_speech(request.text, request.maleSpeaker)
#         # Return audio as base64 for frontend playback
#         audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
#         return {"audio": audio_base64}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text-to-speech/")
async def text_to_speech_api(request: TextToSpeechRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty.")
        audio_bytes = text_to_speech(request.text, request.maleSpeaker)
        # Return audio as base64 for frontend playback
        audio_base64= base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)