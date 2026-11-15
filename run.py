"""Ponto de entrada: python run.py e abra http://127.0.0.1:5000"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    porta = int(os.environ.get("PORTA", "5000"))
    print(f"\n  LaCakes rodando em http://127.0.0.1:{porta}  (Ctrl+C para parar)\n")
    app.run(host="127.0.0.1", port=porta, debug=os.environ.get("FLASK_DEBUG") == "1")
