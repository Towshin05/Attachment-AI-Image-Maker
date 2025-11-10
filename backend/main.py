from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from schemas import ImageGenerationRequest, ImageGenerationResponse
from crud import ImageCRUD
from models import ImageGenerator
import os
from datetime import datetime

app = FastAPI(title="AI Image Maker API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
image_generator = ImageGenerator()
crud = ImageCRUD()

# Ensure generated_images folder exists
os.makedirs("generated_images", exist_ok=True)

# Serve generated images
app.mount("/images", StaticFiles(directory="generated_images"), name="images")

@app.get("/")
def read_root():
    return {"message": "AI Image Maker API is running"}

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    try:
        # Generate image
        filepath, filename = image_generator.generate_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            steps=request.steps
        )
        
        # Save to database
        image_id = crud.save_generation(
            request=request,
            image_path=filename,
            model_used=image_generator.model_id
        )
        
        return ImageGenerationResponse(
            image_id=image_id,
            image_path=f"/images/{filename}",  # frontend can use this URL directly
            prompt=request.prompt,
            generated_at=str(datetime.now())
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{image_id}")
async def delete_image(image_id: int):
    try:
        result = crud.delete_generation(image_id)
        if result:
            return {"message": "Image deleted successfully", "image_id": image_id}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: int, limit: int = 10):
    try:
        history = crud.get_user_history(user_id, limit)
        return [
            {
                "image_id": row[0],
                "prompt": row[1],
                "image_path": f"/images/{row[2]}",
                "generated_at": str(row[3]),
                "model_used": row[4]
            }
            for row in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/all-generations")
async def get_all_generations(limit: int = 20):
    try:
        generations = crud.get_all_generations(limit)
        return [
            {
                "image_id": row[0],
                "prompt": row[1],
                "image_path": f"/images/{row[2]}",
                "generated_at": str(row[3]),
                "username": row[4]
            }
            for row in generations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
