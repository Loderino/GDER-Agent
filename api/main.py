import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


async def run_api(
    host: str = os.getenv("HOST", "0.0.0.0"),
    port: int = int(os.getenv("PORT", "5555")),
    reload: bool = False,
) -> None:
    """
    Asynchronously runs the API server using Uvicorn.

    Args:
        host (str): The host IP address to bind the server to. Defaults to API_HOST environment variable or "0.0.0.0".
        port (int): The port number to bind the server to. Defaults to API_PORT environment variable or 8000.
        reload (bool): Whether to enable auto-reloading of the server. Defaults to False.
    """
    config = uvicorn.Config(app, host=host, port=port, reload=reload)
    server = uvicorn.Server(config)
    await server.serve()
