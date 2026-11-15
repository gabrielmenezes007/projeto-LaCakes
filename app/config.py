"""Configurações da aplicação.

O banco é definido pela variável de ambiente DATABASE_URL. Sem ela, usa SQLite em instance/lacakes.db.
Exemplos:
    DATABASE_URL=postgresql://usuario:senha@localhost:5432/lacakes
    DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/lacakes
"""
import os
import pathlib
from datetime import timedelta

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def _url_banco():
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{(RAIZ / 'instance' / 'lacakes.db').as_posix()}"
    # Alguns serviços entregam "postgres://", que o SQLAlchemy não aceita mais.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "lacakes-chave-de-desenvolvimento-troque-em-producao")
    SQLALCHEMY_DATABASE_URI = _url_banco()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Segurança da sessão e dos formulários (RNF06)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    WTF_CSRF_TIME_LIMIT = None

    # Upload de fotos de produtos (máx. 2 MB)
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    PASTA_UPLOADS = RAIZ / "app" / "static" / "uploads"

    # Dados da loja
    LOJA_NOME = "LaCakes Cupcakes Gourmet"
    LOJA_ENDERECO = "Rua das Flores, 120 – Jaú/SP"
    LOJA_HORARIO = "Segunda a sábado, das 9h às 19h"


class ConfigTeste(Config):
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
