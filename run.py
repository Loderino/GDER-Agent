import asyncio
from langchain_core.messages import HumanMessage, AIMessage

from agent.agent import Agent
from agent.constants import LLM_API_NAME, LLM_API_KEY, LLM_BASE_URL
from agent.exceptions import AgentError
from api.main import run_api

agent = Agent()
agent.api_key = LLM_API_KEY
agent.base_url = LLM_BASE_URL
agent.model = LLM_API_NAME


async def test():
    messages = []
    while True:
        user_input = input("> ")
        messages.append(HumanMessage(content=user_input))
        response = await agent.communicate(1, messages, verbose=True)
        print(response, end="\n\n")
        messages.append(AIMessage(content=response))


import traceback


async def main():
    try:
        await agent.check_health()
    except AgentError as e:
        print(e)
        print(traceback.format_exc())
        return

    await run_api()


asyncio.run(main())
