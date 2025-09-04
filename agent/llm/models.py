from langchain_openai import ChatOpenAI
from openai import NotFoundError, APITimeoutError, APIConnectionError
from langchain_core.messages import BaseMessage
from agent.exceptions import LLMError

class LLMAgent:
    model: str = None
    api_key: str = None
    base_url: str = None
    def __init__(self, tools=None, schema=None, **kwargs):
        if self.model is None or self.api_key is None:
            raise RuntimeError("The model and the api_key must be specified.")
        if tools:
            self.llm = ChatOpenAI(
                model = self.model,
                api_key = self.api_key,
                base_url = self.base_url,
                timeout = 10
            ).bind_tools(tools, **kwargs)
        else:
            self.llm = ChatOpenAI(
                model = self.model,
                api_key = self.api_key,
                base_url = self.base_url,
                timeout = 10
            )
        if schema:
            self.llm = self.llm.with_structured_output(schema, method="json_mode", include_raw=True)
    async def call_model(self, messages: list[BaseMessage]):
        try:
            return await self.llm.ainvoke(messages)
        except NotFoundError:
            raise LLMError(f"Model {self.model} is not supports tools.")
        except APITimeoutError:
            raise LLMError(f"Model {self.model} is not available.")
        except APIConnectionError:
            raise LLMError(f"Model {self.model} is not available.")
