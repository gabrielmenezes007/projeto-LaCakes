# LaCakes Cupcakes Gourmet – Loja virtual

Autor: Gabriel M. O.

Sistema web responsivo para a confeitaria LaCakes (Jaú/SP) vender cupcakes pela internet: vitrine virtual,
carrinho, pedido, pagamento simulado (crédito, débito ou Pix), entrega ou retirada na loja, acompanhamento do
pedido e área administrativa.

**Tecnologias:** Python 3 · Flask (padrão MVC) · SQLAlchemy · SQLite (ou PostgreSQL/MySQL via `DATABASE_URL`) ·
HTML, CSS e JavaScript · pytest

## Como rodar

**Windows:** dê dois cliques em `iniciar.bat`. **Linux/macOS:** `./iniciar.sh`.

O script cria o ambiente virtual, instala as dependências, cria o banco com dados de exemplo e abre
http://127.0.0.1:5000. Requer Python 3.10 ou mais novo.

| Conta de teste | E-mail | Senha |
|---|---|---|
| Administradora | `admin@lacakes.test` | `Admin@2026` |
| Cliente | `cliente@lacakes.test` | `Cliente@2026` |

Cartão de teste aprovado: `4111 1111 1111 1111` (validade futura, CVV `123`). Cartões terminados em `0000` são
recusados. CEP de entrega de exemplo: `17201-000`.

Passo a passo completo, telas e mensagens de erro: [manual de uso](docs/desenvolvimento/manual-de-uso.md).

## Como testar

```bash
.venv\Scripts\python -m pytest --cov=app        # Linux/macOS: .venv/bin/python -m pytest --cov=app
```

São mais de 120 testes (models, regras de negócio, rotas, permissões, páginas de erro e o script SQL), com
cobertura acima de 90%.

## Arquitetura (MVC)

```
app/
  models/        M – entidades SQLAlchemy (Usuario, Categoria, Produto, Pedido, ItemPedido, Pagamento, HistoricoStatus)
  services/      M – regras de negócio (carrinho, frete, pagamento simulado, pedidos, contas, produtos)
  templates/     V – páginas Jinja2 (vitrine, conta, carrinho, checkout, pagamento, pedidos, admin, erros)
  static/        V – CSS responsivo, JavaScript e ilustrações
  controllers/   C – rotas organizadas em blueprints
  config.py      configurações (banco via DATABASE_URL)
  seed.py        dados iniciais (cardápio e contas de teste)
tests/           testes automatizados (pytest)
database/        projeto físico (SQL para SQLite e PostgreSQL) e dicionário de dados
docs/
  planejamento/     histórias de usuário, backlog, requisitos, UML, wireframes, mockups e mapas
  desenvolvimento/  modelo de dados e manual de uso
  testes-usuarios/  roteiro dos testes com usuários
  decisoes.md       decisões de projeto e seus motivos
scripts/         geração de diagramas, telas, ilustrações e documentação do banco
```

## Status

- [x] Planejamento: [docs/planejamento](docs/planejamento/README.md)
- [x] [Revisão do planejamento](docs/desenvolvimento/revisao-do-planejamento.md) (escopo, UML, IHC e dados)
- [x] Banco de dados: [modelo de dados](docs/desenvolvimento/modelo-de-dados.md) e [dicionário](database/dicionario-de-dados.md)
- [x] Código (front-end e back-end) e testes automatizados: [verificação e validação](docs/desenvolvimento/testes.md)
- [x] [Manual de uso](docs/desenvolvimento/manual-de-uso.md) e [telas do sistema](docs/desenvolvimento/img/telas)
- [x] Roteiro dos [testes com usuários](docs/testes-usuarios/README.md)
- [ ] Testes com 5 usuários e correções

## Regenerar os artefatos de planejamento

Requer Node.js (Mermaid) e Microsoft Edge.

```bash
pip install python-docx playwright pillow
cd scripts && npm install && cd ..
python scripts/render.py lote docs/planejamento/diagramas docs/planejamento/img
python scripts/gerar_figuras.py
python scripts/gerar_telas.py
python scripts/gerar_docs_banco.py
```
