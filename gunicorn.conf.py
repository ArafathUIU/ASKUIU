import os

env_port = os.getenv("PORT")
bind = []
if env_port:
    bind.append(f"0.0.0.0:{env_port}")
bind.extend(["0.0.0.0:10000", "0.0.0.0:5000", "0.0.0.0:8000"])
bind = list(dict.fromkeys(bind))

workers = int(os.getenv("WORKERS", "1"))
threads = int(os.getenv("THREADS", "2"))
worker_class = "gthread"
timeout = int(os.getenv("TIMEOUT", "120"))
preload_app = False
keepalive = 5
accesslog = "-"
errorlog = "-"


def on_starting(server):
    print(f"=== GUNICORN ON_STARTING: binding to {server.address} ===", flush=True)


def when_ready(server):
    print(f"=== GUNICORN WHEN_READY: listening on {server.address} ===", flush=True)

