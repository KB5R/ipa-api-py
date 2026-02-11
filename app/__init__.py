from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FreeIPA API",
    description="API для управления пользователями FreeIPA",
    version="1.0.0"
)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.31.185:3000",
        "http://192.168.31.185:8080",  # API тоже может быть origin
        "file://"  # Для открытия через file://
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)