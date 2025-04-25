from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from image_service import generate_valid_image,LogicalGroup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateImageRequest(BaseModel):
    logicalGroups: List[LogicalGroup]

@app.post("/generate_image/")
async def generate_image_endpoint(request: GenerateImageRequest):
    try:
        image_base64 = generate_valid_image(request.logicalGroups)
        return {"image": image_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)