from pinecone import Pinecone, ServerlessSpec
from config import config

# Initialize Pinecone client
pc = Pinecone(api_key=config.PINECONE_API_KEY)

def get_index():
    """Initialize and return the Pinecone index."""
    # create index if it doesn't exist
    existing = [i.name for i in pc.list_indexes()]
    if config.PINECONE_INDEX_NAME not in existing:
        pc.create_index(
            name=config.PINECONE_INDEX_NAME,
            dimension=768,  # Gemini embeddings are 768 dimensions
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(config.PINECONE_INDEX_NAME)

# Get the configured index
index = get_index()
