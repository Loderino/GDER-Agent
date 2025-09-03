from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langchain_core.messages import BaseMessage
from agent.graph.models import State
from agent.graph.nodes import authentication_node, file_selection_node, files_getting_node, file_reading_node, file_questions_node

workflow = StateGraph(State)

workflow.add_node("authentication", authentication_node)
workflow.add_node("files_getting", files_getting_node)
workflow.add_node("file_selection", file_selection_node)
workflow.add_node("file_reading", file_reading_node)
workflow.add_node("file_questions", file_questions_node)

# Добавляем функцию-маршрутизатор для определения начального узла
def router(state):
    if not state.get("authenticated", False):
        return "authentication"
    if not state.get("available_files", False):
        return "files_getting"
    if not state.get("selected_file_id", False):
        return "file_selection"
    if not state.get("current_file_data", False):
        return "file_reading"
    return "file_questions"

workflow.add_conditional_edges(
    "__start__",
    router
)

# Добавляем условные переходы
workflow.add_conditional_edges(
    "authentication",
    lambda state: "files_getting" if state.get("authenticated", False) else "authentication"
)
workflow.add_conditional_edges(
    "files_getting",
    lambda state: "file_selection" if state.get("available_files", False) else "files_getting"
)
workflow.add_conditional_edges(
    "file_selection",
    lambda state: "file_reading" if state.get("selected_file_id", False) else "__end__"#"file_selection"
)
workflow.add_conditional_edges(
    "file_reading",
    lambda state: "file_questions" if state.get("current_file_data", False) else "__end__"#"file_reading"
)
workflow.add_edge(
    "file_questions",
    "__end__"#"file_questions"
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
