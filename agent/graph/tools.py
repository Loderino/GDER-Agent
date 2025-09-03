from agent.parser.parser import WebParser
from langchain_core.tools import StructuredTool

parser = WebParser()

def get_tools():
    tools = []
    for func in [parser.get_site_info]:
        tools.append(StructuredTool.from_function(func, name=func.__name__, description=func.__doc__))
    return tools