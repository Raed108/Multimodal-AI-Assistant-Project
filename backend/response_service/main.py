from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from llm_service import generate_valid_response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Constraint(BaseModel):
    type: str
    value: str

class LogicalGroup(BaseModel):
    operator: str  # AND, OR, NOT
    constraints: List[Constraint]

class RequestPayload(BaseModel):
    question: str
    logicalGroups: List[LogicalGroup]

@app.post("/generate_response/")
async def generate_response(payload: RequestPayload):
    try:
        valid_response = generate_valid_response(payload.question, payload.logicalGroups)
        return {"response": valid_response} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)