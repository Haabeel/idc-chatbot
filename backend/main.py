from dotenv import load_dotenv
import os
import google.genai as genai
from google.genai import types
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini Client
client = genai.Client(api_key=api_key)
model_name = "gemini-2.5-flash-lite-preview-06-17"

# Initialize embedding model and Chroma DB
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
chroma_db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_model
)

print(f"Loaded documents: {chroma_db._collection.count()}")

# Main chatbot logic
def ask_idc_chatbot(query):
    query = query.strip()
    if not query:
        return "AskIDC: Please type something."

    # Get top match
    results_with_scores = chroma_db.similarity_search_with_score(query, k=1)
    if not results_with_scores:
        return "AskIDC: No answer found."

    result, score = results_with_scores[0]
    print(f"🔍 Matched doc (score={score:.3f}): {result.page_content[:100]}...")

    # Show top 3 matches for client-related queries
    if "client" in query.lower() or "customer" in query.lower():
        print("DEBUG: Top 3 client-related matches:")
        matches = chroma_db.similarity_search_with_score(query, k=3)
        for doc, sc in matches:
            print(f"  - Score: {sc:.3f}, Snippet: {doc.page_content[:150]}...")

    # Reject low-quality matches
    if score < 0.7:
        return "AskIDC: Sorry, I don’t know that yet."

    # Rephrase using Gemini
    prompt_text = f"""
You are an intelligent and polite virtual assistant for IDC Technologies.

The user asked: "{query}"

You matched this internal FAQ answer:
"{result.page_content}"

Please rewrite the answer in a clear, helpful, and chatbot-friendly tone.
"""

    contents = [
        types.Content(role="user", parts=[types.Part(text=prompt_text)])
    ]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="text/plain"
    )

    try:
        final_answer = ""
        for chunk in client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config
        ):
            final_answer += chunk.text
        return "AskIDC: " + final_answer.strip()

    except Exception as e:
        print(f"Gemini error: {e}")
        return f"AskIDC: (Gemini error) Showing raw answer instead.\n{result.page_content}"


# Run in loop
if __name__ == "__main__":
    print("AskIDC Chatbot is running. Type your query or 'exit' to quit.")
    while True:
        try:
            user_query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n Goodbye!")
            break

        if user_query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        response = ask_idc_chatbot(user_query)
        print(response)
