# router/upload_router.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from utils.upload_utils import load_file, clean_data, splitted_data
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from services.pinecone_services import index_creation
from services.namespace_creation import generate_namespace
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Load API key from env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise RuntimeError("Missing required API keys. Please check your .env file.")

router = APIRouter(tags=["Upload"])

@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    index_name = "main"  # <-- Always use "main" index
    try:
        # Auto-generate namespace from file name
        namespace = generate_namespace(file.filename)

        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[-1] or ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Load and process the file
        pages = load_file(tmp_path)
        clean_pages = clean_data(pages)
        doc_list = splitted_data(clean_pages)

        # Embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )

        # Ensure Pinecone index exists
        index = index_creation(index_name=index_name, dimension=1536)

        # Store chunks into Pinecone
        vectorstore = PineconeVectorStore.from_documents(
            documents=doc_list,
            embedding=embeddings,
            index_name=index_name,
            namespace=namespace
        )

        return {
            "success": True,
            "filename": file.filename,
            "namespace": namespace,
            "num_pages": len(clean_pages),
            "num_chunks": len(doc_list),
            "status": f"Inserted into Pinecone index '{index_name}' under namespace '{namespace}'"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
