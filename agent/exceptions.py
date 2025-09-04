class AgentError(Exception):
    def __init__(self, message):
        super().__init__(message)

class GoogleDriveAuthError(Exception):
    def __init__(self, message):
        super().__init__(message)

class LLMError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)