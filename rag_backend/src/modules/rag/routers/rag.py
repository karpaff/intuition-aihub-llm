from fastapi import APIRouter
from loguru import logger

from src.modules.rag.components.rag import rag
from src.modules.rag.schemas import RagAnswer
from src.common.database import add_message, get_chat_history

router = APIRouter(
    prefix="/rag"
)

@router.post(
    path="/get_rag_answer",
    response_model=RagAnswer
)
async def get_rag_answer(question: str):
    logger.info(f"Start process answering on question: {question}")
    add_message("user", question)

    history = get_chat_history()
    result = await rag.run_rag_pipeline(
        question, history
    )
    
    add_message("assistant", result.answer)
    logger.info(f"End process answering on question: {question}")
    return result