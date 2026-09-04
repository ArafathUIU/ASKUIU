import os

port = os.getenv("PORT", "5000")
bind = os.getenv("BIND", f"0.0.0.0:{port}")
workers = int(os.getenv("WORKERS", "1"))
threads = int(os.getenv("THREADS", "2"))
timeout = int(os.getenv("TIMEOUT", "120"))
preload_app = False
keepalive = 5
accesslog = "-"
errorlog = "-"
