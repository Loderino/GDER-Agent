from langchain_core.tools import StructuredTool

from agent.parser.parser import WebParser

parser = WebParser()

def get_tools() -> list[StructuredTool]:
    """
    Returns a list of tools functions for llm.
    """
    tools = []
    for func in [parser.get_site_info]:
        tools.append(StructuredTool.from_function(func, name=func.__name__, description=func.__doc__))
    return tools