from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from agent.graph.models import State
from agent.graph.nodes import error_handling_node, file_selection_node, files_getting_node, file_downloading_node, file_questions_node

workflow = StateGraph(State)

workflow.add_node("files_getting", files_getting_node)
workflow.add_node("file_selection", file_selection_node)
workflow.add_node("file_downloading", file_downloading_node)
workflow.add_node("file_questions", file_questions_node)
workflow.add_node("error_handling", error_handling_node)

def start_router(state):
    if  state.get("available_files", None) is None:
        return "files_getting"
    if state.get("selected_file_id", None) is None:
        return "file_selection"
    if state.get("selected_file_path", None) is None:
        return "file_downloading"
    return "file_questions"

def router(state, current_node):
    if not state["error"] is None:
        return "error_handling"
    match current_node:
        case "files_getting":
            return "file_selection" if state.get("available_files", None) is not None else "__end__"
        case "file_selection":
            return "file_downloading" if state.get("selected_file_id", False) else "__end__"
        case "file_downloading":
            return "file_questions" if state.get("selected_file_path", False) else "__end__"
        case "file_questions":
            return "__end__" if state.get("error", None) is None else "error_handling"

workflow.add_conditional_edges(
    "__start__",
    start_router
)
workflow.add_conditional_edges(
    "files_getting",
    lambda state: router(state, "files_getting")
)
workflow.add_conditional_edges(
    "file_selection",
    lambda state: router(state, "file_selection")
)
workflow.add_conditional_edges(
    "file_downloading",
    lambda state: router(state, "file_downloading")
)
workflow.add_conditional_edges(
    "file_questions",
    lambda state: router(state, "file_questions")
)
workflow.add_edge(
    "error_handling",
    "__end__"
)


app = workflow.compile(checkpointer=MemorySaver())

async def interact(user_id: str, messages: list[BaseMessage], verbose: bool = False) -> str:
    """Entry point for interacting with langgraph application."""
    saved_state = app.get_state({"configurable": {"thread_id": user_id}})
    if saved_state.values:
        state = saved_state.values
        if messages and len(messages) > 0:
            state["message_history"].append(messages[-1])
    else:
        state = State(
            user_id=user_id,
            verbose=verbose,
            message_history=messages,
            error=None,
            error_type=None
        )

    state = await app.ainvoke(state, config={"configurable": {"thread_id": user_id}})
    print(state)
    return state["current_response"]
