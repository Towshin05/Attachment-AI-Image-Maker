# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from schemas import ImageGenerationRequest, ImageGenerationResponse
# from crud import ImageCRUD
# from models import ImageGenerator
# import os
# from datetime import datetime

# app = FastAPI(title="AI Image Maker API")

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Initialize components
# image_generator = ImageGenerator()
# crud = ImageCRUD()

# # Ensure generated_images folder exists
# os.makedirs("generated_images", exist_ok=True)

# # Serve generated images
# app.mount("/images", StaticFiles(directory="generated_images"), name="images")

# @app.get("/")
# def read_root():
#     return {"message": "AI Image Maker API is running"}

# @app.post("/generate", response_model=ImageGenerationResponse)
# async def generate_image(request: ImageGenerationRequest):
#     try:
#         # Generate image
#         filepath, filename = image_generator.generate_image(
#             prompt=request.prompt,
#             negative_prompt=request.negative_prompt,
#             width=request.width,
#             height=request.height,
#             steps=request.steps
#         )
        
#         # Save to database
#         image_id = crud.save_generation(
#             request=request,
#             image_path=filename,
#             model_used=image_generator.model_id
#         )
        
#         return ImageGenerationResponse(
#             image_id=image_id,
#             image_path=f"/images/{filename}",  # frontend can use this URL directly
#             prompt=request.prompt,
#             generated_at=str(datetime.now())
#         )
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.delete("/delete/{image_id}")
# async def delete_image(image_id: int):
#     try:
#         result = crud.delete_generation(image_id)
#         if result:
#             return {"message": "Image deleted successfully", "image_id": image_id}
#         else:
#             raise HTTPException(status_code=404, detail="Image not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/history/{user_id}")
# async def get_history(user_id: int, limit: int = 10):
#     try:
#         history = crud.get_user_history(user_id, limit)
#         return [
#             {
#                 "image_id": row[0],
#                 "prompt": row[1],
#                 "image_path": f"/images/{row[2]}",
#                 "generated_at": str(row[3]),
#                 "model_used": row[4]
#             }
#             for row in history
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/all-generations")
# async def get_all_generations(limit: int = 20):
#     try:
#         generations = crud.get_all_generations(limit)
#         return [
#             {
#                 "image_id": row[0],
#                 "prompt": row[1],
#                 "image_path": f"/images/{row[2]}",
#                 "generated_at": str(row[3]),
#                 "username": row[4]
#             }
#             for row in generations
#         ]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)





from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from schemas import ImageGenerationRequest, ImageGenerationResponse
from crud import ImageCRUD
from models import ImageGenerator
import os
from datetime import datetime
import PyPDF2
from typing import Optional

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

# Ensure folders exist
os.makedirs("generated_images", exist_ok=True)
os.makedirs("uploaded_scripts", exist_ok=True)

# Serve generated images
app.mount("/images", StaticFiles(directory="generated_images"), name="images")

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        import io
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "AI Image Maker API is running"}

@app.post("/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """Generate image from text prompt"""
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
            image_path=f"/images/{filename}",
            prompt=request.prompt,
            generated_at=str(datetime.now())
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-from-pdf", response_model=ImageGenerationResponse)
async def generate_from_pdf(
    file: UploadFile = File(...),
    negative_prompt: Optional[str] = Form(""),
    width: Optional[int] = Form(512),
    height: Optional[int] = Form(512),
    steps: Optional[int] = Form(50),
    user_id: Optional[int] = Form(1)
):
    """Generate image from PDF script"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read PDF content
        content = await file.read()
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(content)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Limit prompt length (Stable Diffusion has token limits)
        max_chars = 1000
        prompt = extracted_text[:max_chars] if len(extracted_text) > max_chars else extracted_text
        
        # Save uploaded PDF for reference
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"script_{timestamp}_{file.filename}"
        pdf_path = os.path.join("uploaded_scripts", pdf_filename)
        with open(pdf_path, "wb") as f:
            f.write(content)
        
        # Generate image
        filepath, filename = image_generator.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps
        )
        
        # Create request object for database
        request = ImageGenerationRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            user_id=user_id
        )
        
        # Save to database
        image_id = crud.save_generation(
            request=request,
            image_path=filename,
            model_used=image_generator.model_id
        )
        
        return ImageGenerationResponse(
            image_id=image_id,
            image_path=f"/images/{filename}",
            prompt=f"[From PDF: {file.filename}] {prompt[:100]}...",
            generated_at=str(datetime.now())
        )
    
    except HTTPException:
        raise
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