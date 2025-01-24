from contextlib import asynccontextmanager

from database import sessionmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.audio_process import router as audio_process_router
from routers.chat import router as chat_router
from routers.healthcheck import router as healthcheck_router
from routers.image_processing import router as image_processing_router
from routers.user import router as user_router
from sqlalchemy import select

# URL de conexão com o banco de dados SQLite
DATABASE_URL = "sqlite+aiosqlite:///./better_ai.db"


# Creating engine to be use through the whole app
async def check_db_connection():
    async with sessionmanager.session() as session:
        print("Starting database connection...")
        await session.execute(select(1))
        print("Database connection successful")


sessionmanager.init(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_db_connection()
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


# Instância do FastAPI
app = FastAPI(title="API to help you improve your life using habits", lifespan=lifespan)

# Incluindo os routers
app.include_router(healthcheck_router)
app.include_router(audio_process_router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(image_processing_router)

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", reload=True)
