import chromadb
from chromadb.utils import embedding_functions


DBclient = chromadb.PersistentClient(path="./my_chroma_data")
em_fun = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def relevent_chunks(query: str, top_k=3, collection_name="my_embedded_chunks"):
    collection = DBclient.get_collection(name=collection_name,
        embedding_function=em_fun
        )
    
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    print(results["documents"][0][0:top_k])
    return results["documents"][0][0:top_k]

# que = """
# Next dataset you open, close your laptop for 10 minutes first and just think — 'what is
# this data about, and what would a smart person in this field want to measure that isn't
# directly in the columns?' Write 3 ideas on paper before coding anything. Even if the
# ideas are wrong, this habit is what separates people who can engineer features from
# those who can't.
# """
# chu  = relevent_chunks(query=que)
# print(chu)
