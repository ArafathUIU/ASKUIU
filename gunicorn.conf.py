import os

port = os.getenv("PORT", "10000")
bind = f"0.0.0.0:{port}"
workers = int(os.getenv("WORKERS", "1"))
threads = int(os.getenv("THREADS", "2"))
timeout = int(os.getenv("TIMEOUT", "120"))
preload_app = False
keepalive = 5
accesslog = "-"
errorlog = "-"


def on_starting(server):
    print(f"=== GUNICORN ON_STARTING: binding to {server.address} ===", flush=True)


def when_ready(server):
    print(f"=== GUNICORN WHEN_READY: listening on {server.address} ===", flush=True)

