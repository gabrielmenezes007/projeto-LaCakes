# LaCakes Cupcakes Gourmet – Loja virtual

Autor: Gabriel M. O.

Sistema web responsivo para a confeitaria LaCakes vender cupcakes pela internet: vitrine virtual, carrinho,
pedido, pagamento simulado (crédito, débito ou Pix), entrega/retirada, acompanhamento do pedido e área
administrativa.

## Estrutura do repositório

```
docs/
  planejamento/     histórias de usuário, backlog, requisitos, UML, wireframes, mockups e mapas
  desenvolvimento/  modelo de dados, dicionário de dados, testes e relatório do desenvolvimento
  testes-usuarios/  formulário de teste e consolidação das avaliações
  decisoes.md       decisões de projeto e seus motivos
app/                código da aplicação (Flask, padrão MVC)
tests/              testes automatizados (pytest)
database/           script SQL e dicionário de dados
scripts/            scripts que geram diagramas, telas e documentos
```

## Status

- [x] Planejamento: ver [docs/planejamento](docs/planejamento/README.md)
- [ ] Banco de dados, código e testes
- [ ] Testes com usuários e correções
- [ ] Documentação final

## Como regenerar os artefatos de planejamento

Requisitos: Python 3.12, Node.js (para o Mermaid) e Microsoft Edge. Para o documento Word/PDF, também
Microsoft Word e um modelo `.docx` (que não fica no repositório).

```bash
pip install python-docx playwright pillow
cd scripts && npm install && cd ..
python scripts/render.py lote docs/planejamento/diagramas docs/planejamento/img
python scripts/gerar_figuras.py
python scripts/gerar_telas.py
```

Documento Word (opcional): copie `scripts/dados_aluno.exemplo.json` para `scripts/dados_aluno.json`, preencha
os dados e rode:

```bash
python scripts/montar_documento_planejamento.py "<modelo.docx>" "<saida.docx>"
```
