from app.services.api_calls import HttpClient
from app.config import api_config


class VideoHttpClient:
    @staticmethod
    def create_video(
        title: str,
        desc: str,
        thumbnail_text: str,
        thumbnail_visual_desc: str,
        quotes: list,
    ) -> dict:
        """
        Create a video using the video API.

        :param title: The title of the video.
        :param desc: The description of the video.
        :param thumbnail_text: The text to be displayed on the thumbnail.
        :param thumbnail_visual_desc: The visual description for the thumbnail.
        :param quotes: A list of quotes to include in the video.
        :return: A dictionary containing the API response.
        """
        client = HttpClient(api_config.base_url)
        payload = {
            "projectId": "rRKinclPppk9pZT9V44k",
            "projectName": "Quotes",
            "name": title,
            "description": desc,
            "sceneDescriptions": quotes,
            "properties": "",
            "audioLanguage": "en-US",
            "voiceCode": "en-US-Studio-Q",
            "backgroundMusic": "https://vm-presentations.s3.ap-south-1.amazonaws.com/public/background-music/uplifting-pad-texture-113842.mp3",
        }
        response = client.post(f"/videos/create-with-scenes?key={api_config.api_key}", payload)
        
        return {
            "video_id": response["id"],
            "video_url": f"https://example.com/video/{response['id']}",
        }
