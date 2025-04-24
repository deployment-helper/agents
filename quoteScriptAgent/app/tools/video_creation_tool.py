from langchain.tools import tool, StructuredTool
from pydantic import BaseModel
from typing import List

from app.services.video_http_client import VideoHttpClient


# Step 1: Define a schema
class CreateVideoArgs(BaseModel):
    title: str
    desc: str
    thumbnail_text: str
    thumbnail_visual_desc: str
    quotes: List[str]
    project_id: str # Add project_id field


def create_video(
    title: str,
    desc: str,
    thumbnail_text: str,
    thumbnail_visual_desc: str,
    quotes: List[str],
    project_id: str, # Add project_id parameter
) -> str:
    """
    Create a video with the given title, description, and quotes.

    :param title: The title of the video.
    :param desc: The description of the video.
    :param thumbnail_text: The text to be displayed on the thumbnail.
    :param
    thumbnail_visual_desc: The visual description for the thumbnail.
    :param quotes: A list of quotes to include in the video.
    :param project_id: The ID of the project for video creation.
    :return: A string indicating success or failure.
    """
    # Here you would implement the actual video creation logic
    # For now, we'll just return a success message
    print(f"Creating video with title: {title} for project: {project_id}")
    resp = VideoHttpClient.create_video(
        title=title,
        desc=desc,
        thumbnail_text=thumbnail_text,
        thumbnail_visual_desc=thumbnail_visual_desc,
        quotes=quotes,
        project_id=project_id, # Pass project_id
    )
    return {
        "status": "success",
        "message": f"Video '{title}' created successfully with {len(quotes)} quotes.",
        "video_id": resp["video_id"],
        "video_url": resp["video_url"]
    }


create_video_tool = StructuredTool.from_function(
    func=create_video,
    name="create_video",
    description="Create a video with the given title, description, and quotes.",
    args_schema=CreateVideoArgs,
    return_type=str,
)
