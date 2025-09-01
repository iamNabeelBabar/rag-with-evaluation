import streamlit as st
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:4545")

# Streamlit page configuration
st.set_page_config(page_title="PDF Chatbot", layout="wide")

# Initialize session state
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}  # key: namespace, value: list of messages
if "namespaces" not in st.session_state:
    st.session_state.namespaces = []  # list of uploaded PDF namespaces
if "current_namespace" not in st.session_state:
    st.session_state.current_namespace = None

# Sidebar for PDF upload
with st.sidebar:
    st.header("📂 Upload PDF")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file and st.button("Upload PDF"):
        with st.spinner("Uploading PDF..."):
            files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            response = requests.post(f"{API_URL}/uploadfile/", files=files)

            if response.status_code == 200:
                result = response.json()
                namespace = result["namespace"]

                # Save namespace
                st.session_state.namespaces.append(namespace)
                st.session_state.current_namespace = namespace

                # Initialize chat history for this namespace
                if namespace not in st.session_state.chat_histories:
                    st.session_state.chat_histories[namespace] = []

                st.success(f"✅ PDF uploaded successfully! Namespace: {namespace}")
            else:
                st.error(f"❌ Upload failed: {response.json().get('detail', 'Unknown error')}")

    # Select which uploaded PDF to chat with
    if st.session_state.namespaces:
        st.subheader("📝 Select PDF to Chat")
        selected_ns = st.selectbox(
            "Choose PDF",
            options=st.session_state.namespaces,
            index=st.session_state.namespaces.index(st.session_state.current_namespace)
            if st.session_state.current_namespace in st.session_state.namespaces else 0
        )
        st.session_state.current_namespace = selected_ns

# Main chatbot interface
st.title("💬 PDF Chatbot")

current_ns = st.session_state.current_namespace
if current_ns:
    # Display chat history for current namespace
    for chat in st.session_state.chat_histories.get(current_ns, []):
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # User input
    query = st.chat_input("Ask a question about the selected PDF...")
    if query:
        # Save user message
        st.session_state.chat_histories[current_ns].append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Assistant response placeholder
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("⏳ Thinking...")

        # Send request to backend
        payload = {"namespace": current_ns, "query": query, "top_k": 5}
        try:
            response = requests.post(f"{API_URL}/rag-search", json=payload)

            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "⚠️ No answer found.")

                # Update chat history
                st.session_state.chat_histories[current_ns].append({"role": "assistant", "content": answer})

                # Show answer
                message_placeholder.markdown(answer)
            else:
                error_msg = f"❌ Query failed: {response.json().get('detail', 'Unknown error')}"
                message_placeholder.markdown(error_msg)
        except Exception as e:
            message_placeholder.markdown(f"❌ Connection error: {str(e)}")
else:
    st.warning("📂 Please upload a PDF first to start chatting.")
