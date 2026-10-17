import chromadb
from chromadb.utils import embedding_functions
# from sentence_transformers import SentenceTransformer

em_fun = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')
DBclient = chromadb.PersistentClient(path="./my_chroma_data")

def store_chuks(chunks: list, file_name,collection_name="my_embedded_chunks"):

    collection = DBclient.get_or_create_collection(name=collection_name, embedding_function=em_fun)
    
    collection.add(
        documents = chunks,
        ids = [f"{file_name}_chunk_{no}" for no in range(len(chunks))]
    )

    return len(chunks)

    
