import fitz
from langchain_qdrant import Qdrant
from qdrant_client import models
import os
import time
import gdown
import re
from uuid import uuid4
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from loguru import logger

from src.config import settings
from src.common import qdrant_client
from src.modules.rag.components.embeddings import vector_store



def is_collection_exists(client: Qdrant, collection_name: str) -> bool:
    try:
        client.get_collection(collection_name)
        return True
    except Exception:
        return False
    
def download_pdf(url: str, output_path: str) -> str:
    logger.info(f"Скачивание PDF: {url}")
    gdown.download(url, output_path, quiet=False, fuzzy=True)

def add_documents_in_batches(
    qdrant_store: Qdrant,
    documents: List[Document],
    batch_size: int = settings.QDRANT_UPLOAD_BATCH_SIZE,
    max_retries: int = settings.QDRANT_MAX_RETRIES
  ):

    total_docs = len(documents)
    added_docs = 0

    for i in range(0, total_docs, batch_size):
        batch = documents[i:i + batch_size]
        retry_count = 0

        while retry_count < max_retries:
            try:
                qdrant_store.add_documents(batch)
                added_docs += len(batch)
                logger.info(f"[OK] Qdrant: Добавлено {added_docs}/{total_docs} документов")
                break

            except Exception as e:
                retry_count += 1
                logger.info(f"[FAIL] Qdrant: Ошибка при добавлении батча {i//batch_size + 1}, попытка {retry_count}/{max_retries}: {e}")
                time.sleep(5)
                if retry_count >= max_retries:
                    raise e

def get_chunks(pdf_path: str, splitter) -> List[Document]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Файл не найден: {pdf_path}")

    doc = fitz.open(pdf_path)
    full_text = ""
    pdf_name = os.path.basename(pdf_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        full_text += "\n" + page.get_text("text")
    doc.close()

    if not full_text.strip():
        raise ValueError("Не удалось извлечь текст из PDF")

    text = "\n" + full_text.strip()
    pattern = r'\n(\d+)\s*\n'
    parts = re.split(pattern, text)

    chapters = []
    global_chapter_num = 1

    i = 1
    while i < len(parts):
        if i + 1 < len(parts):
            local_num = parts[i].strip()
            chapter_text = parts[i + 1].strip()
            if chapter_text and local_num.isdigit():
                chapters.append({
                    "title": str(global_chapter_num),
                    "local_title": local_num,
                    "text": chapter_text,
                    "source": pdf_name
                })
                global_chapter_num += 1
            i += 2
        else:
            i += 1

    if not chapters:
        chapters.append({
            "title": "1",
            "local_title": "1",
            "text": full_text.strip(),
            "source": pdf_name
        })

    langchain_docs = []
    for ch in chapters:
        doc = Document(
            page_content=ch["text"],
            metadata={
                "source": ch["source"],
                "chapter": ch["title"],        
            }
        )
        langchain_docs.append(doc)

    chunks = splitter.split_documents(langchain_docs)
    return chunks


def chunk_upload_qdrant(
    pdf_path: str,
    qdrant_store: Qdrant,
    splitter: RecursiveCharacterTextSplitter
):
    chunks = get_chunks(pdf_path, splitter)
    logger.info(f"{len(chunks)} чанков")
    add_documents_in_batches(qdrant_store, chunks)


def main():
    
    if not os.path.exists(settings.TEMP_DIR):
        os.mkdir(settings.TEMP_DIR)

    if is_collection_exists(qdrant_client, settings.QDRANT_COLLECTION):
        logger.info(f"Коллекция {settings.QDRANT_COLLECTION} уже существует")
        return
    
    filename = uuid4().hex + ".pdf"
    pdf_path = os.path.join(settings.TEMP_DIR, filename)
    download_pdf(settings.QDRANT_BOOK_URL, pdf_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.QDRANT_CHUNK_SIZE,
        chunk_overlap=settings.QDRANT_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
        is_separator_regex=False,
        strip_whitespace=True
    )

    qdrant_client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=models.VectorParams(
            size=settings.EMBEDDING_SIZE,
            distance=models.Distance.COSINE
        )
    )
    logger.info(f"Коллекция {settings.QDRANT_COLLECTION} только что была создана")

    chunk_upload_qdrant(
        pdf_path=pdf_path,
        qdrant_store=vector_store,
        splitter=splitter
    )
    os.remove(pdf_path)



if __name__ == "__main__":
    main()