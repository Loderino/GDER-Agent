from agent.llm.models import LLMAgent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from agent.graph.models import State
from agent.GD.requestor import GDRequestor

# from neuromail_agent.db.db_handler import DBHandler
# from neuromail_agent.client.client_manager import ImapClientManager
# from neuromail_agent.client.models import make_credentials
# from neuromail_agent.graph.models import State
from agent.llm.prompts import FILE_SELECTION_PROMPT, FILE_QUESTIONS_PROMPT
# from neuromail_agent.graph.tools import get_tools

# llm_with_tools = LLMAgent(tools=tools, tool_choice="update_record")

async def authentication_node(state: State) -> State:
    """
    Authentication node in the application graph.
    Checks user record in database and connection to IMAP server.
    """
    if state["verbose"]:
        print("==========AUTHENTICATION NODE==========", end="\n\n")
        try:
            GDRequestor()
            state["authenticated"] = True
        except Exception as e:
            state["error"] = str(e)
            state["error_type"] = "authentication"
            state["authenticated"] = False
    return state

async def files_getting_node(state: State) -> State:
    if state["verbose"]:
        print("==========FILES GETTING NODE==========", end="\n\n")
    state["available_files"] = GDRequestor().list_files()
    return state

async def file_selection_node(state: State) -> State:
    if state["verbose"]:
        print("==========FILE SELECTION NODE==========", end="\n\n")

    schema = {
        "file_id": "Id файла, который выбрал пользователь",
        "file_name": "Имя файла, который выбрал пользователь",
        "answer": "ответ пользователю"
    }
    llm = LLMAgent(schema=schema)
    system_message = SystemMessage(content=FILE_SELECTION_PROMPT.format(state["available_files"]))
    # if state["verbose"]:
        # print("SYSTEM MESSAGE:", system_message.content, end="\n\n")
    messages = [system_message, *state["message_history"]]
    response = await llm.call_model(messages)
    state["current_response"] = response["message"]
    state["selected_file_id"] = response["file_id"]
    state["selected_file_name"] = response["file_name"]
    return state


async def file_reading_node(state: State) -> State:
    if state["verbose"]:
        print("==========FILE DOWNLOADING NODE==========", end="\n\n")
    state["current_file_data"] = GDRequestor().read_excel(state["selected_file_id"])
    return state

async def file_questions_node(state: State) -> State:
    if state["verbose"]:
        print("==========FILE QUESTIONS NODE==========", end="\n\n")
    schema = {
        "answer": "ответ пользователю",
        "reselect": "флаг для выбора другого файла"
    }
    llm = LLMAgent(schema=schema)
    system_message = SystemMessage(content=FILE_QUESTIONS_PROMPT.format(state["selected_file_name"], state["current_file_data"]))
    # if state["verbose"]:
        # print("SYSTEM MESSAGE:", system_message.content, end="\n\n")
    messages = [system_message, *state["message_history"]]
    response = await llm.call_model(messages)
    # print(response)
    state["current_response"] = response["answer"]
    if response["reselect"]:
        state["current_file_data"] = None
        state["available_files"] = None
        state["selected_file_id"] = None
        state["selected_file_name"] = None
    return state

async def error_handling_node(state: State) -> State:
    pass