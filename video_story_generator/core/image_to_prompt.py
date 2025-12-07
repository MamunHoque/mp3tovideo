"""
Image-to-prompt module using AI vision models.
Converts images to text descriptions for video generation.
"""

import base64
from typing import Optional, List, Dict
from pathlib import Path
import os


class ImageToPrompt:
    """Handles image-to-text conversion using AI vision models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini"):
        """
        Initialize image-to-prompt converter.
        
        Args:
            api_key: API key for the vision model
            model: Model to use ("gemini", "openai", "blip")
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        # Initialize appropriate client
        if model == "gemini":
            self._init_gemini()
        elif model == "openai":
            self._init_openai()
        elif model == "blip":
            self._init_blip()
    
    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-pro-vision')
        except ImportError:
            print("google-generativeai not installed. Install with: pip install google-generativeai")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            print("openai not installed. Install with: pip install openai")
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
    
    def _init_blip(self):
        """Initialize BLIP local model."""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
            self.client = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.client = self.client.to("cuda")
        except ImportError:
            print("transformers not installed. Install with: pip install transformers torch")
        except Exception as e:
            print(f"Error initializing BLIP: {e}")
    
    def generate_prompt(
        self,
        image_path: str,
        context: Optional[str] = None,
        style: str = "cinematic"
    ) -> Optional[str]:
        """
        Generate text prompt from image.
        
        Args:
            image_path: Path to image file
            context: Optional context for prompt generation
            style: Style hint for prompt ("cinematic", "realistic", "artistic")
            
        Returns:
            Generated text prompt or None if failed
        """
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
        
        try:
            if self.model == "gemini":
                return self._generate_with_gemini(image_path, context, style)
            elif self.model == "openai":
                return self._generate_with_openai(image_path, context, style)
            elif self.model == "blip":
                return self._generate_with_blip(image_path, context, style)
            else:
                print(f"Unknown model: {self.model}")
                return None
        except Exception as e:
            print(f"Error generating prompt: {e}")
            return None
    
    def _generate_with_gemini(
        self,
        image_path: str,
        context: Optional[str],
        style: str
    ) -> Optional[str]:
        """Generate prompt using Google Gemini."""
        if not self.client:
            return None
        
        try:
            from PIL import Image
            import google.generativeai as genai
            
            # Load image
            img = Image.open(image_path)
            
            # Create prompt
            system_prompt = f"Describe this image in detail for video generation. Focus on {style} elements."
            if context:
                system_prompt += f" Context: {context}"
            
            # Generate description
            response = self.client.generate_content([system_prompt, img])
            return response.text
            
        except Exception as e:
            print(f"Error with Gemini: {e}")
            return None
    
    def _generate_with_openai(
        self,
        image_path: str,
        context: Optional[str],
        style: str
    ) -> Optional[str]:
        """Generate prompt using OpenAI GPT-4 Vision."""
        if not self.client:
            return None
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt
            system_prompt = f"Describe this image in detail for video generation. Focus on {style} elements."
            if context:
                system_prompt += f" Context: {context}"
            
            # Generate description
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": system_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error with OpenAI: {e}")
            return None
    
    def _generate_with_blip(
        self,
        image_path: str,
        context: Optional[str],
        style: str
    ) -> Optional[str]:
        """Generate prompt using BLIP local model."""
        if not self.client:
            return None
        
        try:
            from PIL import Image
            import torch
            
            # Load image
            raw_image = Image.open(image_path).convert('RGB')
            
            # Create prompt
            text = f"a {style} scene of"
            if context:
                text = f"{context}, {text}"
            
            # Process image
            inputs = self.processor(raw_image, text, return_tensors="pt")
            
            # Move to GPU if available
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate caption
            out = self.client.generate(**inputs, max_length=100)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            print(f"Error with BLIP: {e}")
            return None
    
    def batch_generate_prompts(
        self,
        image_paths: List[str],
        context: Optional[str] = None,
        style: str = "cinematic"
    ) -> List[Optional[str]]:
        """
        Generate prompts for multiple images.
        
        Args:
            image_paths: List of image file paths
            context: Optional context for prompt generation
            style: Style hint for prompts
            
        Returns:
            List of generated prompts (None for failed images)
        """
        prompts = []
        for image_path in image_paths:
            prompt = self.generate_prompt(image_path, context, style)
            prompts.append(prompt)
        return prompts
    
    def enhance_prompt(
        self,
        base_prompt: str,
        style: str = "cinematic",
        duration: int = 5
    ) -> str:
        """
        Enhance a basic prompt with style and technical details.
        
        Args:
            base_prompt: Basic description
            style: Style to apply
            duration: Video duration in seconds
            
        Returns:
            Enhanced prompt
        """
        style_modifiers = {
            "cinematic": "cinematic lighting, dramatic composition, film grain, 4K quality",
            "realistic": "photorealistic, natural lighting, high detail, sharp focus",
            "artistic": "artistic style, creative composition, vibrant colors, stylized",
            "anime": "anime style, vibrant colors, detailed animation, studio quality",
            "documentary": "documentary style, natural setting, authentic, real-world"
        }
        
        modifier = style_modifiers.get(style, style_modifiers["cinematic"])
        enhanced = f"{base_prompt}, {modifier}, {duration} seconds"
        
        return enhanced
