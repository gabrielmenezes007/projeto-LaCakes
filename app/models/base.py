"""Utilitários comuns aos models."""
from datetime import datetime

from app.extensions import db


def agora():
    """Data e hora local, sem fuso (a loja atende uma única cidade)."""
    return datetime.now().replace(microsecond=0)


def coluna_enum(enum_cls, nome_restricao):
    """Enum gravado como texto (VARCHAR) com restrição CHECK, portável entre SQLite, PostgreSQL e MySQL."""
    return db.Enum(enum_cls, native_enum=False, create_constraint=True, validate_strings=True,
                   length=max(len(m.value) for m in enum_cls), name=nome_restricao)
