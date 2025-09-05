from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from agent.graph.models import State
from agent.graph.nodes import file_selection_node, files_getting_node, file_reading_node, file_questions_node

workflow = StateGraph(State)

workflow.add_node("files_getting", files_getting_node)
workflow.add_node("file_selection", file_selection_node)
workflow.add_node("file_reading", file_reading_node)
workflow.add_node("file_questions", file_questions_node)

def router(state):
    if  state.get("available_files", []) is None:
        return "files_getting"
    if state.get("selected_file_id", None) is None:
        return "file_selection"
    if state.get("current_file_data", None) is None:
        return "file_reading"
    return "file_questions"

workflow.add_conditional_edges(
    "__start__",
    router
)
workflow.add_conditional_edges(
    "files_getting",
    lambda state: "file_selection" if state.get("available_files", None) is not None else "__end__"
)
workflow.add_conditional_edges(
    "file_selection",
    lambda state: "file_reading" if state.get("selected_file_id", False) else "__end__"
)
workflow.add_conditional_edges(
    "file_reading",
    lambda state: "file_questions" if state.get("current_file_data", False) else "__end__"
)
workflow.add_edge(
    "file_questions",
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
            verbose=verbose,
            message_history=messages,
            authenticated=False,
            files_listed=False
        )

    state = await app.ainvoke(state, config={"configurable": {"thread_id": user_id}})
    return state["current_response"]
