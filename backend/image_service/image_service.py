from diffusers import StableDiffusionPipeline
import torch
import io
import base64
from fastapi import HTTPException
from transformers import CLIPProcessor, CLIPModel
from typing import List
from pydantic import BaseModel 

class Constraint(BaseModel):
    type: str
    value: str

class LogicalGroup(BaseModel):
    operator: str  # AND, OR, NOT
    constraints: List[Constraint]

# Check for GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the Stable Diffusion model
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,  # Use float16 for GPU
    use_safetensors=True
)
pipe = pipe.to(device)  # Move model to GPU or CPU
if device == "cuda":
    pipe.enable_attention_slicing()  # Optimize memory usage on GPU

# Load the CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def generate_prompt(logicalGroups: List[LogicalGroup]) -> str:
    """
    Generate a detailed text prompt based on the constraints.
    """
    prompt = "A high-quality, realistic image of "
    for group in logicalGroups:
        for constraint in group.constraints:
            if constraint.type == "object_inclusion":
                if group.operator == "NOT":
                    continue
                else:
                    prompt += f"a {constraint.value}, "
            elif constraint.type == "color_inclusion":
                if group.operator == "NOT":
                    continue
                else:
                    prompt += f"with a {constraint.value} color, "
    prompt += "and a peaceful, vibrant atmosphere."
    return prompt

def generate_image(prompt: str):
    """
    Use Stable Diffusion to generate an image based on the prompt.
    """
    image = pipe(
        prompt,
        num_inference_steps=140 if device == "cuda" else 50,  # More steps for GPU
        guidance_scale=12 if device == "cuda" else 7.5,  # Stronger guidance for GPU
    ).images[0]
    return image

def validate_image(image, logicalGroups: List[LogicalGroup]) -> bool:
    """
    Validate if the generated image meets the constraints using CLIP.
    """
    text_descriptions = []
    for group in logicalGroups:
        for constraint in group.constraints:
            if constraint.type == "object_inclusion":
                if group.operator == "NOT":
                    text_descriptions.append(f"a photo without {constraint.value}")
                else:
                    text_descriptions.append(f"a photo of {constraint.value}")

    if not text_descriptions:
        return True

    inputs = processor(text=text_descriptions, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)

    for prob in probs[0]:
        if prob > 0.5:
            return True
    return False

def generate_valid_image(logicalGroups: List[LogicalGroup]):
    """
    Generate and validate an image based on the given constraints.
    """
    prompt = generate_prompt(logicalGroups)
    print("Generated Prompt:", prompt)

    max_attempts = 5 if device == "cuda" else 3  # More attempts on GPU
    for attempt in range(max_attempts):
        image = generate_image(prompt)
        if validate_image(image, logicalGroups):
            print(logicalGroups)
            print("Image validation successful.")
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return image_base64
        else:
            print(f"Image validation failed. Regenerating (attempt {attempt + 1}/{max_attempts})...")
    
    raise HTTPException(status_code=400, detail="Failed to generate a valid image after multiple attempts.")