import logging

from flask import Blueprint, jsonify, request

from app.rag.generator import Generator
from app.rag.retriever import Retriever

api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)
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

    try:
        retrieved = retriever.retrieve_data(query, category=category, field=field)
        response = generator.generate_answer(retrieved, query)
        return jsonify({"response": response, "sources": retrieved})
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        return jsonify({"error": "Assistant is not configured correctly"}), 500
    except Exception as e:
        logger.exception("Error processing API query")
        return jsonify({"error": "An error occurred while processing the query"}), 500
