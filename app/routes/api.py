from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.tasks.audio_tasks import process_audio
from app.rag.retriever import Retriever
from app.rag.generator import generate_answer
import os

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'webm', 'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    file = request.files['audio']
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    filename = secure_filename(file.filename)
    audio_path = f"audio_temp/{filename}"
    file.save(audio_path)
    task = process_audio.delay(audio_path)
    return jsonify({"task_id": task.id})

@api_bp.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = data.get('query')
    if not query_text:
        return jsonify({"error": "No query provided"}), 400
    retriever = Retriever()
    docs = retriever.search(query_text)
    answer = generate_answer(docs, query_text)
    return jsonify({"answer": answer, "sources": [doc.metadata for doc in docs]})