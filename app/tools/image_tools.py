# app/tools/image_tools.py
"""Image generation function tools for the Grocery Assistant agent."""

import uuid

from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import client, types

PROJECT_ID = "qwiklabs-gcp-01-8566d63f79b1"
BUCKET_NAME = "grocery-assistant-images-qwiklabs-gcp-01-8566d63f79b1"


def generate_item_image(item_description: str, tool_context: ToolContext = None) -> str:
    """Generate a high-quality product or dish image for a grocery item, recipe, or meal kit.

    Args:
        item_description: Detailed description of the grocery item or dish to generate an image for (e.g. 'A bowl of fresh organic Gala apples').
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        Public HTTPS URL of the generated image stored in Cloud Storage.
    """
    try:
        # 1. Initialize Vertex AI client in global location
        ai_client = client.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        prompt = (
            f"A professional studio food photograph of {item_description.strip()}, "
            "vibrant, appetizing, commercial product style, high quality"
        )

        response = ai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    if part.inline_data.mime_type:
                        mime_type = part.inline_data.mime_type
                    break

        if not image_bytes:
            return f"Failed to generate image for '{item_description}': No image bytes returned."

        filename = f"item_{uuid.uuid4().hex[:8]}.jpg"

        # 2. Action (1): Save with tool_context.save_artifact for Playground Artifacts panel
        if tool_context:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 3. Action (2): Upload image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return (
            f"Successfully generated image for '{item_description}'.\n"
            f"Public Image URL: {public_url}"
        )

    except Exception as e:
        return f"Image generation error: {str(e)}"
