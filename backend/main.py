from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
import google.genai as genai
from google.genai import types


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)
model_name = "gemini-2.5-flash-lite-preview-06-17"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
chroma_db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)


def ask_idc_chatbot(query):
    query = query.strip()
    if not query:
        return "AskIDC: Please type something."

    results_with_scores = chroma_db.similarity_search_with_score(query, k=1)

    if results_with_scores:
        result, score = results_with_scores[0]
        if score < 0.7:
            return "AskIDC: Sorry, I don’t know that yet."

        # gemini prompt
        prompt_text = f"""
You are an intelligent and polite virtual assistant for IDC Technologies.

The user asked: "{query}"

You matched this internal FAQ answer:
"{result.page_content}"

Please rewrite the answer in a clear, helpful, and chatbot-friendly tone.
"""
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part(text=prompt_text)
                ],  # 1 part = 1 piece of content for gemini
            )
        ]

        # tools = [types.Tool(googleSearch=types.GoogleSearch())]

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            # tools=tools,
            response_mime_type="text/plain",
        )

        try:
            final_answer = ""
            for chunk in client.models.generate_content_stream(
                model=model_name, contents=contents, config=config
            ):
                final_answer += chunk.text
            return "AskIDC: " + final_answer.strip()
        except Exception as e:
            return f"AskIDC: (Gemini error) Showing raw answer instead.\n{result.page_content}"
    else:
        return "AskIDC: No answer found."
