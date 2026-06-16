from flask import Blueprint, request, jsonify

from app.rag.retriever import Retriever
from app.rag.generator import Generator

api = Blueprint("api", __name__)
retriever = Retriever()
generator = Generator()


@api.route("/query", methods=["POST"])
def handle_query():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    category = data.get("category")
    field = data.get("field")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    retrieved = retriever.retrieve_data(query, category=category, field=field)
    response = generator.generate_answer(retrieved, query)
    return jsonify({"response": response, "sources": retrieved})
