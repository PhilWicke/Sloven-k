import os
from google import genai
from google.genai import types


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY environment variable")
    return genai.Client(api_key=api_key)


def generate_image(client: genai.Client, prompt: str) -> bytes:
    """Generate an image using Gemini's image generation and return PNG bytes."""
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1),
    )
    return response.generated_images[0].image.image_bytes


def generate_text(client: genai.Client, prompt: str) -> str:
    """Generate text using Gemini and return the response."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text
