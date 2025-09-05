# Google Drive Excel Reader Agent

## Установка и запуск

### Через venv
 
1) Установить зависимости: 

```bash
python3 -m venv venv
source venv/bin/activate
```

2) Заполнить .env файл:

GD_CREDENTIALS_FILE - путь к фалу для аутентификации в Google Drive;
LLM_BASE_URL - базовый адрес llm провайдера. Провайдер должен быть OpenAI совместимым. *Пример: "http://127.0.0.1:11434/v1"*;
LLM_API_KEY - secret key для доступа к моделям. Если не нужен, оставить пустую строку;
LLM_API_NAME - API name выбранной модели. Модель обязательно должна поддерживать tools;

HOST - адрес, на котором будет работать API. По умолчанию 0.0.0.0;
PORT - порт,  на котором будет работать API. По умолчанию 5555.

3) Запуск:

```bash
python run.py
```