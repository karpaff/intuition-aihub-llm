from qdrant_client import QdrantClient

from src.config import settings



qdrant_client = QdrantClient(
    url=settings.QDRANT_URL, 
    api_key=settings.QDRANT_KEY
)