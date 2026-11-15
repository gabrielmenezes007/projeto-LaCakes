"""Gera a documentação do banco a partir dos models (fonte única):

- database/schema_sqlite.sql        projeto físico para SQLite (banco padrão)
- database/schema_postgresql.sql    projeto físico para PostgreSQL (com COMMENT ON)
- database/dicionario-de-dados.md   dicionário de dados
- docs/desenvolvimento/diagramas/modelo-logico.mmd  diagrama ER lógico (Mermaid)

Uso: python scripts/gerar_docs_banco.py
"""
import pathlib
import sys

from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateIndex, CreateTable

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from app import create_app  # noqa: E402
from app.config import ConfigTeste  # noqa: E402
from app.extensions import db  # noqa: E402

CABECALHO = """-- =====================================================================
-- LaCakes Cupcakes Gourmet – projeto físico do banco de dados ({nome})
-- Gerado automaticamente a partir dos models SQLAlchemy por
-- scripts/gerar_docs_banco.py. Não edite à mão: altere os models e gere de novo.
-- Valores em dinheiro são guardados em centavos (INTEGER).
-- =====================================================================
"""

DESCRICAO_TABELAS = {
    "usuario": "Pessoas cadastradas (clientes e administradores).",
    "categoria": "Categorias da vitrine (Clássicos, Recheados, Zero açúcar, Datas especiais).",
    "produto": "Cupcakes vendidos, com preço e estoque do dia.",
    "pedido": "Pedidos dos clientes, com modalidade, endereço de entrega e totais.",
    "item_pedido": "Itens de cada pedido, com o preço congelado no momento da compra.",
    "pagamento": "Tentativas de pagamento (simulado) de cada pedido.",
    "historico_status": "Linha do tempo das mudanças de status de cada pedido.",
}


def ddl(dialeto, nome):
    linhas = [CABECALHO.format(nome=nome)]
    for tabela in db.metadata.sorted_tables:
        linhas.append(f"-- {tabela.name}: {DESCRICAO_TABELAS.get(tabela.name, '')}")
        linhas.append(str(CreateTable(tabela).compile(dialect=dialeto)).strip() + ";\n")
        for indice in sorted(tabela.indexes, key=lambda i: i.name):
            linhas.append(str(CreateIndex(indice).compile(dialect=dialeto)).strip() + ";")
        if tabela.indexes:
            linhas.append("")
        if isinstance(dialeto, postgresql.dialect):
            linhas.append(f"COMMENT ON TABLE {tabela.name} IS '{DESCRICAO_TABELAS.get(tabela.name, '')}';")
            for coluna in tabela.columns:
                if coluna.comment:
                    texto = coluna.comment.replace("'", "''")
                    linhas.append(f"COMMENT ON COLUMN {tabela.name}.{coluna.name} IS '{texto}';")
            linhas.append("")
    return "\n".join(linhas) + "\n"


def tipo_legivel(coluna):
    tipo = coluna.type
    nome = type(tipo).__name__.upper()
    if nome == "ENUM":
        return f"VARCHAR({tipo.length})"
    if nome == "STRING":
        return f"VARCHAR({tipo.length})"
    return {"INTEGER": "INTEGER", "TEXT": "TEXT", "BOOLEAN": "BOOLEAN", "DATETIME": "DATETIME"}.get(nome, nome)


def restricoes_da_coluna(tabela, coluna):
    itens = []
    if coluna.primary_key:
        itens.append("PK")
    for fk in coluna.foreign_keys:
        itens.append(f"FK → {fk.target_fullname}")
    if coluna.unique:
        itens.append("UNIQUE")
    if coluna.index and not coluna.unique:
        itens.append("índice")
    if type(coluna.type).__name__ == "Enum":
        itens.append("CHECK: " + ", ".join(coluna.type.enums))
    for ck in tabela.constraints:
        texto = str(getattr(ck, "sqltext", ""))
        if texto and coluna.name in texto and type(ck).__name__ == "CheckConstraint" and ck.name and \
                not ck.name.startswith(("ck_usuario_perfil", "ck_pedido_status", "ck_pedido_modalidade",
                                        "ck_historico_status", "ck_pagamento_metodo", "ck_pagamento_status")):
            itens.append(f"CHECK: {texto}")
    return "; ".join(itens)


