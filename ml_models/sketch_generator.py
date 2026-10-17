import os  
from huggingface_hub import InferenceClient  
import base64  
import io  
from dotenv import load_dotenv  

# Load environment variables  
load_dotenv()  

class SketchGenerator:  
    def __init__(self,   
                 model_name='CompVis/stable-diffusion-v1-4',   
                 access_token=None):  
        """  
        Initialize Hugging Face Inference Client  
        """  
        try:  
            # Use environment variable or passed token  
            self.access_token = access_token or os.getenv('HF_ACCESS_TOKEN')  
            
            # Initialize Inference Client  
            self.client = InferenceClient(  
                model=model_name,  
                token=self.access_token  
            )  
        except Exception as e:  
            print(f"Error initializing Inference Client: {e}")  
            self.client = None  

    def generate_sketch(self, prompt, negative_prompt=None, num_images=1):  
        """  
        Generate image based on prompt using Hugging Face Inference  
        """  
        if not self.client:  
            raise ValueError("Inference Client not initialized")  

        try:  
            # Construct full prompt with optional negative prompting  
            full_prompt = prompt  
            if negative_prompt:  
                full_prompt += f" --neg {negative_prompt}"  

            # Generate images  
            images = []  
            for _ in range(num_images):  
                image = self.client.text_to_image(prompt)  
                
                # Convert image to base64  
                buffered = io.BytesIO()  
                image.save(buffered, format="PNG")  
                img_str = base64.b64encode(buffered.getvalue()).decode()  
                
                images.append({  
                    "image": img_str,  
                    "prompt": prompt  
                })  

            # Return single image or list based on num_images  
            return images[0] if num_images == 1 else images  

        except Exception as e:  
            print(f"Image generation error: {e}")  
            return None  

# Singleton instance with token from environment  
sketch_generator = SketchGenerator()