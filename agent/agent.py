import httpx
from agent.llm.models import LLMAgent
from agent.graph.workflows import interact
from agent.GD.requestor import GDRequestor
from agent.exceptions import AgentError
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
    base_url = None
    model = None

    def __setattr__(self, name: str, value: str):
        """
        Sets an attribute on the MailAgent instance.

        Args:
            name (str): The name of the attribute to set.
            value (str): The value to set for the attribute.
        """
        if name == "base_url":
            LLMAgent.base_url = value
        elif name == "api_key":
            LLMAgent.api_key = value
        elif name == "model":
            LLMAgent.model = value

    @staticmethod
    async def check_health():
        """
        Checks the health of the agent.

        Returns:
            bool: True if the agent is healthy, False otherwise.
        """
        try:
            response = httpx.get(LLMAgent.base_url + "/models", headers={"Authorization": "Bearer " + LLMAgent.api_key}, timeout=5)
        except (httpx.ConnectTimeout, httpx.ConnectError) as exc:
            raise AgentError("No connection to llm api") from exc
        if response.status_code==401:
            raise AgentError("wrong api key")
        if response.status_code!=200:
            raise AgentError("wrong llm data")
        for model in response.json()["data"]:
            if model["id"] == LLMAgent.model:
                break
        else:
            raise AgentError(f"model {LLMAgent.model} not available.")
        GDRequestor()
        return True

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

