"""Preenche o modelo Word do documento de desenvolvimento e anexa a documentação do repositório como apêndices.

Uso: python scripts/montar_documento_desenvolvimento.py <modelo.docx> <saida.docx>
O modelo e o documento gerado não fazem parte do repositório. Dados de identificação: scripts/dados_aluno.json.

Os apêndices são convertidos dos arquivos Markdown de docs/ (fonte única), por um conversor simples que entende
títulos, parágrafos, listas, tabelas, imagens, citações e blocos de código.
"""
import pathlib
import re
import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import conteudo_planejamento as C  # noqa: E402
from montar_documento_planejamento import (FUNDO_CABECALHO, Escritor, bordas, limpar, nao_quebrar_linha,  # noqa: E402
                                           repetir_cabecalho, run, sombrear)

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
REPOSITORIO = "https://github.com/gabrielmenezes007/projeto-LaCakes"
CINZA = RGBColor(0x66, 0x66, 0x66)

APENDICES = [
    ("A", "Revisão do planejamento", [DOCS / "desenvolvimento" / "revisao-do-planejamento.md"]),
    ("B", "Modelo de dados e dicionário de dados", [DOCS / "desenvolvimento" / "modelo-de-dados.md",
                                                   RAIZ / "database" / "dicionario-de-dados.md"]),
    ("C", "Telas do sistema implementado", None),
    ("D", "Testes: verificação e validação", [DOCS / "desenvolvimento" / "testes.md"]),
    ("E", "Manual de uso", [DOCS / "desenvolvimento" / "manual-de-uso.md"]),
    ("F", "Roteiro e formulário dos testes com usuários", [DOCS / "testes-usuarios" / "roteiro-de-teste.md",
                                                          DOCS / "testes-usuarios" / "formulario-de-teste.md"]),
]

TELAS = [
    ("01-vitrine", "Vitrine"), ("02-vitrine-filtro-recheados", "Vitrine filtrada"),
    ("03-detalhe-produto", "Detalhes do cupcake"), ("04-erro-estoque-insuficiente", "Erro: estoque insuficiente"),
    ("05-cadastro-com-erros", "Cadastro com erros"), ("06-login-invalido", "Login inválido"),
    ("07-carrinho-vazio", "Carrinho vazio"), ("08-carrinho", "Carrinho"),
    ("09-checkout-cep-fora-da-area", "Checkout: CEP fora da área"), ("10-pagamento-credito", "Pagamento (crédito)"),
    ("11-pagamento-pix", "Pagamento (Pix)"), ("12-pagamento-recusado", "Pagamento recusado"),
    ("13-pedido-confirmado", "Pedido confirmado"), ("14-meus-pedidos", "Meus pedidos"),
    ("15-acompanhamento", "Acompanhamento (pago)"), ("21-acompanhamento-em-preparo", "Acompanhamento (em preparo)"),
    ("16-acesso-negado-403", "Erro 403"), ("17-pagina-nao-encontrada-404", "Erro 404"),
    ("18-admin-pedidos", "Admin: pedidos"), ("19-admin-produtos-estoque", "Admin: produtos e estoque"),
    ("20-admin-produto-com-erros", "Admin: produto com erros"),
]

INLINE = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|\*[^*\s][^*]*\*)")


# ------------------------------------------------------------------ Markdown -> Word
def inline(p, texto, tam=10, negrito=False, italico=False):
    """Escreve texto com **negrito**, *itálico*, `código` e [links](url) (mostra só o texto do link)."""
    for parte in INLINE.split(texto):
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**"):
            inline(p, parte[2:-2], tam, negrito=True, italico=italico)  # pode ter `código` dentro
        elif parte.startswith("`") and parte.endswith("`"):
            r = run(p, parte[1:-1], negrito or None, tam - 0.5)
            r.font.name = "Consolas"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        elif parte.startswith("["):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", parte)
            run(p, m.group(1), negrito or None, tam, italico or None)
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            run(p, parte[1:-1], negrito or None, tam, True)
        else:
            run(p, parte, negrito or None, tam, italico or None)


