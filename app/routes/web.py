import logging

from flask import Blueprint, jsonify, render_template, request

from app.rag.service import generator, retriever

web = Blueprint("web", __name__)
logger = logging.getLogger(__name__)


@web.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Support both form-urlencoded and JSON requests
        if request.is_json:
            data = request.get_json(silent=True) or {}
            user_question = data.get("user_message") or data.get("query", "")
            category = data.get("category")
        else:
            user_question = request.form.get("user_message", "")
            category = request.form.get("category")

        user_question = (user_question or "").strip()

        if not user_question:
            return jsonify({"response": "Please enter a valid question.", "sources": []})

        try:
            retrieved = retriever.retrieve_data(user_question, category=category, k=3)
            answer = generator.generate_answer(retrieved, user_question)
            return jsonify({
                "response": answer,
                "sources": retrieved,
                "provider": generator.active_provider,
            })
        except ValueError as e:
            logger.error("Configuration error: %s", e)
            return jsonify({
                "response": "Sorry, the assistant is not configured correctly.",
                "sources": [],
            })
        except Exception as e:
            logger.exception("Error processing web query")
            return jsonify({
                "response": "Sorry, an error occurred while processing your question.",
                "sources": [],
            })

    from app.rag.service import is_retriever_ready
    if is_retriever_ready():
        try:
            stats = retriever.get_stats()
        except Exception:
            stats = {"total_documents": 127}
    else:
        stats = {"total_documents": 127}

    active_provider = getattr(generator, "active_provider", "groq")
    return render_template("index.html", stats=stats, active_provider=active_provider)

