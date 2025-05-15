import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
from langchain_community.document_loaders import WebBaseLoader
from classes import RagToolSchema

def initialize_rag():
    # Cargar documentos desde archivos
    def load_documents(folder_path: str) -> List[Document]:
        documents = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            else:
                continue
            documents.extend(loader.load())
        return documents

    # Cargar documentos desde links
    def load_links(links: List[str]) -> List[Document]:
        documents = []
        for link in links:
            loader = WebBaseLoader(link)
            documents.extend(loader.load())
        return documents

    # Definir los links a cargar
    links = [
        "https://www.britannica.com/place/Canada",
        "https://www.natgeokids.com/uk/discover/geography/countries/facts-about-canada/",
    ]

    # Procesar documentos de archivos y links
    file_documents = load_documents("data")
    link_documents = load_links(links)
    all_documents = file_documents + link_documents

    # Dividir documentos en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    splits = text_splitter.split_documents(all_documents)
    
    # Inicializar vectorstore
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists("./chroma_db") and os.listdir("./chroma_db"):
        return Chroma(
            collection_name="my_collection",
            persist_directory="./chroma_db",
            embedding_function=embedding_function
        )
    else:
        return Chroma.from_documents(
            collection_name="my_collection",
            documents=splits,
            embedding=embedding_function,
            persist_directory="./chroma_db"
        )

@tool(args_schema=RagToolSchema)
def retriever_tool(question):
    """Retrieve documents about FutureSmart AI"""
    vectorstore = initialize_rag()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return "\n\n".join(doc.page_content for doc in retriever.invoke(question))
