from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DB_DIR = "chroma_db"  # Carpeta donde se guarda la base de datos vectorial

def retrieve_documents(query, k=7):
    """Recupera documentos relevantes desde ChromaDB."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)

    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(query)
    
    if not docs:
        return "No se encontró información relevante en los documentos."
    
    content = "\n\n".join(doc.page_content for doc in docs)
    return content

if __name__ == "__main__":
    query = input("Ingrese su consulta: ")
    print("\nResultados:")
    print(retrieve_documents(query))
