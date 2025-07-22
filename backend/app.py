from flask import Flask, request, jsonify
from main import ask_idc_chatbot
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests for your frontend (React)

@app.route("/")
def home():
    return "IDC Chatbot API is running."

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Missing query in request"}), 400

    user_query = data["query"]
    response = ask_idc_chatbot(user_query)

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
