import asyncio

from api.main import run_api
from agent.agent import Agent
from langchain_core.messages import HumanMessage, AIMessage
from agent.constants import LLM_API_NAME, LLM_API_KEY, LLM_API_BASE
from agent.exceptions import AgentError


agent = Agent()
agent.api_key = LLM_API_KEY
agent.base_url = LLM_API_BASE
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
        traceback.format_exc()
        return
    
    await run_api()


asyncio.run(main())