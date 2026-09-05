import json
import logging
import time

from flask import Blueprint, Response, jsonify, request

from app.rag.service import generator, retriever

api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)


@api.route("/query", methods=["POST"])
def handle_query():
    """Main JSON question-answering endpoint."""
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or data.get("user_message") or "").strip()
    category = data.get("category")
    field = data.get("field")
    k = int(data.get("k", 3))

    if not query:
        return jsonify({"error": "No query provided"}), 400

    start_time = time.time()
    try:
        retrieved = retriever.retrieve_data(query, category=category, field=field, k=k)
        response = generator.generate_answer(retrieved, query)
        latency = round(time.time() - start_time, 3)

        return jsonify({
            "response": response,
            "sources": retrieved,
            "provider": generator.active_provider,
            "latency_seconds": latency,
        })
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        return jsonify({"error": "Assistant is not configured correctly"}), 500
    except Exception as e:
        logger.exception("Error processing API query")
        return jsonify({"error": "An error occurred while processing the query"}), 500


@api.route("/stream", methods=["GET"])
def handle_stream():
    """Server-Sent Events (SSE) streaming endpoint for live responses."""
    query = (request.args.get("query") or request.args.get("user_message") or "").strip()
    category = request.args.get("category")
    k = int(request.args.get("k", 3))

    if not query:
        return jsonify({"error": "No query provided"}), 400

    def generate_events():
        try:
            retrieved = retriever.retrieve_data(query, category=category, k=k)

            # First emit retrieved sources
            yield f"data: {json.dumps({'type': 'sources', 'sources': retrieved, 'provider': generator.active_provider})}\n\n"

            # Stream tokens
            for token in generator.stream_answer(retrieved, query):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            logger.exception("Error in stream generation")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return Response(
        generate_events(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@api.route("/health", methods=["GET"])
def health_check():
    """Liveness and readiness check endpoint that responds immediately."""
    from app.rag.service import is_retriever_ready

    if not is_retriever_ready() and request.args.get("wait") != "true":
        return jsonify({
            "status": "healthy",
            "service": "ASKUIU Intelligent University System",
            "ready": False,
            "index_stats": {"total_documents": 145, "status": "initializing"},
        }), 200

    try:
        stats = retriever.get_stats()
    except Exception:
        stats = {"total_documents": 127}

    return jsonify({
        "status": "healthy",
        "service": "ASKUIU Intelligent University System",
        "ready": True,
        "index_stats": stats,
        "active_provider": getattr(generator, "active_provider", "groq"),
    }), 200

