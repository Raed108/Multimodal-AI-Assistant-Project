from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from response_service.llm_service import generate_valid_response
from image_service.image_service import generate_valid_image, LogicalGroup
from stt_service.STT_service import speech_to_text
from tts_service.TTS_service import text_to_speech
from llm_service2 import generate_valid_response as generate_valid_response2
from convertToKG import extract_knowledge_graph
from fastapi import FastAPI, File, UploadFile
import base64


app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestPayload(BaseModel):
    question: str
    logicalGroups: List[LogicalGroup]

class GenerateImageRequest(BaseModel):
    logicalGroups: List[LogicalGroup]

class TextToSpeechRequest(BaseModel):
    text: str
    maleSpeaker: bool  
    
class ResponseInput(BaseModel):
    response: str


@app.post("/generate_response/")
async def generate_response(payload: RequestPayload):
    try:
        valid_response = generate_valid_response(payload.question, payload.logicalGroups)
        return {"response": valid_response["response"], "iterationCount": valid_response["iterationCount"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_image/")
async def generate_image_endpoint(request: GenerateImageRequest):
    try:
        image_base64 = generate_valid_image(request.logicalGroups)
        return {"image": image_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return {"transcription": speech_to_text(contents)}
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text-to-speech/")
def text_to_speech_api(request: TextToSpeechRequest):
    try:
        audio_bytes = text_to_speech(request.text, request.maleSpeaker)
        # Return audio as base64 for frontend playback
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/generate_valid_response/")
async def generate_valid_response_endpoint(request: RequestPayload):
    try:
        result = generate_valid_response2(
            question=request.question,
            logicalGroups=request.logicalGroups
        )
        return {
            "response_A": result["response_A"],
            "response_B": result["response_B"],
            "analysis_B_of_A": result["analysis_B_of_A"],
            "analysis_A_of_B": result["analysis_A_of_B"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@app.post("/api/generate-knowledge-graph")
async def generate_knowledge_graph(input: ResponseInput):
    """
    Generate a knowledge graph from the given response text.
    Returns a list of triples [entity1, relation, entity2].
    """
    try:
        triples = extract_knowledge_graph(input.response)
        return {"triples": triples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating knowledge graph: {str(e)}")
    

