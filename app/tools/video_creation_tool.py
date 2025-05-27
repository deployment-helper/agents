from langchain.tools import tool, StructuredTool
from pydantic import BaseModel
from typing import List, Literal, Union
import logging

from app.services.video_http_client import VideoHttpClient
from app.models import MCQQuestion

logger = logging.getLogger(__name__)

# Step 1: Define a schema
class CreateVideoArgs(BaseModel):
    title: str
    desc: str
    thumbnail_text: str
    thumbnail_visual_desc: str
    video_type: Literal['message', 'mcq']
    raw: Union[List[str], List[MCQQuestion]]
    project_id: str # Add project_id field


def create_video(
    title: str,
    desc: str,
    thumbnail_text: str,
    thumbnail_visual_desc: str,
    video_type: Literal['message', 'mcq'],
    raw: Union[List[str], List[MCQQuestion]],
    project_id: str,
) -> str:
    """
    Create a video with the given title, description, and content.

    :param title: The title of the video.
    :param desc: The description of the video.
    :param thumbnail_text: The text to be displayed on the thumbnail.
    :param thumbnail_visual_desc: The visual description for the thumbnail.
    :param video_type: The type of video ('message' or 'mcq').
    :param raw: A list of quotes (for message type) or MCQList object (for mcq type).
    :param project_id: The ID of the project for video creation.
    :return: A string indicating success or failure.
    """
    # Here you would implement the actual video creation logic
    # For now, we'll just return a success message
    logger.info(f"Creating video with title: {title} for project: {project_id}")
    
    # Convert MCQQuestion objects to dictionaries for JSON serialization
    serializable_raw = raw
    if video_type == 'mcq' and raw and isinstance(raw[0], MCQQuestion):
        serializable_raw = [question.model_dump() for question in raw]
    
    resp = VideoHttpClient.create_video(
        title=title,
        desc=desc,
        thumbnail_text=thumbnail_text,
        thumbnail_visual_desc=thumbnail_visual_desc,
        raw=serializable_raw,
        project_id=project_id,
        video_type= video_type
    )
    
    
    return {
        "status": "success",
        "message": f"Video '{title}' created successfully",
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