def dicionario():
    linhas = ["# Dicionário de dados – LaCakes Cupcakes Gourmet", "",
              "Gerado automaticamente a partir dos models (`scripts/gerar_docs_banco.py`). "
              "Valores em dinheiro ficam em **centavos** (inteiro) para evitar erros de arredondamento.", ""]
    for tabela in db.metadata.sorted_tables:
        linhas += [f"## Tabela `{tabela.name}`", "", DESCRICAO_TABELAS.get(tabela.name, ""), "",
                   "| Coluna | Tipo | Nulo? | Padrão | Restrições | Descrição |", "|---|---|---|---|---|---|"]
        for c in tabela.columns:
            padrao = ""
            if c.default is not None:
                arg = c.default.arg
                padrao = "data/hora atual" if callable(arg) else (getattr(arg, "value", arg))
            linhas.append(f"| `{c.name}` | {tipo_legivel(c)} | {'sim' if c.nullable else 'não'} | {padrao} | "
                          f"{restricoes_da_coluna(tabela, c)} | {c.comment or ''} |")
        unicos = [u for u in tabela.constraints if type(u).__name__ == "UniqueConstraint" and len(u.columns) > 1]
        for u in unicos:
            linhas.append(f"\nRestrição de unicidade `{u.name}`: ({', '.join(col.name for col in u.columns)}).")
        linhas.append("")
    return "\n".join(linhas)


def mermaid_logico():
    nomes_tipo = {"INTEGER": "int", "TEXT": "text", "BOOLEAN": "bool", "DATETIME": "datetime"}
    linhas = ["erDiagram"]
    for tabela in db.metadata.sorted_tables:
        linhas.append(f"  {tabela.name.upper()} {{")
        for c in tabela.columns:
            tipo = tipo_legivel(c)
            tipo = nomes_tipo.get(tipo, tipo.lower().replace("(", "_").replace(")", ""))
            chave = "PK" if c.primary_key else ("FK" if c.foreign_keys else ("UK" if c.unique else ""))
            linhas.append(f"    {tipo} {c.name} {chave}".rstrip())
        linhas.append("  }")
    linhas += [
        '  USUARIO ||--o{ PEDIDO : "faz"',
        '  CATEGORIA ||--o{ PRODUTO : "agrupa"',
        '  PEDIDO ||--|{ ITEM_PEDIDO : "contém"',
        '  PRODUTO ||--o{ ITEM_PEDIDO : "aparece em"',
        '  PEDIDO ||--o{ PAGAMENTO : "tem tentativas"',
        '  PEDIDO ||--|{ HISTORICO_STATUS : "registra"',
    ]
    return "\n".join(linhas) + "\n"


def main():
    app = create_app(ConfigTeste)
    with app.app_context():
        pasta_db = RAIZ / "database"
        pasta_db.mkdir(exist_ok=True)
        (pasta_db / "schema_sqlite.sql").write_text(ddl(sqlite.dialect(), "SQLite"), encoding="utf-8")
        (pasta_db / "schema_postgresql.sql").write_text(ddl(postgresql.dialect(), "PostgreSQL"), encoding="utf-8")
        (pasta_db / "dicionario-de-dados.md").write_text(dicionario(), encoding="utf-8")
        diag = RAIZ / "docs" / "desenvolvimento" / "diagramas"
        diag.mkdir(parents=True, exist_ok=True)
        (diag / "02-modelo-logico.mmd").write_text(mermaid_logico(), encoding="utf-8")
    print("schema_sqlite.sql, schema_postgresql.sql, dicionario-de-dados.md e modelo lógico gerados")


if __name__ == "__main__":
    main()
