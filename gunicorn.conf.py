import os

bind = os.getenv("BIND", "0.0.0.0:5000")
workers = int(os.getenv("WORKERS", "2"))
timeout = int(os.getenv("TIMEOUT", "120"))
accesslog = "-"
errorlog = "-"
