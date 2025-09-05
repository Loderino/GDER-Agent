from typing import Optional
from typing import TypedDict
from langchain_core.messages import BaseMessage

class State(TypedDict):
    """State for the Google Drive agent workflow."""

    message_history: list[BaseMessage]  # История сообщений
    current_response: Optional[str]  # Текущий ответ агента

    authenticated: bool  # Прошла ли аутентификация
    selected_file_id: Optional[str]  # ID выбранного файла
    selected_file_name: Optional[str]  # имя выбранного файла

    available_files: Optional[list[dict]]  # Список доступных файлов
    current_file_data: dict  # Данные выбранного файла

    verbose: bool  # Режим подробного вывода

    error: Optional[str]  # Сообщение об ошибке, если есть
    error_type: Optional[str]  # Тип ошибки