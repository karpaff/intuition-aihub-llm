from langchain.embeddings.base import Embeddings
from langchain_qdrant import Qdrant
from yandex_cloud_ml_sdk import YCloudML
from typing import List
import numpy as np
import time

from src.config import settings
from src.common import qdrant_client



class YandexCloudEmbeddings(Embeddings):
    """Класс-обертка для эмбеддингов Yandex Cloud, совместимый с LangChain."""

    def __init__(
          self,
          folder_id: str,
          api_key: str,
          requests_per_second: int=9,
          timeout: float=60.0
        ):

        self.sdk = YCloudML(
            folder_id=folder_id,
            auth=api_key
        )
        self.query_model = self.sdk.models.text_embeddings("query")
        self.doc_model = self.sdk.models.text_embeddings("doc")
        self.vector_size = 256
        self.delay = 1.0 / requests_per_second
        self.timeout = timeout

    def _rate_limited_run(self, model, text: str) -> List[float]:
        """Выполняет запрос с учетом ограничения скорости."""
        result = model.run(text, timeout=self.timeout)
        time.sleep(self.delay)
        return result

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Получает эмбеддинги для списка документов с учетом ограничения скорости."""
        return [self._rate_limited_run(self.doc_model, text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Получает эмбеддинг для запроса."""
        return self._rate_limited_run(self.query_model, text)

    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """Совместимость с интерфейсом SentenceTransformer."""
        embeddings = self.embed_documents(texts)
        return np.array(embeddings)
    


embeddings_model = YandexCloudEmbeddings(
    folder_id=settings.YANDEX_FOLDER_ID,
    api_key=settings.YANDEX_API_KEY
)
vector_store = Qdrant(
    client=qdrant_client,
    collection_name=settings.QDRANT_COLLECTION,
    embeddings=embeddings_model
)