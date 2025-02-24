import os
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Actualización según el warning
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

DATA_DIR = "data"  # carpeta donde está la info que vamos a hacer el RAG
CHROMA_DB_DIR = "chroma_db"  # Carpeta donde se guardará la base de datos vectorial

def extract_text_from_pdfs(directory):
    """Extrae el texto de todos los PDFs en una carpeta."""
    documents = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            print(f"Leyendo: {filepath}")

            pdf_reader = pypdf.PdfReader(filepath)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            documents.append(Document(page_content=text, metadata={"source": filename}))
    
    return documents

def split_text_into_chunks(documents, chunk_size=1000, chunk_overlap=100):
    """Divide los documentos en chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return text_splitter.split_documents(documents)

def store_in_chroma(chunks):
    """Guarda los chunks en una base de datos vectorial Chroma."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DB_DIR)
    vectordb.persist()
    return vectordb

if __name__ == "__main__":
    docs = extract_text_from_pdfs(DATA_DIR)
    chunks = split_text_into_chunks(docs)
    vectordb = store_in_chroma(chunks)
    print(f"\nBase de datos vectorial creada en '{CHROMA_DB_DIR}' con {len(chunks)} chunks.")