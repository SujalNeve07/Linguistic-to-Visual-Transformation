import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TOGETHER_API_URL = "https://api.together.xyz/v1/images/generations"


class SketchGenerator:
    def __init__(self):
        self.api_key = os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment")

        # Stable Diffusion image model
        self.model_name = "stabilityai/stable-diffusion-xl-base-1.0"

        self.system_prompt = (
            "A realistic hand-drawn forensic pencil sketch, portrait only, "
            "neutral background, grayscale, detailed facial features. "
        )

    def generate_sketch(self, prompt):
        full_prompt = self.system_prompt + prompt

        logger.info(f"Generating sketch for prompt: {prompt}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "width": 512,
            "height": 512,
            "steps": 30,
            "n": 3
        }

        response = requests.post(
            TOGETHER_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        logger.info(f"Together raw response keys: {data['data'][0].keys()}")

        images = []
        for img in data["data"]:
             if "b64_json" in img:
                 images.append({
                      "type": "base64",
                      "image_base64": img["b64_json"]
                      })
             elif "url" in img:
                 images.append({
                      "type": "url",
                      "image_url": img["url"]
                      })
        return images

# Singleton instance
sketch_generator = SketchGenerator()    