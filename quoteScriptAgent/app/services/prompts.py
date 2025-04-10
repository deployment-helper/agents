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