class Markdown:
    def __init__(self, escritor, nivel_base=2):
        self.e = escritor
        self.nivel_base = nivel_base

    def tabela(self, linhas, pasta):
        celulas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas]
        cab, corpo = celulas[0], [c for c in celulas[2:]]
        ncol = len(cab)
        tam = 8 if ncol >= 5 else 9
        t = self.e.doc.add_table(rows=1 + len(corpo), cols=ncol)
        self.e._colocar(t._tbl)
        bordas(t)
        for i, txt in enumerate(cab):
            c = t.rows[0].cells[i]
            limpar(c.paragraphs[0])
            inline(c.paragraphs[0], txt, tam, negrito=True)
            sombrear(c, FUNDO_CABECALHO)
        repetir_cabecalho(t.rows[0])
        for li, linha in enumerate(corpo, 1):
            for ci in range(ncol):
                p = t.rows[li].cells[ci].paragraphs[0]
                p.paragraph_format.space_after = Pt(1)
                inline(p, linha[ci] if ci < len(linha) else "", tam)
            nao_quebrar_linha(t.rows[li])
        self.e.par(espaco_depois=4)

    def converter(self, arquivo, pular_h1=False):
        pasta = arquivo.parent
        linhas = arquivo.read_text(encoding="utf-8").splitlines()
        i = 0
        paragrafo = []

        def fechar_paragrafo():
            if paragrafo:
                p = self.e.par(alinhar="just")
                inline(p, " ".join(s.strip() for s in paragrafo))
                paragrafo.clear()

        while i < len(linhas):
            linha = linhas[i]
            s = linha.strip()
            if not s:
                fechar_paragrafo()
            elif s.startswith("```"):
                fechar_paragrafo()
                i += 1
                while i < len(linhas) and not linhas[i].strip().startswith("```"):
                    p = self.e.par(espaco_depois=0)
                    p.paragraph_format.left_indent = Cm(0.5)
                    r = run(p, linhas[i], tam=8.5)
                    r.font.name = "Consolas"
                    i += 1
                self.e.par(espaco_depois=2)
            elif s.startswith("#"):
                fechar_paragrafo()
                nivel = len(s) - len(s.lstrip("#"))
                texto = s.lstrip("#").strip().replace("`", "").replace("**", "")
                if nivel == 1 and pular_h1:
                    pass  # o título do apêndice já faz esse papel
                elif nivel == 1:
                    self.e.titulo(texto, self.nivel_base)
                elif nivel + self.nivel_base - 1 <= 3:
                    self.e.titulo(texto, nivel + self.nivel_base - 1)
                else:
                    p = self.e.par(negrito=True, espaco_depois=4)
                    inline(p, texto, 10.5, negrito=True)
            elif s.startswith("|"):
                fechar_paragrafo()
                bloco = []
                while i < len(linhas) and linhas[i].strip().startswith("|"):
                    bloco.append(linhas[i])
                    i += 1
                self.tabela(bloco, pasta)
                continue
            elif s.startswith("!["):
                fechar_paragrafo()
                m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", s)
                caminho = (pasta / m.group(2)).resolve()
                if caminho.exists():
                    self.e.imagem(caminho, m.group(1))
            elif re.match(r"^(- \[[ x]\] |[-*] |\d+\. )", s):
                fechar_paragrafo()
                marcador = "☐" if s.startswith("- [ ]") else ("•" if s[0] in "-*" else s.split(".")[0] + ".")
                texto = re.sub(r"^(- \[[ x]\] |[-*] |\d+\. )", "", s)
                # junta linhas de continuação (indentadas)
                while i + 1 < len(linhas) and linhas[i + 1].startswith("   ") and linhas[i + 1].strip() \
                        and not re.match(r"^\s*(- |\d+\. )", linhas[i + 1]):
                    i += 1
                    texto += " " + linhas[i].strip()
                p = self.e.par(espaco_depois=3)
                recuo = 1.2 if linha.startswith("  ") else 0.6
                p.paragraph_format.left_indent = Cm(recuo)
                p.paragraph_format.first_line_indent = Cm(-0.4)
                run(p, marcador + " ")
                inline(p, texto)
            elif s.startswith(">"):
                fechar_paragrafo()
                texto = s.lstrip(">").strip()
                while i + 1 < len(linhas) and linhas[i + 1].strip().startswith(">"):
                    i += 1
                    texto += " " + linhas[i].strip().lstrip(">").strip()
                p = self.e.par(espaco_depois=6)
                p.paragraph_format.left_indent = Cm(0.6)
                inline(p, texto, 9.5, italico=True)
            elif s.startswith("---"):
                fechar_paragrafo()
            else:
                paragrafo.append(s)
            i += 1
        fechar_paragrafo()


