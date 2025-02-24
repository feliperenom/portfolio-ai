import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
from classes import RagToolSchema

# -- Asegúrate de usar la ruta absoluta del archivo actual:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

def load_documents(folder_path: str) -> List[Document]:
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif filename.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            # Ignora formatos que no sean PDF o DOCX
            continue
        documents.extend(loader.load())
    return documents

def initialize_rag():
    # 1) Carga tus documentos
    documents = load_documents(DATA_DIR)

    # 2) Procesamiento (Split en chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    splits = text_splitter.split_documents(documents)
    
    # 3) Embeddings
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 4) Verifica si existe la carpeta Chroma con datos previos
    if os.path.exists(CHROMA_DB_DIR) and os.listdir(CHROMA_DB_DIR):
        vectorstore = Chroma(
            collection_name="my_collection",
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embedding_function
        )
    else:
        vectorstore = Chroma.from_documents(
            collection_name="my_collection",
            documents=splits,
            embedding=embedding_function,
            persist_directory=CHROMA_DB_DIR
        )
    return vectorstore

@tool(args_schema=RagToolSchema)
def retriever_tool(question: str) -> str:
    """Retrieve documents relacionados con TinyHome (u otros temas) mediante Chroma."""
    vectorstore = initialize_rag()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 7})
    docs = retriever.invoke(question)
    
    # Si no se encuentra nada, docs será lista vacía.
    if not docs:
        return "No se encontró información relevante en los documentos."
    
    content = "\n\n".join(doc.page_content for doc in docs)
    return content
