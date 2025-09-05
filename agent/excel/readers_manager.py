from agent.excel.excel_reader import ExcelReader


class Manager:
    """
    Manager for storing and retrieving ExcelReader instances.
    """

    _readers = {}

    @classmethod
    def get_reader(cls, user_id: str, file_name=None, file_path=None) -> ExcelReader:
        """Get an ExcelReader instance for a given user_id.

        If an instance does not exist, create a new one.

        Args:
            user_id (str): Unique identifier for the user.
            file_name (str): Optional file name to pass to ExcelReader.
            file_path (str): Optional file path to pass to ExcelReader.

        Returns:
            ExcelReader: The ExcelReader instance for the given user_id.
        """
        if user_id not in cls._readers or file_name or file_path:
            cls._readers[user_id] = ExcelReader(file_name, file_path)
        return cls._readers[user_id]
