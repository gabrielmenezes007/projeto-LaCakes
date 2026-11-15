"""Testes do projeto físico: o script SQL versionado precisa criar exatamente as tabelas dos models."""
import pathlib
import sqlite3

from app.extensions import db
from app.seed import CONTAS, PRODUTOS, popular

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def test_schema_sqlite_cria_as_mesmas_tabelas_dos_models(app):
    conexao = sqlite3.connect(":memory:")
    conexao.executescript((RAIZ / "database" / "schema_sqlite.sql").read_text(encoding="utf-8"))
    tabelas_sql = {r[0] for r in conexao.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert tabelas_sql == set(db.metadata.tables)
    for nome, tabela in db.metadata.tables.items():
        colunas_sql = {r[1] for r in conexao.execute(f"PRAGMA table_info({nome})")}
        assert colunas_sql == {c.name for c in tabela.columns}, nome


def test_schema_sqlite_respeita_restricoes(app):
    conexao = sqlite3.connect(":memory:")
    conexao.executescript((RAIZ / "database" / "schema_sqlite.sql").read_text(encoding="utf-8"))
    conexao.execute("INSERT INTO categoria (id, nome) VALUES (1, 'Clássicos')")
    try:
        conexao.execute("INSERT INTO produto (categoria_id, nome, preco_centavos, estoque, ativo, criado_em) "
                        "VALUES (1, 'Caro', 50000, 1, 1, '2026-11-15')")
        assert False, "o CHECK de preço deveria impedir"
    except sqlite3.IntegrityError:
        pass


def test_seed_e_idempotente(app):
    assert "já tem dados" in popular()
    assert db.session.scalar(db.select(db.func.count()).select_from(db.metadata.tables["usuario"])) == len(CONTAS)
    assert db.session.scalar(db.select(db.func.count()).select_from(db.metadata.tables["produto"])) == len(PRODUTOS)
