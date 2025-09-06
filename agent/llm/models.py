from langchain_core.messages import BaseMessage, trim_messages
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APITimeoutError, BadRequestError, NotFoundError

from agent.exceptions import LLMError


class LLMAgent:
    """
    Class for communicating with LLM.
    """

    model: str = None
    api_key: str = None
    base_url: str = None

    def __init__(
        self, tools: list = None, schema: dict = None, max_tokens: int = 1000, **kwargs
    ):
        """
        Makes llm instance with necessary settings.

        Args:
            tools (list, optional): list of tools to bind to llm. Defaults to None.
            schema (dict, optional): json schema for llm structured answer. Defaults to None.
            max_tokens (int, optional): max count of tokens in llm answer. Defaults to 1000.

        Raises:
            RuntimeError: if was attempt to create llm instance without model or api key.
        """
        if self.model is None or self.api_key is None:
            raise RuntimeError("The model and the api_key must be specified.")
        if tools:
            self.llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=30,
                max_completion_tokens=max_tokens,
            ).bind_tools(tools, **kwargs)
        else:
            self.llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=30,
                max_completion_tokens=max_tokens,
            )
        if schema:
            self.llm = self.llm.with_structured_output(
                schema, method="json_mode", include_raw=True
            )

    async def call_model(self, messages: list[BaseMessage]) -> BaseMessage:
        """
        Makes a request to llm.

        Args:
            messages (list[BaseMessage]): chat history.

        Returns:
            BaseMessage: llm response.

        Raises: LLMError when problems with response completion.
        """
        # counter = ChatOpenAI(model=self.model, api_key=self.api_key)
        # messages = trim_messages(messages, max_tokens=1000, token_counter=counter)

        try:
            return await self.llm.ainvoke(messages)
        except NotFoundError as exc:
            raise LLMError(f"Model {self.model} is not supports tools.") from exc
        except APITimeoutError as exc:
            raise LLMError(f"Model {self.model} is not available.") from exc
        except APIConnectionError as exc:
            raise LLMError(f"Model {self.model} is not available.") from exc
        except BadRequestError as exc:
            raise LLMError(f"Model {self.model} is not supports tools.") from exc
