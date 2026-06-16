from flask import Blueprint, jsonify, render_template, request

from app.rag.generator import Generator
from app.rag.retriever import Retriever

web = Blueprint("web", __name__)
retriever = Retriever()
generator = Generator()


@web.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_question = request.form.get("user_message", "").strip()

        if not user_question:
            return jsonify({"response": "Please enter a valid question."})

        try:
            retrieved = retriever.retrieve_data(user_question, k=3)
            answer = generator.generate_answer(retrieved, user_question)
            return jsonify({"response": answer})
        except Exception as e:
            print(f"Error processing query: {e}")
            return jsonify({"response": "Sorry, an error occurred while processing your question."})

    return render_template("index.html")
