from logging import getLogger

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

from agent.constants import LOG_LEVEL
from agent.excel.readers_manager import Manager
from agent.exceptions import GoogleDriveError, LLMError
from agent.GD.requestor import GDRequestor
from agent.graph.models import State
from agent.graph.tools import get_tools
from agent.llm.models import LLMAgent
from agent.llm.prompts import (FILE_QUESTIONS_PROMPT,
                               FILE_QUESTIONS_TOOLS_USE_PROMPT,
                               FILE_SELECTION_PROMPT)

MAX_TOOLS_USAGE_RETRIES = 3
logger = getLogger("nodes")
logger.setLevel(LOG_LEVEL)


async def files_getting_node(state: State) -> State:
    """
    Node for getting list of excel files from Google drive.
    """
    logger.debug("==========FILES GETTING NODE==========")
    try:
        state["available_files"] = GDRequestor().list_files()
    except GoogleDriveError as exc:
        state["error"] = str(exc)
        state["error_type"] = "GoogleDriveError"
    return state


async def file_selection_node(state: State) -> State:
    """
    Node for selecting the excel file in list from previous node.
    """
    logger.debug("==========FILE SELECTION NODE==========")
    schema = {
        "file_id": "Id файла, который выбрал пользователь",
        "file_name": "Имя файла, который выбрал пользователь",
        "answer": "ответ пользователю",
    }
    llm = LLMAgent(schema=schema)
    system_message = SystemMessage(
        content=FILE_SELECTION_PROMPT.format(state["available_files"])
    )

    messages = [system_message, *state["message_history"]]
    try:
        response = await llm.call_model(messages)
    except LLMError as exc:
        state["error"] = str(exc)
        state["error_type"] = "LLMError"
        return state
    response = response["parsed"]
    state["current_response"] = response.get("answer", "хорошо")
    state["selected_file_id"] = response["file_id"]
    state["selected_file_name"] = response["file_name"]
    return state


async def file_downloading_node(state: State) -> State:
    """
    Node for downloading selected excel file from Google drive.
    """
    logger.debug("==========FILE DOWNLOADING NODE==========")
    try:
        state["selected_file_path"] = GDRequestor().download_file(
            state["selected_file_id"]
        )
    except GoogleDriveError as exc:
        state["error"] = str(exc)
        state["error_type"] = "GoogleDriveError"
    return state


async def file_questions_node(state: State) -> State:
    """
    Node for handle the users questions about selected file content.
    """
    logger.debug("==========FILE QUESTIONS NODE==========")
    schema = {
        "answer": "ответ пользователю",
        "reselect": "флаг для выбора другого файла",
    }
    excel_reader = Manager.get_reader(
        state["user_id"], state["selected_file_name"], state["selected_file_path"]
    )

    llm = LLMAgent(schema=schema)
    tools = get_tools(state["user_id"])
    llm_with_tools = LLMAgent(tools=tools, tool_choice="auto")

    system_message = SystemMessage(
        content=FILE_QUESTIONS_TOOLS_USE_PROMPT.format(
            state["selected_file_name"],
            await excel_reader.get_file_summary(),
            await excel_reader.get_sheet_preview(),
        )
    )

    messages = [system_message, *state["message_history"]]
    for _ in range(MAX_TOOLS_USAGE_RETRIES):
        try:
            response = await llm_with_tools.call_model(messages)
        except LLMError as exc:
            state["error"] = str(exc)
            state["error_type"] = "LLMError"
            return state

        intermediate_steps = []
        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                tool = next(t for t in tools if t.name == tool_name)
                tool_result = await (await tool.ainvoke(tool_args))
                intermediate_steps.append((tool_call, tool_result))
        else:
            break
        for tool_call, tool_result in intermediate_steps:
            logger.debug("TOOL: %s", str(tool_call))
            messages.append(AIMessage(content="", tool_calls=[tool_call]))
            messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
            )

    system_message = SystemMessage(
        content=FILE_QUESTIONS_PROMPT.format(
            state["selected_file_name"],
            await excel_reader.get_file_summary(),
            await excel_reader.get_sheet_preview(),
        )
    )
    messages[0] = system_message
    try:
        response = await llm.call_model(messages)
    except LLMError as exc:
        state["error"] = str(exc)
        state["error_type"] = "LLMError"
        return state

    state["current_response"] = response["parsed"]["answer"]
    if response["parsed"]["reselect"]:
        state["selected_file_path"] = None
        state["available_files"] = None
        state["selected_file_id"] = None
        state["selected_file_name"] = None
    return state


async def error_handling_node(state: State) -> State:
    """
    Node for errors handling.
    """
    logger.debug("==========ERROR HANDLING NODE==========")
    logger.error("%s: %s", state["error_type"], state["error"])
    match state["error_type"]:
        case "LLMError":
            state["current_response"] = "Извините, не могу ответить на ваш вопрос."
        case "GoogleDriveError":
            state["current_response"] = (
                "Извините, не могу установить соединение с Google Drive."
            )

    state["error"] = None
    state["error_type"] = None
    return state
