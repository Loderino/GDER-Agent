class AgentError(Exception):
    """
    Class for errors from Agent.
    """

    def __init__(self, message):
        super().__init__(message)


class GoogleDriveAuthError(Exception):
    """
    Class for errors related with Google Drive auth process.
    """

    def __init__(self, message):
        super().__init__(message)


class GoogleDriveError(Exception):
    """
    Class for errors related with Google Drive operations.
    """

    def __init__(self, message):
        super().__init__(message)


class LLMError(RuntimeError):
    """
    Class for errors related with llm response errors
    """

    def __init__(self, message):
        super().__init__(message)
