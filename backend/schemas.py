from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    width: Optional[int] = 512
    height: Optional[int] = 512
    steps: Optional[int] = 50
    user_id: Optional[int] = 1

class ImageGenerationResponse(BaseModel):
    image_id: int
    image_path: str
    prompt: str
    generated_at: str

class ImageHistory(BaseModel):
    image_id: int
    prompt: str
    image_path: str
    generated_at: datetime
    username: str