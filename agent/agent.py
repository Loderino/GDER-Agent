import httpx

from agent.exceptions import AgentError
from agent.GD.requestor import GDRequestor
from agent.graph.workflows import interact
from agent.llm.models import LLMAgent


class Agent:
    """
    Agent for access to excel files on Google Drive using langgraph.

    Attributes:
        api_key (str): Your OpenAI API key.
        api_base (str): The base URL for the OpenAI API.
        model (str): The api-name of the model to use for the chat.

    Methods:
        check_health: Checks if the llm and Google Drive are available.
        communicate: Communicates with the langgraph agent.
    """

    api_key = None
    base_url = None
    model = None

    def __setattr__(self, name: str, value: str):
        """
        Sets an attribute on the Agent instance.

        Args:
            name (str): The name of the attribute to set.
            value (str): The value to set for the attribute.
        """
        if name == "base_url":
            LLMAgent.base_url = value
        elif name == "api_key":
            LLMAgent.api_key = value if value else "key"
        elif name == "model":
            LLMAgent.model = value

    @staticmethod
    async def check_health() -> bool:
        """
        Checks the health of the agent.

        Returns:
            bool: True if the agent is healthy.

        Raises:
            AgentError: if some problems with Google drive authentication or llm is unreachable.
        """
        try:
            response = httpx.get(
                LLMAgent.base_url + "/models",
                headers={"Authorization": "Bearer " + LLMAgent.api_key},
                timeout=5,
            )
        except (httpx.ConnectTimeout, httpx.ConnectError) as exc:
            raise AgentError("No connection to llm api") from exc
        except httpx.LocalProtocolError as exc:
            raise AgentError(str(exc)) from exc
        if response.status_code == 401:
            raise AgentError("wrong api key")
        if response.status_code != 200:
            raise AgentError("wrong llm data")
        for model in response.json()["data"]:
            if model["id"] == LLMAgent.model:
                break
        else:
            raise AgentError(f"model {LLMAgent.model} not available.")
        GDRequestor()
        return True

    async def communicate(self, user_id: int, messages: list) -> str:
        """
        Communicates with the langgraph agent.

        Args:
            user_id (int): The ID of the user.
            messages (list): The message history.

        Returns:
            str: The response from the agent.
        """
        return await interact(user_id, messages)
