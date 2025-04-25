from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from STT_service import speech_to_text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return {"transcription": speech_to_text(contents)}
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)