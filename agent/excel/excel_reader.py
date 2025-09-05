import pandas as pd

class ExcelReader:
    def __init__(self, file_name, file):
        """Инициализация с путем к Excel-файлу."""
        self.file_name = file_name
        self.excel_file = pd.ExcelFile(file)
        self.sheets = self.excel_file.sheet_names
        self.dataframes = {}

    def get_file_summary(self):
        """Возвращает общую информацию о файле."""
        return {
            "file_name": self.file_name,
            "sheet_count": len(self.sheets),
            "sheet_names": self.sheets
        }

    def get_sheet_preview(self, sheet_name=None):
        """Возвращает предпросмотр указанного листа."""
        if sheet_name is None:
            sheet_name = self.sheets[0]

        if sheet_name not in self.dataframes:
            self.dataframes[sheet_name] = pd.read_excel(self.excel_file, sheet_name)

        df = self.dataframes[sheet_name]

        return {
            "sheet_name": sheet_name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "preview_rows": df.head(5).to_dict(orient="records"),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }

    def search_data(self, sheet_name, search_term):
        """Ищет данные на листе по ключевому слову."""
        if sheet_name not in self.dataframes:
            self.dataframes[sheet_name] = pd.read_excel(self.excel_file, sheet_name)

        df = self.dataframes[sheet_name]

        # Поиск по всем столбцам
        matches = []
        for col in df.columns:
            if df[col].dtype == 'object':  # Только для текстовых столбцов
                matches.extend(df[df[col].astype(str).str.contains(search_term, case=False, na=False)].to_dict(orient="records"))

        return {
            "sheet_name": sheet_name,
            "search_term": search_term,
            "matches_count": len(matches),
            "matches": matches[:10]  # Ограничиваем количество результатов
        }

    def get_cell_value(self, sheet_name, cell_reference):
        """Получает значение ячейки по ссылке (A1, B2 и т.д.)."""
        if sheet_name not in self.dataframes:
            self.dataframes[sheet_name] = pd.read_excel(self.excel_file, sheet_name)

        df = self.dataframes[sheet_name]

        # Преобразование ссылки A1 в индексы
        import re
        match = re.match(r'([A-Z]+)(\d+)', cell_reference)
        if not match:
            return {"error": f"Неверный формат ссылки: {cell_reference}"}

        col_str, row_str = match.groups()
        row_idx = int(row_str) - 1

        # Преобразование буквенного обозначения столбца в индекс
        col_idx = 0
        for c in col_str:
            col_idx = col_idx * 26 + (ord(c) - ord('A') + 1)
        col_idx -= 1

        # Проверка границ
        if row_idx < 0 or row_idx >= len(df) or col_idx < 0 or col_idx >= len(df.columns):
            return {"error": f"Ячейка {cell_reference} находится за пределами таблицы"}

        # Получение значения
        value = df.iloc[row_idx, col_idx]
        return {
            "sheet_name": sheet_name,
            "cell_reference": cell_reference,
            "value": value
        }

    def analyze_column(self, sheet_name, column_name):
        """Анализирует указанный столбец."""
        if sheet_name not in self.dataframes:
            self.dataframes[sheet_name] = pd.read_excel(self.excel_file, sheet_name)

        df = self.dataframes[sheet_name]

        if column_name not in df.columns:
            return {"error": f"Столбец {column_name} не найден"}

        column = df[column_name]

        # Базовая статистика
        stats = {
            "count": len(column),
            "null_count": column.isna().sum(),
            "unique_values": column.nunique()
        }

        # Дополнительная статистика для числовых столбцов
        if pd.api.types.is_numeric_dtype(column):
            stats.update({
                "min": float(column.min()),
                "max": float(column.max()),
                "mean": float(column.mean()),
                "median": float(column.median()),
                "std": float(column.std())
            })

        # Для категориальных данных
        else:
            # Наиболее частые значения
            value_counts = column.value_counts().head(5).to_dict()
            stats["most_common_values"] = {str(k): int(v) for k, v in value_counts.items()}

        return {
            "sheet_name": sheet_name,
            "column_name": column_name,
            "stats": stats
        }

