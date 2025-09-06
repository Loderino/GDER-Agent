from langchain_core.tools import StructuredTool

from agent.excel.readers_manager import Manager
from agent.parser.parser import WebParser

parser = WebParser()


def get_tools(user_id: str) -> list[StructuredTool]:
    """
    Returns a list of tools functions for llm, specified for user.
    """
    tools = []
    excel_reader = Manager.get_reader(user_id)
    for func in [
        parser.get_site_info,
        excel_reader.get_sheet_preview,
        excel_reader.search_data,
        excel_reader.get_cell_value,
        excel_reader.get_range_values,
        excel_reader.analyze_column,
    ]:
        tools.append(
            StructuredTool.from_function(
                func, name=func.__name__, description=func.__doc__
            )
        )
    return tools
