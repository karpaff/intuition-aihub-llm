from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.modules.rag.routers.rag import router as rag_router
from src.common.database import clear_messages_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    clear_messages_table()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(rag_router)