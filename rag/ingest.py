import time
import json
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from config import config
from rag.vectordb import get_index
import json
import time




# Configure Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

# Get the configured index
index = get_index()

# Splitting chunk size to better align with headings/paragraphs
# We use slightly larger chunks or rely heavily on \n\n to capture whole sections
splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
    length_function=len,
    add_start_index =True
)

def clean_text(text: str) -> str:
    """Remove common PDF artifacts from clinical documents."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        line = line.strip()
        # skip page numbers, headers, footers common in these PDFs
        if not line:
            continue
        if line.startswith("Page ") and "of" in line:
            continue
        if "www." in line and len(line) < 60:
            continue
        if line.startswith("©"):
            continue
        if "Registered Charity" in line:
            continue
        if "PATIENT INFORMATION LEAFLET |" in line:
            continue
        cleaned.append(line)
    return "\n".join(cleaned)

def extract_pdf_langchain(filepath: str) -> str:
    """Extract text using Langchain's PyPDFLoader"""
    loader = PyPDFLoader(filepath)
    pages = loader.load()
    
    # Combine page content from all loaded Document objects
    full_text = "\n\n".join([page.page_content for page in pages])
    return full_text

def embed(texts: list[str]) -> list[list[float]]:
    # Using Gemini for embeddings
    response = genai.embed_content(
        model=config.EMBEDDING_MODEL,
        content=texts,
        task_type="retrieval_document",
        output_dimensionality=config.EMBEDDING_DIMENSION
    )
    # The response dict contains 'embedding' which is a list of lists of floats
    return response['embedding']

## ingest pdf
def normalize_condition_name(filename: str) -> str:

    return (
        filename.lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

def ingest_pdf(filepath: str):

    path = Path(filepath)

    condition = normalize_condition_name(path.stem)

    print(f"\n{'=' * 50}")
    print(f"Processing: {path.name}")
    print(f"Condition: {condition}")
   
    # Use LangChain's loader
    raw = extract_pdf_langchain(str(path))
    
    cleaned = clean_text(raw)

    # Split using the configured splitter
    chunks = splitter.split_text(cleaned)
    
    
    
    print(f"Raw chars: {len(raw)} | After cleaning: {len(cleaned)}")
    print(f"chunk size config: {config.CHUNK_SIZE} chars with {config.CHUNK_OVERLAP} overlap")
    print(f"Chunks created: {len(chunks)}")

    # IMPORTANT — verify chunk quality before proceeding
    print(f"\nFirst 3 chunks:")
    for i, c in enumerate(chunks[:3]):
        print(f"\n[{i}] length={len(c)}")
        print(c)
        print("-" * 40)

    # Automatically proceed instead of waiting for input
    confirm = 'y'

    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = embed([chunk])[0]
        vectors.append({
            "id": f"{condition}_{i}",
            "values": embedding,
            "metadata": {
                "text": chunk,
                "condition": condition,
                "source": path.name,
                "chunk_index": i,
                
            }
        })
        time.sleep(0.1)

    # upsert in batches of 50
    for i in range(0, len(vectors), 50):
        batch = vectors[i:i+50]
        index.upsert(vectors=batch)
        print(f"  Upserted batch {i//50 + 1}/{(len(vectors)-1)//50 + 1}")

    print(f"Done: {len(vectors)} vectors for '{condition}' ✓")

def ingest_ingredients():

    print(f"\n{'=' * 50}")
    print("Processing: ingredients.json")

    # load JSON file
    with open(config.INGREDIENTS_FILE, "r") as f:
        ingredients = json.load(f)

    print(f"Found {len(ingredients)} ingredients")

    vectors = []

    # loop through every ingredient
    for i, ing in enumerate(ingredients):

        lines = []

        # loop through every field inside ingredient
        for key, value in ing.items():

            # skip empty values
            if not value:
                continue

            # convert key nicely
            # avoid_with -> Avoid With
            label = key.replace("_", " ").title()

            # if value is list convert to readable string
            if isinstance(value, list):
                value = ", ".join(value)

            # create formatted line
            lines.append(f"{label}: {value}")

        # combine all lines into final text
        text = "\n".join(lines)

        print("\nGenerated Text:")
        print(text)

        # create embedding
        embedding = embed([text])[0]

        # store vector
        vectors.append({
            "id": f"ingredient_{i}",

            "values": embedding,

            "metadata": {
                "text": text,
                "ingredient_name": ing.get("name", ""),
                "source": "ingredients.json",
                "type": "ingredient"
            }
        })

        print(f"\nEmbedded: {ing.get('name', '')}")

        time.sleep(0.1)

    # upload vectors in batches
    for i in range(0, len(vectors), 50):

        index.upsert(
            vectors=vectors[i:i + 50]
        )

    print(f"\nDone: {len(vectors)} ingredients indexed ✓")


if __name__ == "__main__":
    pdf_dir = Path(config.RAW_PDF_DIR)
    pdfs = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs: {[p.name for p in pdfs]}")

    for pdf in pdfs:
        ingest_pdf(str(pdf))

    ingest_ingredients()
    print("\n✓ All ingestion complete")
