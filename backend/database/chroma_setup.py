import pandas as pd
import uuid
import chromadb
from chromadb import PersistentClient

client = PersistentClient("my_chroma_db")
collection = client.get_or_create_collection("my_collection")

def setup_chroma_if_needed():
    df = pd.read_csv("my_portfolio.csv")
    if not collection.count():
        for _, row in df.iterrows():
            collection.add(
    documents=[row["Techstack"]],  # ✅ wrap in list
    metadatas={"links": row["Links"]},
    ids=[str(uuid.uuid4())],
)


def get_top_links(skills: list[str], n_results=2):
    print(skills)
    if not skills:
        raise ValueError("No skills provided to query Chroma.")
    
    collection = collection = client.get_or_create_collection("my_collection")
 # however you're getting your collection
    results = collection.query(query_texts=skills, n_results=n_results)
    
    return results.get("metadatas", [])
