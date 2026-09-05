import logging
import os
import socket

from app import create_app

app = create_app()


def find_available_port(preferred_port=5050):
    candidates = [preferred_port, 5000, 8000, 8080, 5500]
    for p in candidates:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            continue
    return preferred_port


if __name__ == "__main__":
    env_port = os.getenv("PORT")
    port = int(env_port) if env_port else 5000
    host = "0.0.0.0"
    print(f"=== ASKUIU Intelligence System running on http://{host}:{port} ===", flush=True)
    app.run(host=host, port=port, debug=False, use_reloader=False)

