import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os
from datetime import datetime

class ImageGenerator:
    def __init__(self):
        self.model_id = "runwayml/stable-diffusion-v1-5"  # Lightweight model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load model
        print("Loading AI model... This may take a few minutes on first run.")
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None,  # Disable for faster inference
        )
        
        # Use faster scheduler
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )
        
        self.pipe = self.pipe.to(self.device)
        
        # Enable memory optimizations for CPU
        if self.device == "cpu":
            self.pipe.enable_attention_slicing()
        
        print("Model loaded successfully!")
        
        # Create output directory
        self.output_dir = "generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      width: int = 512, height: int = 512, steps: int = 50):
        try:
            print(f"Generating image for prompt: {prompt[:50]}...")
            
            # Generate image
            image = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=7.5
            ).images[0]
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"img_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath)
            
            print(f"Image generated successfully: {filename}")
            return filepath, filename
        
        except Exception as e:
            print(f"Image generation error: {e}")
            raise