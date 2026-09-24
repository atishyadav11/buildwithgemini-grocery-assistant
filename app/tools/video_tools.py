# app/tools/video_tools.py
"""Video generation function tools for the Grocery Assistant agent."""

import base64
import uuid

from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import client, types

PROJECT_ID = "qwiklabs-gcp-01-8566d63f79b1"
BUCKET_NAME = "grocery-assistant-images-qwiklabs-gcp-01-8566d63f79b1"


def generate_item_video(item_description: str, tool_context: ToolContext = None) -> str:
    """Generate a short video preview for a grocery item, recipe, or meal prep demo using Google Omni model.

    Args:
        item_description: Detailed description of the item or dish to generate a video for (e.g. 'Fresh organic strawberries being washed').
        tool_context: ADK ToolContext provided automatically by the agent framework.

    Returns:
        Public HTTPS URL of the generated video stored in Cloud Storage.
    """
    try:
        # 1. Initialize Vertex AI client in global location for gemini-omni-flash-preview
        ai_client = client.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        prompt = (
            f"A short video demonstrating {item_description.strip()}, "
            "vibrant, professional food cinematography, high quality"
        )

        response = ai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        # Extract video bytes and mime type from response
        output_video = getattr(response, "output_video", None)
        if output_video:
            if getattr(output_video, "mime_type", None):
                mime_type = output_video.mime_type
            if getattr(output_video, "data", None):
                raw_data = output_video.data
                if isinstance(raw_data, bytes):
                    video_bytes = raw_data
                elif isinstance(raw_data, str):
                    video_bytes = base64.b64decode(raw_data)

        if not video_bytes and getattr(response, "outputs", None):
            for out in response.outputs:
                raw_data = getattr(out, "data", None)
                if raw_data:
                    if isinstance(raw_data, bytes):
                        video_bytes = raw_data
                    elif isinstance(raw_data, str):
                        video_bytes = base64.b64decode(raw_data)
                    if getattr(out, "mime_type", None):
                        mime_type = out.mime_type
                    break

        if not video_bytes:
            return f"Failed to generate video for '{item_description}': No video bytes returned from model."

        ext = "mp4"
        if "webm" in mime_type:
            ext = "webm"
        filename = f"video_{uuid.uuid4().hex[:8]}.{ext}"

        # Action (1): Save video bytes with tool_context.save_artifact for Playground Artifacts panel
        if tool_context and hasattr(tool_context, "save_artifact"):
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # Action (2): Upload video bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return (
            f"Successfully generated video for '{item_description}'.\n"
            f"Public Video URL: {public_url}"
        )

    except Exception as e:
        return f"Video generation error: {str(e)}"
