import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"=== WSGI Server listening on 0.0.0.0:{port} ===", flush=True)
    app.run(host="0.0.0.0", port=port)
