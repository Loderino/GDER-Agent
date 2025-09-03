import os
from agent.llm.models import LLMAgent
from agent.graph.workflows import interact

class Agent:
    """
    Mail agent for interacting with email accounts using langgraph.

    Attributes:
        api_key (str): Your OpenAI API key.
        api_base (str): The base URL for the OpenAI API.
        model (str): The api-name of the model to use for the chat.
        db_dir (str): the path to the directory containing the database files.

    Methods:
        communicate: Communicates with the langgraph agent.
    """

    api_key = None
    api_base = None
    model = None
    # db_dir = "./"
    # _db_url = "sqlite://{}/db.sqlite3"

    # def __init__(self):
    #     """
    #     Initializes the MailAgent instance.
    #     """
    #     DBHandler.DB_URL = self._db_url.format(self.db_dir)

    def __setattr__(self, name: str, value: str):
        """
        Sets an attribute on the MailAgent instance.

        Args:
            name (str): The name of the attribute to set.
            value (str): The value to set for the attribute.
        """
        if name == "api_base":
            LLMAgent.base_url = value
        elif name == "api_key":
            LLMAgent.api_key = value
        elif name == "model":
            LLMAgent.model = value
        # elif name == "db_dir":
        #     if os.path.isdir(value):
        #         value = str(value).rstrip("/")
        #         DBHandler.DB_URL = self._db_url.format(value)
        #     else:
        #         raise ValueError("The db_dir path must be an existing directory.")

    async def communicate(self, user_id, messages, verbose=False):
        """
        Communicates with the langgraph agent.

        Args:
            user_id (int): The ID of the user to communicate with.
            message (str): The message to send to the user.
            verbose (bool): Whether to print the response from the agent.

        Returns:
            str: The response from the agent.
        """
        return await interact(user_id, messages, verbose=verbose)

