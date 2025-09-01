from fastapi import APIRouter
from pydantic import BaseModel
from pinecone import Pinecone
import os

from openai import OpenAI
from langsmith.wrappers import wrap_openai # New: LangSmith wrapper for OpenAI
from langsmith import traceable          # New: Decorator for tracing functions
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -----------------------
# Set LangSmith environment variables
# These must be set for the @traceable decorator to work.
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = "Lansmith api key"
os.environ["LANGSMITH_PROJECT"] = "2"
# -----------------------

# Load OpenAI and Pinecone API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Embeddings client (now wrapped for tracing)
embed_client = wrap_openai(OpenAI(api_key=OPENAI_API_KEY))

# LangChain components
chat_model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Use LCEL for a clearer RAG chain structure
prompt_template = ChatPromptTemplate.from_template(
    """Answer the question based only on the following context:
{context}

Question: {query}"""
)
rag_chain = prompt_template | chat_model | StrOutputParser()

# Router object
router = APIRouter(tags=["Retrieve"])

# Request schema
class QueryRequest(BaseModel):
    namespace: str
    query: str
    top_k: int = 5

# Trace the entire function execution
@router.post("/rag-search")
@traceable
def rag_search(request: QueryRequest):
    # 1. Encode query using LangSmith-wrapped OpenAI embeddings
    embed = embed_client.embeddings.create(
        model="text-embedding-3-small",
        input=request.query
    )
    query_vector = embed.data[0].embedding

    # 2. Connect to Pinecone index
    index = pc.Index("main")

    # 3. Search Pinecone
    results = index.query(
        namespace=request.namespace,
        vector=query_vector,
        top_k=request.top_k,
        include_metadata=True
    )

    # 4. Collect retrieved text chunks
    retrieved_chunks = [
        match["metadata"].get("text", "")
        for match in results["matches"]
    ]
    context = "\n".join(retrieved_chunks)

    # 5. Use the LCEL chain (traced automatically)
    final_answer = rag_chain.invoke({
        "query": request.query,
        "context": context
    })

    return {
        "query": request.query,
        "namespace": request.namespace,
        "answer": final_answer
    }

