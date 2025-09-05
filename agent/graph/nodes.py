from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

from agent.GD.requestor import GDRequestor
from agent.graph.models import State
from agent.graph.tools import get_tools
from agent.llm.models import LLMAgent
from agent.llm.prompts import FILE_SELECTION_PROMPT, FILE_QUESTIONS_PROMPT


# async def authentication_node(state: State) -> State:
#     """
#     Authentication node in the application graph.
#     Checks if the .
#     """
#     if state["verbose"]:
#         print("==========AUTHENTICATION NODE==========", end="\n\n")
#     try:
#         GDRequestor()
#         state["authenticated"] = True
#     except Exception as e:
#         state["error"] = str(e)
#         state["error_type"] = "authentication"
#         state["authenticated"] = False
#     return state

async def files_getting_node(state: State) -> State:
    """
    Node for getting list of excel files from Google drive.
    """
    if state["verbose"]:
        print("==========FILES GETTING NODE==========", end="\n\n")
    state["available_files"] = GDRequestor().list_files()
    return state

async def file_selection_node(state: State) -> State:
    """
    Node for selecting the excel file in list from previous node.
    """
    if state["verbose"]:
        print("==========FILE SELECTION NODE==========", end="\n\n")

    schema = {
        "file_id": "Id файла, который выбрал пользователь",
        "file_name": "Имя файла, который выбрал пользователь",
        "answer": "ответ пользователю"
    }
    llm = LLMAgent(schema=schema)
    system_message = SystemMessage(content=FILE_SELECTION_PROMPT.format(state["available_files"]))
    if state["verbose"]:
        print("SYSTEM MESSAGE:", system_message.content, end="\n\n")
    messages = [system_message, *state["message_history"]]
    response = await llm.call_model(messages)
    response = response["parsed"]
    state["current_response"] = response["answer"]
    state["selected_file_id"] = response["file_id"]
    state["selected_file_name"] = response["file_name"]
    return state


async def file_reading_node(state: State) -> State:
    """
    Node for downloading selected excel file from Google drive.
    """
    if state["verbose"]:
        print("==========FILE DOWNLOADING NODE==========", end="\n\n")
    state["current_file_data"] = GDRequestor().read_excel(state["selected_file_id"])
    return state

async def file_questions_node(state: State) -> State:
    """
    Node for handle the users questions about selected file content.
    """
    if state["verbose"]:
        print("==========FILE QUESTIONS NODE==========", end="\n\n")
    schema = {
        "answer": "ответ пользователю",
        "reselect": "флаг для выбора другого файла"
    }

    tools = get_tools()
    llm_with_tools = LLMAgent(tools=tools, max_tokens=1, tool_choice="auto")
    llm = LLMAgent(schema=schema)
    system_message = SystemMessage(content=FILE_QUESTIONS_PROMPT.format(state["selected_file_name"], state["current_file_data"]))

    messages = [system_message, *state["message_history"]]
    response = await llm_with_tools.call_model(messages)
    print(response)
    intermediate_steps = []
    if hasattr(response, "tool_calls"):
        for tool_call in response.tool_calls:
            if state["verbose"]:
                print(tool_call)
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            tool = next(t for t in tools if t.name == tool_name)
            tool_result = await (await tool.ainvoke(tool_args))

            intermediate_steps.append((tool_call, tool_result))

    full_messages = messages.copy()
    for tool_call, tool_result in intermediate_steps:
        if state["verbose"]:
            print("TOOL:", tool_call, end="\n\n")
        full_messages.append(AIMessage(content="", tool_calls=[tool_call]))
        full_messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

    final_response = await llm.call_model(full_messages)

    state["current_response"] = final_response["parsed"]["answer"]
    if final_response["parsed"]["reselect"]:
        state["current_file_data"] = None
        state["available_files"] = None
        state["selected_file_id"] = None
        state["selected_file_name"] = None
    return state

async def error_handling_node(state: State) -> State:
    pass