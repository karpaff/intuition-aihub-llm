from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.modules.rag.routers.rag import router as rag_router
from src.common.database import clear_messages_table
from src.common.middlewares import handle_exceptions_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    clear_messages_table()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(handle_exceptions_middleware)

app.include_router(rag_router)