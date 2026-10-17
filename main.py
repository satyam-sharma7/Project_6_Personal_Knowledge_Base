from openai import OpenAI
from dotenv import load_dotenv
import argparse
import os

from functions.doc_extractor import extracted_content
from functions.chunker import recursive_split
from functions.store_embedding import store_chuks
from functions.chunk_retriever import relevent_chunks

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest="command")

ingest_parser = subparser.add_parser("ingest")
ingest_parser.add_argument("--docs", required=True)

query_parser = subparser.add_parser("query")
query_parser.add_argument("question")   # position argument

args = parser.parse_args()


def store(path_addr: str):
    contents = extracted_content(path_addr)
    total_chunks = 0
    for i,key in enumerate(contents.keys()):
        text = contents[key]
        chunked_text = recursive_split(text)
        total_chunks += store_chuks(chunked_text, file_name=key)
    
    print(f"Ingested {total_chunks+1} chunks from {i+1} documents")

def retrieve(query: str):
    load_dotenv()

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/",
        api_key=os.getenv("GOOGLE_AI_STUDIO")
    )

    while True:
        print(query)
        retrieved_chunks = ""            # final retrieved chunks
        chunks = relevent_chunks(query, top_k=1)
        for chunk in chunks:
            retrieved_chunks += chunk
        
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages= [
                {"role":"system", "content":"You have been provided with a text_content and a query try to answer the query using text_content"},
                {
                    "role":"user", "content":
                    f"""
                    text_content:{retrieved_chunks}\n\n
                    query: {query}
                    """
                }
            ],
            stream=True
        )

        print("\n\033[92mBot:\033[0m ", end="", flush=True)  # green "Bot:" label
        for reply_chunk in response:
            piece = reply_chunk.choices[0].delta.content
            if piece != None:
                print(piece, end="", flush=True)
        
        query = input("\n\n\033[31mAsk another question: \033[0m")
        if query == "quit":
            break


if args.command == "ingest":
    store(args.docs)
elif args.command == "query":
    retrieve(args.question)

