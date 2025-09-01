# PDF Chatbot with RAG and LangSmith Tracing

A FastAPI and Streamlit-based application for uploading PDFs, storing their content in Pinecone, and querying them using Retrieval-Augmented Generation (RAG) with OpenAI embeddings and LangSmith tracing.

## Features
- **PDF Upload**: Upload a single PDF via a Streamlit UI, processed and stored in Pinecone.
- **Chat Interface**: Query the PDF content in a ChatGPT-like interface (queries on the right, answers on the left).
- **RAG Pipeline**: Uses OpenAI embeddings and GPT-4o-mini for context-aware answers.
- **LangSmith Tracing**: Tracks embedding and RAG operations for debugging and performance monitoring.
- **Single Upload**: Ensures only one PDF is uploaded per session.
- **Pinecone Integration**: Stores PDF chunks in a Pinecone index under a unique namespace.

## Prerequisites
- Python 3.8+
- Pinecone account and API key
- OpenAI API key
- LangSmith API key
- Required packages:
  ```bash
  pip install fastapi uvicorn streamlit python-dotenv pinecone-client langchain langchain-openai langchain-community langsmith openai requests PyPDF2
  ```

## Project Structure
```
project/
├── main.py                  # FastAPI app entry point
├── router/
│   ├── upload_router.py     # Handles PDF uploads
│   ├── retrieve_router.py   # Handles RAG queries with LangSmith tracing
├── utils/
│   ├── upload_utils.py      # PDF loading, cleaning, and splitting
│   ├── pinecone_services.py # Pinecone index creation
│   ├── namespace_creation.py# Generates unique namespaces
├── streamlit_app.py         # Streamlit UI for PDF upload and chat
├── .env                     # Environment variables
├── README.md                # This file
```

## Setup
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create `.env` File**:
   In the project root, create a `.env` file with:
   ```
   PINECONE_API_KEY=your_pinecone_api_key
   OPENAI_API_KEY=your_openai_api_key
   LANGSMITH_API_KEY=langsmith-api-key
   LANGSMITH_TRACING=true
   LANGSMITH_ENDPOINT=https://api.smith.langchain.com
   LANGSMITH_PROJECT=pr-tart-simple-92
   API_URL=http://localhost:8000
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run FastAPI Server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Run Streamlit App**:
   In a separate terminal:
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage
1. **Access Streamlit UI**:
   Open `http://localhost:8501` in your browser.

2. **Upload PDF**:
   - In the sidebar, select a PDF file and click "Upload PDF".
   - A unique namespace is generated, and the PDF content is stored in Pinecone.
   - The UI displays a success message with the namespace.

3. **Query the PDF**:
   - Enter a question in the chat input box (right column).
   - The system retrieves relevant chunks from Pinecone (top_k=5) and generates an answer using GPT-4o-mini.
   - Answers appear in the left column, queries in the right.

4. **Monitor with LangSmith**:
   - View tracing data (embeddings, RAG pipeline) at `https://smith.langchain.com` under project `pr-tart-simple-92`.

## Testing
- **Test Upload Endpoint**:
  ```bash
  curl -X POST http://localhost:8000/uploadfile/ -F "file=@/path/to/sample.pdf"
  ```
- **Test Query Endpoint**:
  ```bash
  curl -X POST http://localhost:8000/rag-search -H "Content-Type: application/json" -d '{"namespace":"your-namespace","query":"What is the main topic?","top_k":5}'
  ```

## Troubleshooting
- **404 Not Found**: Ensure FastAPI is running on `http://localhost:8000` and `API_URL` in `.env` matches.
- **API Key Errors**: Verify Pinecone, OpenAI, and LangSmith API keys in `.env`.
- **CORS Issues**: Confirm CORS middleware is configured in `main.py`.
- **Pinecone Issues**: Check index `main` exists and dimension matches (1536).

## License
MIT License
