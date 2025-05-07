from langchain_core.prompts import ChatPromptTemplate

class Prompts:
    """
    This class contains the prompts used in the application.
    """

    @staticmethod
    def get_prompt(prompt_name: str) -> str:
        """
        Returns the prompt based on the prompt name.
        """
        prompts = {
            "greeting": "Hello! How can I assist you today?",
            "farewell": "Goodbye! Have a great day!",
            "help": "Here are some commands you can use: ...",
        }

        return prompts.get(prompt_name, "Prompt not found.")

    @staticmethod
    def create_titles_thumbnails_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            [
                (
                    "system",
                    "you are expert youtube content creator specialized in creating quotes types of video data like, Generating good list of title and thumbnail text for given topics.",
                ),
                (
                    "user",
                    "create list of titles and a list of thumbnail texts for this  {topic}. each list should contains 10 items.",
                ),
            ]
        )

    @staticmethod
    def find_best_title_thumbnail_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            [
                (
                    "system",
                    "you are expert youtube content creator specialized in creating quotes types of video data like, selecting best title and thumbnail text for given list of titles and thumbnail texts for this {topic}.",
                ),
                (
                    "user",
                    "select best title and thumbnail text from given list of titles and thumbnail texts. \n\n **Title List:** {titles} \n\n **Thumbnail Text List:** {thumbnail_text_list}",
                ),
            ]
        )

    @staticmethod
    def create_quotes_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            [
                (
                    "system",
                    "you are expert youtube content creator specialized in creating quotes types of video data like, generating good list of quotes for given title and thumbnail text for this {topic}.",
                ),
                (
                    "user",
                    "create a list of 40-50 quotes for this **Title:** {best_title} and **Thumbnail_text:** {best_thumbnail_text}.",
                ),
            ]
        )

    @staticmethod
    def create_thumbnail_visual_desc_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            [
                (
                    "system",
                    "you are an expert midjourney prompt creator specialized in creating youtube thumbnails images with small and concise prompts. Use oil painting style  and black, red, yellow, white colors scheme",
                ),
                (
                    "user",                    
                    "create a image description for youtube thumbnail image for title {best_title} and a place in image to write thumbnail text \"{best_thumbnail_text}\" manually after generating the image.",
                ),
            ]
        )

    @staticmethod
    def create_description_prompt() -> ChatPromptTemplate:
        return ChatPromptTemplate(
            [
                (
                    "system",
                    "you are expert youtube content creator specialized in creating description for given title and thumbnail text for this *{topic}* topic.",
                ),
                (
                    "user",
                    "create a description for the youtube video for this **Title: {best_title} ** and **Thumbnail_text: {best_thumbnail_text}**.",
                ),
            ]
        )