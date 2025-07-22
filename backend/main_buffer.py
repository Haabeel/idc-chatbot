from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
import os
import google.generativeai as genai
import numpy as np
import re
import sys
from textblob import TextBlob 


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: No API key found! Please set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file.")
    sys.exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-06-17")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
chroma_db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)

print(f"Loaded documents: {chroma_db._collection.count()}")

memory = ConversationBufferMemory(return_messages=True)
memory.chat_memory.messages[-10:]



#functions
def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def keyword_match_score(query, doc_text):
    query_words = set(re.findall(r'\w+', query.lower()))
    doc_words = set(re.findall(r'\w+', doc_text.lower()))
    return len(query_words & doc_words) / len(query_words | doc_words)

def split_query_into_subquestions(query): 
    return [q.strip() for q in re.split(r'\s*(?:and|,|\.|\?|;)\s*', query) if q.strip()]

def correct_spelling(text):  
    blob = TextBlob(text)
    return str(blob.correct())

predefined_answers = {
    "who are you": "IDC Technologies is a global leader in IT staffing and workforce solutions, delivering talent across multiple industries.",
    "what do you do": "IDC Technologies provides staffing, consulting, and project-based solutions tailored for the IT and engineering sectors.",
}


def ask_idc_chatbot(query):
    query = query.strip()
    if not query:
        return "AskIDC: Please type something."

    
    corrected_query = correct_spelling(query)
    if corrected_query.lower() != query.lower():
        print(f"[Corrected] \"{query}\" → \"{corrected_query}\"")
        query = corrected_query

    if query.lower() in predefined_answers:
        answer = predefined_answers[query.lower()]
        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(answer)
        return "AskIDC: " + answer

    subquestions = split_query_into_subquestions(query)
    if not subquestions:
        subquestions = [query]

    answers = []

    for subq in subquestions:
        top_k = chroma_db.similarity_search_with_score(subq, k=5)
        if not top_k:
            answers.append(f"For '{subq}': Sorry, I couldn’t find anything.")
            continue

        docs = [doc for doc, _ in top_k]
        doc_embeds = [embedding_model.embed_query(doc.page_content) for doc in docs]
        subq_embed = embedding_model.embed_query(subq)

        reranked = []
        for doc, emb in zip(docs, doc_embeds):
            cos_sim = cosine_similarity(subq_embed, emb)
            kw_score = keyword_match_score(subq, doc.page_content)
            final_score = (0.7 * cos_sim) + (0.3 * kw_score)
            reranked.append((doc, final_score))

        reranked.sort(key=lambda x: x[1], reverse=True)
        top_docs = [doc.page_content for doc, score in reranked[:3]]

        context_block = "\n".join([f"- {text}" for text in top_docs])

        conversation_string = "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in memory.chat_memory.messages[-10:]])

        prompt = f"""
You are AskIDC, a helpful and professional chatbot answering ONLY questions related to IDC Technologies.

Conversation so far:
{conversation_string}

Context for the current question:
{context_block}

User's current sub-question: "{subq}"

Respond clearly and concisely using ONLY the above context.
"""

        try:
            response = model.generate_content(prompt)
            answers.append(response.text.strip())
        except Exception as e:
            print(f"[Gemini error on sub-question: {subq}] -> {e}")
            answers.append(f"For '{subq}': (Gemini error) Showing top result.\n{top_docs[0]}")

    final_answer = "\n\n".join(answers)

    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(final_answer)

    return "AskIDC: " + final_answer



if __name__ == "__main__":
    print("AskIDC Chatbot is ready!")
    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(ask_idc_chatbot(user_query))
