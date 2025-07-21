import os
import google.generativeai as genai
from dotenv import load_dotenv
from embed import embed_text
import chromadb

# Load .env file for API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load model
model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")


# Connect to ChromaDB
client = chromadb.PersistentClient(path="chroma/")
collection = client.get_or_create_collection(name="faq")

def answer_question(query):
    # Embed the user's full query
    query_embedding = embed_text([query])[0]

    # Fetch top 3 relevant entries
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["metadatas", "distances", "documents"]
    )

    # Combine answers from the top results
    contexts = [meta["answer"] for meta in results["metadatas"][0]]
    context_block = "\n".join([f"- {c}" for c in contexts])

    # Prompt template (handles multiple subquestions too)
    prompt = f"""
You are an intelligent, helpful, and honest assistant trained to answer based on the provided FAQ context.

Context:
{context_block}

Now answer the following question clearly and informatively, even if it has multiple sub-parts.

Question: {query}
Answer:
"""

    # Generate answer
    response = model.generate_content(prompt)

    return {
        "answer": response.text.strip(),
        "source": results["documents"][0],
        "score": results["distances"][0]
    }