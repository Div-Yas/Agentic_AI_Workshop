import os
from dotenv import load_dotenv
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

class Settings:
    # Google AI Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS_STR: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(',')]
    
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/payroll_db")
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "data/outputs")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # RAG Configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "data/knowledge_base/chroma_db")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Payroll Configuration
    DEFAULT_CURRENCY: str = os.getenv("DEFAULT_CURRENCY", "INR")
    DEFAULT_COUNTRY: str = os.getenv("DEFAULT_COUNTRY", "IN")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Payroll & Tax Planner"

    # MongoDB client (initialized once)
    mongo_client: AsyncIOMotorClient = None
    mongo_db = None

    def __init__(self):
        if not Settings.mongo_client:
            Settings.mongo_client = AsyncIOMotorClient(self.MONGODB_URI)
            # If a database is specified in the URI, get it; else, use 'payroll_db'
            db_name = self.MONGODB_URI.rsplit('/', 1)[-1] if '/' in self.MONGODB_URI else 'payroll_db'
            Settings.mongo_db = Settings.mongo_client.get_database(db_name)

    class Config:
        case_sensitive = True

settings = Settings() 