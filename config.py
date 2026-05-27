from dotenv import load_dotenv
import os

load_dotenv(override=True)

class Config:

    # =========================
    # API KEYS
    # =========================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "dermaflow")

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI")

    # =========================
    # MODELS
    # =========================
    LLM_MODEL = "gemini-2.5-flash"

    EMBEDDING_MODEL = "models/gemini-embedding-2"

    EMBEDDING_DIMENSION = 768

    # =========================
    # RAG SETTINGS
    # =========================
    CHUNK_SIZE = 300

    CHUNK_OVERLAP = 60

    SEPARATORS = [
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]

    TOP_K_RETRIEVE = 5

    CONFIDENCE_THRESHOLD = 0.45

    # =========================
    # PATHS
    # =========================
    RAW_PDF_DIR = "data/raw/pdfs"

    INGREDIENTS_FILE = "data/raw/ingredients.json"

    SESSIONS_DIR = "memory/sessions"
    UPLOAD_DIR = "data/uploads"


config = Config()