# ------------------------------------------------------------------ preenchimento do modelo
def substituir_rotulado(p, rotulo, valor):
    limpar(p)
    run(p, rotulo + " ", True)
    run(p, valor)


def celula(c, linhas, tam=10):
    p = c.paragraphs[0]
    limpar(p)
    for extra in c.paragraphs[1:]:
        extra._element.getparent().remove(extra._element)
    for i, l in enumerate(linhas):
        alvo = p if i == 0 else c.add_paragraph()
        inline(alvo, l, tam)


def preencher(doc):
    aluno = C.ALUNO
    ps = doc.paragraphs
    for p in ps:
        if p.text.startswith("Nome:"):
            substituir_rotulado(p, "Nome:", aluno["nome"])
        elif p.text.startswith("RGM:"):
            substituir_rotulado(p, "RGM:", aluno["rgm"])
            novo = OxmlElement("w:p")
            p._p.addnext(novo)
            pc = docx.text.paragraph.Paragraph(novo, p._parent)
            run(pc, "Curso: ", True)
            run(pc, aluno["curso"])
        elif p.text.startswith("Link do repositório:"):
            substituir_rotulado(p, "Link do repositório:", REPOSITORIO)
            ancora_doc = p

    esc = Escritor(doc, ancora_doc._p)
    esc.par("Projeto: LaCakes Cupcakes Gourmet – loja virtual de cupcakes gourmet (Jaú/SP), continuação do "
            "planejamento entregue anteriormente.", alinhar="just")
    esc.par("A documentação do planejamento foi revisada e atualizada no repositório (pasta docs/). Os principais "
            "documentos revisados estão nos apêndices deste arquivo:", alinhar="just")
    for letra, nome, _ in APENDICES:
        esc.item(f"Apêndice {letra} – {nome}")
    esc.par("O repositório também contém as histórias de usuário, backlog, diagramas UML, wireframes e mockups "
            "(docs/planejamento), o código-fonte (app/), os testes automatizados (tests/) e os scripts SQL "
            "(database/).", alinhar="just")

    # Tabela de codificação
    valores = [
        ["Python 3.12 com Flask 3.1 (padrão MVC) e SQLAlchemy 2.1. Front-end em HTML5, CSS3 e JavaScript."],
        ["SQLite (padrão), acessado pelo ORM SQLAlchemy. Compatível com PostgreSQL e MySQL pela variável "
         "DATABASE_URL, sem mudar o código. Scripts SQL e dicionário de dados no Apêndice B."],
        ["Execução local (servidor Flask em http://127.0.0.1:5000), iniciada com um comando: iniciar.bat "
         "(Windows) ou iniciar.sh (Linux/macOS). Sem hospedagem pública nesta versão."],
        ["Aplicação web responsiva: navegador no computador e no celular."],
        None,
        [REPOSITORIO],
        ["Execução local – passo a passo no README do repositório e no Apêndice E (Manual de uso)."],
        ["a preencher"],
    ]
    t = doc.tables[0]
    for i, v in enumerate(valores):
        if v is not None:
            celula(t.rows[i].cells[1], v)
    for p in t.rows[4].cells[1].paragraphs:
        if "Tradicional" in p.text:
            limpar(p)
            run(p, "(X) Tradicional", True)

    # Tabelas dos testadores: marcar como pendentes
    for tb in doc.tables[1:6]:
        for row in tb.rows:
            for c in {id(x): x for x in row.cells}.values():
                p = c.paragraphs[-1]
                r = run(p, " a preencher", italico=True, tam=9)
                r.font.color.rgb = CINZA

    # Laudo de qualidade
    laudo = next(p for p in doc.paragraphs if p.text.startswith("Insira a seguir o laudo"))
    e2 = Escritor(doc, laudo._p)
    e2.par()
    p = e2.par(negrito=True)
    run(p, "1. Verificação – testes automatizados", True, 11)
    e2.par("Resultado da execução com pytest (evidência completa no Apêndice D e em "
           "docs/desenvolvimento/evidencias/resultado-testes.txt):", alinhar="just")
    e2.tabela(["Arquivo de teste", "Tipo", "Testes", "Resultado"], [
        ["test_models.py", "Unitário", "15", "15 aprovados"], ["test_servicos.py", "Unitário", "39", "39 aprovados"],
        ["test_rotas_cliente.py", "Integração", "43", "43 aprovados"],
        ["test_rotas_admin_e_erros.py", "Integração", "23", "23 aprovados"],
        ["test_banco.py", "Integração (dados)", "3", "3 aprovados"], ["Total", "", "123", "123 aprovados – cobertura 95%"],
    ], [5.5, 3.5, 2, 4])
    p = e2.par(negrito=True)
    run(p, "2. Erros encontrados durante o desenvolvimento e correções", True, 11)
    e2.tabela(["#", "Erro", "Como foi encontrado", "Correção"], [
        ["V1", "Mensagem de pedido mínimo não aparecia no checkout (macro com o mesmo nome da variável)",
         "Revisão de código", "Macro importado com outro nome"],
        ["V2", "Teste de desativar produto acusava erro falso (nome na mensagem de sucesso)", "Teste automatizado",
         "Verificação mais precisa"],
        ["V3", "Aviso do SQLAlchemy ao montar pedidos nos testes", "Execução dos testes",
         "Pedido adicionado à sessão antes dos itens"],
        ["V4", "Valores longos desalinhados no resumo do pedido", "Teste manual no navegador",
         "Coluna de valores alinhada à direita"],
        ["V5", "Ícone de conta pouco visível sobre o roxo do topo", "Revisão visual",
         "Círculo branco com as iniciais"],
    ], [1, 6.2, 3.6, 4.2])
    p = e2.par(negrito=True)
    run(p, "3. Erros apontados pelos testadores e correções", True, 11)
    e2.tabela(["#", "Erro relatado", "Testador(es)", "Correção", "Evidência"],
              [[str(i), "a preencher", "", "", ""] for i in range(1, 5)], [1, 5, 2.8, 3.6, 2.6])
    p = e2.par(negrito=True)
    run(p, "4. Conclusão", True, 11)
    p = e2.par(alinhar="just")
    r = run(p, "a preencher após os testes com usuários.", italico=True)
    r.font.color.rgb = CINZA

    # Link do vídeo da solução atualizada
    celula(doc.tables[6].rows[0].cells[1], ["a preencher"])


def apendices(doc):
    esc = Escritor(doc, doc.paragraphs[-1]._p)
    for letra, nome, arquivos in APENDICES:
        esc.quebra_pagina()
        esc.titulo(f"Apêndice {letra} – {nome}", 1)
        if arquivos is None:
            esc.par("Capturas de tela do sistema em funcionamento (tamanho de celular), geradas por "
                    "scripts/capturar_telas.py em 15/11/2026.", alinhar="just")
            pasta = DOCS / "desenvolvimento" / "img" / "telas"
            esc.grade_imagens([(pasta / f"{n}.png", t) for n, t in TELAS], colunas=3, largura_cm=4.6)
            esc.imagem(pasta / "22-vitrine-computador.png", "Vitrine em tela de computador (1280 px)")
            continue
        md = Markdown(esc, nivel_base=2)
        for arquivo in arquivos:
            md.converter(arquivo, pular_h1=len(arquivos) == 1)


def main(modelo, saida):
    doc = docx.Document(modelo)
    preencher(doc)
    apendices(doc)
    doc.core_properties.author = C.ALUNO["nome"]
    doc.core_properties.title = "Desenvolvimento – LaCakes Cupcakes Gourmet"
    doc.save(saida)
    print("ok", saida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
