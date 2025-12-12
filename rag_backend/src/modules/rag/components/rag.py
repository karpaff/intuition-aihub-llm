from typing import List
from langchain_core.language_models.llms import LLM
from langchain_core.vectorstores.base import VectorStore
from langchain_core.prompts import PromptTemplate
from langchain.schema import Document

from src.modules.rag.components.llm import yandex_gpt
from src.modules.rag.components.embeddings import vector_store
from src.modules.rag.schemas import SourceItem, RagAnswer
from src.config import settings


class RAG:
  def __init__(
      self,
      llm: LLM,
      vector_store: VectorStore,
      top_k_docs: int = settings.TOP_K_DOCS,
      search_type: str = settings.SEARCH_DISTANCE_TYPE
    ):

    self.llm = llm
    self.vector_store = vector_store
    self.top_k_docs = top_k_docs
    self.search_type = search_type
    self.prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=settings.PROMPT
    )


  async def retrieve_documents(
      self,
      question: str
  ) -> List[Document]:

    relevant_docs = await self.vector_store.asearch(
        query=question,
        search_type=self.search_type, 
        k=self.top_k_docs
    )
    return relevant_docs


  async def generate_answer(
      self,
      history,
      question: str,
      relevant_docs: List[Document]
  ):

    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    prompt = self.prompt.format(
        history=history,
        context=context,
        question=question
    )

    answer = await self.llm.ainvoke(prompt)
    return answer


  async def run_rag_pipeline(
      self,
      question: str,
      history
  ) -> RagAnswer:

    relevant_docs = await self.retrieve_documents(
        question=question
    )

    answer =  await self.generate_answer(
        history=history,
        question=question,
        relevant_docs=relevant_docs
    )

    return RagAnswer(
      answer=answer,
      sources=[SourceItem(
        chapter_n=doc.metadata["chapter"], 
        text_chunk=str(doc.page_content)
      ) for doc in relevant_docs]
    )
  

rag = RAG(
    llm=yandex_gpt,
    vector_store=vector_store
)