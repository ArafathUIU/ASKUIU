# from flask import Blueprint, request, jsonify
# from werkzeug.utils import secure_filename
# from app.tasks.audio_tasks import process_audio
# from app.rag.retriever import Retriever
# from app.rag.generator import generate_answer
# import os

# api_bp = Blueprint('api', __name__)

# ALLOWED_EXTENSIONS = {'webm', 'wav', 'mp3'}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @api_bp.route('/speech-to-text', methods=['POST'])
# def speech_to_text():
#     if 'audio' not in request.files:
#         return jsonify({"error": "No audio file provided"}), 400
#     file = request.files['audio']
#     if not file or not allowed_file(file.filename):
#         return jsonify({"error": "Invalid file type"}), 400
#     filename = secure_filename(file.filename)
#     audio_path = f"audio_temp/{filename}"
#     file.save(audio_path)
#     task = process_audio.delay(audio_path)
#     return jsonify({"task_id": task.id})

# @api_bp.route('/query', methods=['POST'])
# def query():
#     data = request.get_json()
#     query_text = data.get('query')
#     if not query_text:
#         return jsonify({"error": "No query provided"}), 400
#     retriever = Retriever()
#     docs = retriever.search(query_text)
#     answer = generate_answer(docs, query_text)
#     return jsonify({"answer": answer, "sources": [doc.metadata for doc in docs]})


# C:\xampp\htdocs\AskUIU\ASKUIU\app\routes\api.py
from flask import Blueprint, request, jsonify
from app.rag.retriever import Retriever
from app.rag.generator import Generator

api = Blueprint('api', __name__)
retriever = Retriever()
generator = Generator()

@api.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get('query', '')
    category = data.get('category', None)
    field = data.get('field', None)
    retrieved = retriever.retrieve_data(query, category=category, field=field)
    response = generator.generate_answer(retrieved, query)
    return jsonify({'response': response})