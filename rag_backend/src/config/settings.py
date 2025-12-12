from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field



class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Server
    HOST: str = Field("localhost")
    PORT: int = Field(8000)
    PRODUCTION_MODE: bool = Field(False)
    TEMP_DIR: str = Field("temp")

    # TinyDB
    DB_PATH: str = Field("db.json")
    DB_WINDOW_MSGS: int = Field(5)

    # QDRANT
    QDRANT_URL: str = Field("qdrant_url")
    QDRANT_KEY: str = Field("qdrant_key")
    QDRANT_COLLECTION: str = Field("qdrant_collection")
    QDRANT_BOOK_URL: str = Field("qdrant_book_url")
    QDRANT_UPLOAD_BATCH_SIZE: int = Field(200)
    QDRANT_UPLOAD_TIMEOUT: int = Field(300)
    QDRANT_MAX_RETRIES: int = Field(3)
    QDRANT_CHUNK_SIZE:int = Field(400)
    QDRANT_OVERLAP: int = Field(100)

    # LLM
    YANDEX_API_KEY: str = Field("yandex_api_key")
    YANDEX_FOLDER_ID: str = Field("yandex_api_key")
    MAX_TOKENS: int = Field(500)
    TEMPERATURE: float = Field(0.0)
    PROMPT: str = Field("llm_prompt")

    # EMBEDDINGS MODEL
    EMBEDDING_SIZE: int = Field(256)

    # RAG
    TOP_K_DOCS: int = Field(3)
    SEARCH_DISTANCE_TYPE: str = Field("similarity")


settings = Settings()