from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    firecrawl_api_key: str
    openai_api_key: str = ''
    base_url: str = 'https://openrouter.ai/api/v1'
    openai_model: str = 'openai/gpt-oss-20b:free'
    temp_dir: str = "./uploads"
    chunk_size: int = 1000
    chunk_overlap: int = 100
    collection_name: str
    use_hybrid_rag: bool = False
    retrieval_k: int = 5

    model_config = SettingsConfigDict(
        extra="ignore",
        case_sensitive=False
    )
    
settings = Settings()