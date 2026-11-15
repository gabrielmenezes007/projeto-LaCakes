"""Preenche o modelo Word do documento de planejamento e gera os Markdown de docs/planejamento.

Uso: python scripts/montar_documento_planejamento.py <modelo.docx> <saida.docx>
O modelo .docx e o documento gerado não fazem parte do repositório.
"""
import copy
import pathlib
import sys

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import conteudo_planejamento as C  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
IMG = RAIZ / "docs" / "planejamento" / "img"
LARGURA_UTIL_CM = 15.0
ALTURA_MAX_CM = 21.0
COR_TITULO = RGBColor(0x11, 0x2F, 0x24)
FUNDO_CABECALHO = "EADBE6"

H = {h["id"]: h for h in C.HISTORIAS}
RN = {r[0]: r for r in C.REGRAS}
RNF = {r[0]: r for r in C.RNFS}


# ----------------------------------------------------------------- utilitários
def run(p, texto, negrito=None, tam=None, italico=None, cor=None):
    r = p.add_run(texto)
    r.font.name = "Arial"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    if negrito is not None:
        r.bold = negrito
    if italico:
        r.italic = True
    if tam:
        r.font.size = Pt(tam)
    if cor:
        r.font.color.rgb = cor
    return r


def limpar(p):
    for r in list(p.runs):
        r._element.getparent().remove(r._element)


def nivel_estrutura(p, nivel):
    ppr = p._p.get_or_add_pPr()
    ol = OxmlElement("w:outlineLvl")
    ol.set(qn("w:val"), str(nivel))
    ppr.append(ol)


class Escritor:
    """Insere conteúdo em sequência depois de um elemento âncora do corpo."""

    def __init__(self, doc, ancora):
        self.doc = doc
        self.ancora = ancora

    def _colocar(self, elem):
        self.ancora.addnext(elem)
        self.ancora = elem

    def par(self, texto="", negrito=None, tam=None, alinhar=None, italico=None, espaco_depois=6):
        p = self.doc.add_paragraph()
        self._colocar(p._p)
        if texto:
            run(p, texto, negrito, tam, italico)
        p.paragraph_format.space_after = Pt(espaco_depois)
        if alinhar == "centro":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif alinhar == "just":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        return p

    def rotulado(self, rotulo, texto):
        p = self.par()
        run(p, rotulo + " ", True)
        run(p, texto)
        return p

    def titulo(self, texto, nivel=1):
        tam = {1: 15, 2: 13, 3: 11.5}[nivel]
        p = self.par(espaco_depois=8)
        p.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
        p.paragraph_format.keep_with_next = True
        run(p, texto, True, tam, cor=COR_TITULO)
        nivel_estrutura(p, nivel - 1)
        return p

    def quebra_pagina(self):
        p = self.par(espaco_depois=0)
        p.add_run().add_break(WD_BREAK.PAGE)

    def item(self, texto, marcador="•"):
        p = self.par(espaco_depois=3)
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.4)
        run(p, f"{marcador} {texto}")
        return p

    def imagem(self, caminho, legenda, largura_cm=LARGURA_UTIL_CM):
        w, h = Image.open(caminho).size
        larg = min(largura_cm, ALTURA_MAX_CM * w / h)
        p = self.par(alinhar="centro", espaco_depois=2)
        p.add_run().add_picture(str(caminho), width=Cm(larg))
        lg = self.par(alinhar="centro", espaco_depois=10)
        run(lg, legenda, italico=True, tam=9)

    def tabela(self, cabecalho, linhas, larguras=None, tam=9):
        t = self.doc.add_table(rows=1 + len(linhas), cols=len(cabecalho))
        self._colocar(t._tbl)
        bordas(t)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, txt in enumerate(cabecalho):
            c = t.rows[0].cells[i]
            preencher_celula(c, txt, negrito=True, tam=tam)
            sombrear(c, FUNDO_CABECALHO)
        repetir_cabecalho(t.rows[0])
        for li, linha in enumerate(linhas, start=1):
            for ci, txt in enumerate(linha):
                preencher_celula(t.rows[li].cells[ci], txt, tam=tam)
        if larguras:
            for row in t.rows:
                for ci, lw in enumerate(larguras):
                    row.cells[ci].width = Cm(lw)
        self.par(espaco_depois=4)
        return t

    def grade_imagens(self, itens, colunas=3, largura_cm=4.6):
        linhas = (len(itens) + colunas - 1) // colunas
        t = self.doc.add_table(rows=linhas, cols=colunas)
        self._colocar(t._tbl)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, (caminho, legenda) in enumerate(itens):
            c = t.rows[i // colunas].cells[i % colunas]
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(caminho), width=Cm(largura_cm))
            lg = c.add_paragraph()
            lg.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run(lg, legenda, italico=True, tam=8)
        for row in t.rows:
            nao_quebrar_linha(row)
        self.par(espaco_depois=4)


def preencher_celula(c, texto, negrito=False, tam=9):
    linhas = texto if isinstance(texto, list) else [texto]
    p = c.paragraphs[0]
    limpar(p)
    for i, l in enumerate(linhas):
        if i:
            p = c.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        if isinstance(l, tuple):  # (rótulo em negrito, texto)
            run(p, l[0], True, tam)
            run(p, l[1], negrito, tam)
        else:
            run(p, l, negrito, tam)


def bordas(t):
    tblPr = t._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "999999")
        b.append(e)
    tblPr.append(b)


def sombrear(c, cor):
    tcPr = c._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), cor)
    tcPr.append(s)


def repetir_cabecalho(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader")
    e.set(qn("w:val"), "true")
    trPr.append(e)


def nao_quebrar_linha(row):
    trPr = row._tr.get_or_add_trPr()
    e = OxmlElement("w:cantSplit")
    e.set(qn("w:val"), "true")
    trPr.append(e)


# ------------------------------------------------------------ partes do doc
def preencher_identificacao(doc):
    ps = doc.paragraphs
    for p in ps:
        if p.text.startswith("Nome:"):
            limpar(p)
            run(p, "Nome: ", True)
            run(p, C.ALUNO["nome"])
            p_nome = p
        elif p.text.startswith("RGM:"):
            limpar(p)
            run(p, "RGM: ", True)
            run(p, C.ALUNO["rgm"])
            novo = copy.deepcopy(p._p)
            p._p.addnext(novo)
            pc = docx.text.paragraph.Paragraph(novo, p._parent)
            limpar(pc)
            run(pc, "Curso: ", True)
            run(pc, C.ALUNO["curso"])
            ancora = novo
    esc = Escritor(doc, ancora)
    esc.par()
    esc.rotulado("Tema:", f"Loja virtual de cupcakes gourmet – \"{C.LOJA}\" (vitrine virtual, pedido eletrônico, pagamento e entrega).")
    esc.par(C.CONTEXTO, alinhar="just")
    esc.par("Os cartões a seguir usam as regras de negócio (RN) e os requisitos não funcionais (RNF) descritos "
            "na seção 3. A escala de prioridade (A a E) e os pontos de história estão explicados na seção 2.",
            alinhar="just")
    return p_nome


def preencher_cartoes(doc):
    modelo = doc.tables[0]
    elem_modelo = modelo._tbl
    anterior = elem_modelo
    for i, h in enumerate(C.HISTORIAS):
        if i == 0:
            tbl = elem_modelo
        else:
            tbl = copy.deepcopy(elem_modelo)
            sep = OxmlElement("w:p")
            anterior.addnext(sep)
            sep.addnext(tbl)
        t = docx.table.Table(tbl, modelo._parent)
        rows = t.rows

        def simples(idx, rotulo, valor, negrito_rot=False):
            p = rows[idx].cells[0].paragraphs[0]
            limpar(p)
            run(p, rotulo + " ", True if negrito_rot else True)
            run(p, valor)

        simples(0, "ID:", h["id"])
        simples(1, "Título:", h["titulo"])
        simples(2, "Requerente:", h["requerente"])
        simples(3, "Ação:", h["acao"])
        simples(4, "Comentários:", h["comentarios"])

        def lista(idx, rotulo, itens):
            cel = rows[idx].cells[0]
            p0, p1 = cel.paragraphs[0], cel.paragraphs[1]
            limpar(p0)
            run(p0, rotulo, True)
            base = p1._p
            for j, txt in enumerate(itens):
                if j == 0:
                    alvo = p1
                else:
                    novo = copy.deepcopy(base)
                    base.addnext(novo)
                    base = novo
                    alvo = docx.text.paragraph.Paragraph(novo, cel)
                limpar(alvo)
                run(alvo, txt)

        lista(5, "Critérios de aceitação:", [f"CA#{k} – {txt}" for k, txt in enumerate(h["ca"], 1)])
        lista(6, "Regras de negócio:", [f"{r} – {RN[r][1]}: {RN[r][2]}" for r in h["rn"]])
        lista(7, "Requisito não funcional:", [f"{r} – {RNF[r][1]}" for r in h["rnf"]])
        cel = rows[8].cells[0]
        for p in cel.paragraphs:
            txt = p.text.strip()
            if txt.startswith("["):
                letra = txt[-1]
                limpar(p)
                run(p, f"[{'X' if letra == h['prioridade'] else '  '}] {letra}", letra == h["prioridade"])
            else:
                limpar(p)
                run(p, "Prioridade:", True)
        simples(9, "Pontos de história:", str(h["pontos"]))
        manter_tabela_junta(t)
        anterior = tbl


def preencher_backlog(doc):
    t = doc.tables[len(C.HISTORIAS)]  # a tabela de backlog vem logo depois dos cartões
    assert t.rows[0].cells[0].text.strip() == "ID", t.rows[0].cells[0].text
    for pos, uid in enumerate(C.ORDEM_BACKLOG, start=1):
        h = H[uid]
        tema = C.TEMAS[h["tema"]][0]
        valores = [uid, f"[{tema}] {h['acao']}", str(h["pontos"]), f"{pos} ({h['prioridade']})"]
        for ci, v in enumerate(valores):
            preencher_celula(t.rows[pos].cells[ci], v, tam=9)
    larguras(t, [1.5, 9.7, 2.0, 1.8])
    return t


def larguras(t, cms):
    grid = t._tbl.tblGrid
    for col, cm in zip(grid.findall(qn("w:gridCol")), cms):
        col.set(qn("w:w"), str(int(cm * 567)))
    for row in t.rows:
        for c, cm in zip(row.cells, cms):
            c.width = Cm(cm)


def manter_tabela_junta(t):
    """Evita que o cartão quebre entre páginas (linhas inteiras + manter com a próxima)."""
    for i, row in enumerate(t.rows):
        nao_quebrar_linha(row)
        if i < len(t.rows) - 1:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.keep_with_next = True


def secoes_finais(doc):
    ultimo = doc.paragraphs[-1]
    esc = Escritor(doc, ultimo._p)
    esc.par("Legenda do backlog: a coluna Prioridade mostra a ordem de execução (1 = primeiro) e, entre parênteses, "
            "a classe de prioridade do cartão (A a E). O tema de cada história aparece entre colchetes.", tam=9, italico=True)
    esc.quebra_pagina()

    # 1. Personas
    esc.titulo("1. Visão do produto e personas")
    esc.par(f"O produto é a loja virtual da {C.LOJA}. O objetivo é vender pela internet com segurança e clareza, "
            "resolvendo os problemas que a loja tem hoje com pedidos por mensagem. As histórias foram escritas a "
            "partir das falas de cada perfil de usuário abaixo.", alinhar="just")
    esc.tabela(["Perfil", "Quem é / o que precisa"], [list(p) for p in C.PERSONAS], [4.5, 10.5])

    # 2. Escala
    esc.titulo("2. Escala de prioridade e pontos de história")
    esc.tabela(["Prioridade", "Significado"], [list(e) for e in C.ESCALA_PRIORIDADE], [2.5, 12.5])
    esc.par("Pontos de história seguem a sequência de Fibonacci (1, 2, 3, 5, 8). Eles medem o esforço relativo: "
            "1 ponto é uma alteração pequena e bem conhecida; 5 pontos envolve várias telas, regras e testes. "
            f"Total do backlog: {sum(h['pontos'] for h in C.HISTORIAS)} pontos em {len(C.HISTORIAS)} histórias.", alinhar="just")
    esc.titulo("2.1 Mapa de afinidade", 2)
    esc.par("As histórias foram agrupadas por eixo temático. Cada cor representa um tema e facilita enxergar o "
            "trabalho de cada área do sistema.", alinhar="just")
    esc.imagem(IMG / "00-mapa-de-afinidade.png", "Figura 1 – Mapa de afinidade das histórias de usuário")

    # 3. Requisitos
    esc.quebra_pagina()
    esc.titulo("3. Requisitos extraídos das histórias")
    esc.titulo("3.1 Requisitos funcionais", 2)
    esc.tabela(["ID", "Requisito funcional", "Histórias"], [[r[0], r[1], ", ".join(r[2])] for r in C.RFS], [1.6, 10.4, 3.0])
    esc.titulo("3.2 Requisitos não funcionais", 2)
    esc.tabela(["ID", "Nome", "Descrição"], [list(r) for r in C.RNFS], [1.6, 3.6, 9.8])
    esc.titulo("3.3 Regras de negócio", 2)
    esc.tabela(["ID", "Regra", "Descrição"], [list(r) for r in C.REGRAS], [1.6, 3.6, 9.8])

    # 4. Tarefas
    esc.titulo("4. Tarefas por história (estimativas de 2 a 12 horas)")
    esc.par("Cada história foi quebrada em tarefas técnicas. Para manter as tarefas pequenas e fáceis de estimar, nenhuma tarefa "
            "passa de 12 horas nem fica abaixo de 2 horas.", alinhar="just")
    linhas, total = [], 0
    for uid in C.ORDEM_BACKLOG:
        for k, (tarefa, horas) in enumerate(C.TAREFAS[uid], 1):
            linhas.append([uid, f"T{uid[2:]}.{k}", tarefa, str(horas)])
            total += horas
    esc.tabela(["História", "Tarefa", "Descrição da tarefa", "Horas"], linhas, [1.8, 1.6, 10.0, 1.6])
    esc.par(f"Total estimado: {total} horas de desenvolvimento.", negrito=True)

    esc.titulo("4.1 Sugestão de sprints", 2)
    sprints = [
        ("Sprint 1 – Fundação", ["US05", "US06", "US19", "US20", "US01", "US08", "US09"]),
        ("Sprint 2 – Compra completa", ["US10", "US12", "US13", "US17", "US23", "US03", "US04", "US22"]),
        ("Sprint 3 – Refinamentos", ["US11", "US15", "US16", "US21", "US07", "US02", "US14", "US18"]),
    ]
    esc.tabela(["Sprint", "Histórias", "Pontos"],
               [[n, ", ".join(us), str(sum(H[u]["pontos"] for u in us))] for n, us in sprints], [5, 8, 2])

    # 5. UML
    esc.quebra_pagina()
    esc.titulo("5. Artefatos UML")
    esc.titulo("5.1 Diagrama de caso de uso geral", 2)
    esc.par("Atores: Visitante, Cliente (que herda tudo o que o Visitante faz), Administrador e o Serviço de "
            "pagamento (sistema externo, simulado nesta versão).", alinhar="just")
    esc.imagem(IMG / "01-diagrama-casos-de-uso.png", "Figura 2 – Diagrama de caso de uso geral")
    esc.titulo("5.2 Casos de uso expandidos", 2)
    esc.par("As telas citadas (TELAxx e ERROxx) estão na seção 6 e as regras (RNxx) na seção 3.3.", alinhar="just")
    for uc in C.CASOS_DE_USO:
        esc.titulo(f"{uc['id']} – {uc['nome']}", 3)
        basico = [f"{i}. {passo}" for i, passo in enumerate(uc["basico"], 1)]
        alts = []
        for nome, passos in uc["alternativos"]:
            alts.append(("Curso alternativo " + nome, ""))
            alts.extend(passos)
        linhas = [["Nome", uc["nome"]], ["Identificador", uc["id"]], ["Atores", uc["atores"]],
                  ["Descrição", uc["descricao"]], ["Pré-condições", uc["pre"]], ["Pós-condições", uc["pos"]],
                  ["Histórias relacionadas", uc["historias"]], ["Curso básico de ação", basico],
                  ["Cursos alternativos", alts]]
        t = esc.doc.add_table(rows=len(linhas), cols=2)
        esc._colocar(t._tbl)
        bordas(t)
        for i, (k, v) in enumerate(linhas):
            preencher_celula(t.rows[i].cells[0], k, negrito=True)
            sombrear(t.rows[i].cells[0], FUNDO_CABECALHO)
            preencher_celula(t.rows[i].cells[1], v)
            t.rows[i].cells[0].width = Cm(3.6)
            t.rows[i].cells[1].width = Cm(11.4)
        esc.par(espaco_depois=4)

    esc.quebra_pagina()
    esc.titulo("5.3 Diagrama de classes (persistência)", 2)
    esc.par("Classes persistentes do sistema. O carrinho fica na sessão do navegador (não é gravado no banco) "
            "e por isso não aparece aqui. Composição foi usada onde a parte não existe sem o todo (itens, "
            "pagamentos e histórico pertencem ao pedido); agregação entre Categoria e Produto.", alinhar="just")
    esc.imagem(IMG / "03-diagrama-de-classes.png", "Figura 3 – Diagrama de classes de persistência")
    esc.titulo("5.4 Diagramas de sequência", 2)
    esc.par("Cada diagrama mostra o cenário normal e os cenários alternativos com blocos \"alt\".", alinhar="just")
    esc.imagem(IMG / "04-sequencia-login.png", "Figura 4 – Sequência: autenticar usuário (UC04)")
    esc.imagem(IMG / "05-sequencia-pedido-pagamento.png", "Figura 5 – Sequência: finalizar pedido e pagar (UC06/UC07)")
    esc.imagem(IMG / "06-sequencia-status-pedido.png", "Figura 6 – Sequência: atualizar e acompanhar status (UC11/UC08)")
    esc.titulo("5.5 Diagrama de atividades", 2)
    esc.imagem(IMG / "07-diagrama-de-atividades-compra.png", "Figura 7 – Atividades do processo de compra", 13)

    # 6. IHC
    esc.quebra_pagina()
    esc.titulo("6. Protótipo das telas (IHC)")
    esc.par("O aplicativo será web e responsivo (mobile first), por isso as telas foram desenhadas no tamanho de um "
            "celular. As mesmas telas funcionam em tablet e computador com mais colunas na vitrine.", alinhar="just")
    esc.titulo("6.1 Lista de telas", 2)
    esc.tabela(["ID", "Tela"], [list(t) for t in C.TELAS], [2.5, 12.5])
    esc.titulo("6.2 Mapa conceitual", 2)
    esc.imagem(IMG / "08-mapa-conceitual.png", "Figura 8 – Mapa conceitual da loja virtual")
    esc.titulo("6.3 Mapa navegacional (mapa do app)", 2)
    esc.par("Lilás: telas públicas; laranja: telas do cliente logado; amarelo: área administrativa; vermelho "
            "tracejado: telas e mensagens de erro.", alinhar="just")
    esc.imagem(IMG / "09-mapa-navegacional.png", "Figura 9 – Mapa navegacional")
    esc.quebra_pagina()
    esc.titulo("6.4 Wireframes", 2)
    esc.par("Wireframes de baixa fidelidade (tons de cinza, imagens representadas por caixas com X). Incluem as "
            "telas de erro (ERRO01 a ERRO08).", alinhar="just")
    esc.grade_imagens([(IMG / "wireframes" / f"{t}.png", f"{t} – {n}") for t, n in C.TELAS])
    esc.quebra_pagina()
    esc.titulo("6.5 Mockups (média/alta fidelidade)", 2)
    esc.par("Paleta da LaCakes: Roxo Amora #5D2452 (ações principais), Verde Profundo #112F24 (títulos e área "
            "admin), Creme Amêndoa #FAF4ED (fundo) e Menta Sálvia #29604C (confirmações e pagamento). Os tons claros "
            "usados em seleções e destaques (#F3E8F1, #EADBE6 e #DDEBE4) são variações dessas mesmas cores.", alinhar="just")
    esc.par("Acessibilidade: o texto branco tem contraste de 11,4:1 sobre o Roxo Amora, 14,4:1 sobre o Verde "
            "Profundo e 7,3:1 sobre a Menta Sálvia; o texto principal sobre o Creme Amêndoa tem 13,9:1. Todos passam "
            "no nível AA da WCAG 2.1 (mínimo 4,5:1). Mensagens de erro aparecem perto do campo, em vermelho e com "
            "ícone, para não depender só da cor.", alinhar="just")
    esc.grade_imagens([(IMG / "mockups" / f"{t}.png", f"{t} – {n}") for t, n in C.TELAS])

    esc.titulo("7. Ferramentas utilizadas")
    esc.par("Diagramas UML e mapas: Mermaid (código-fonte em docs/planejamento/diagramas no repositório) e SVG; "
            "wireframes e mockups: HTML e CSS renderizados em imagem (docs/planejamento/prototipo). Todo o material "
            f"está no repositório GitHub do projeto (github.com/gabrielmenezes007).", alinhar="just")


def gerar_markdown():
    d = RAIZ / "docs" / "planejamento"
    md = [f"# Planejamento – {C.LOJA}\n",
          C.CONTEXTO + "\n",
          "## Arquivos\n",
          "- [Histórias de usuário](historias.md)\n- [Backlog, requisitos e tarefas](backlog-requisitos-tarefas.md)\n"
          "- [Casos de uso e UML](uml.md)\n- [IHC: telas, mapas, wireframes e mockups](ihc.md)\n"
          "- Protótipo navegável: [prototipo/index.html](prototipo/index.html)\n"]
    (d / "README.md").write_text("\n".join(md), encoding="utf-8")

    out = ["# Histórias de usuário\n", "## Mapa de afinidade\n", "![Mapa de afinidade](img/00-mapa-de-afinidade.png)\n"]
    for h in C.HISTORIAS:
        out.append(f"## {h['id']} – {h['titulo']}\n")
        out.append(f"- **Tema:** {C.TEMAS[h['tema']][0]}\n- **Requerente:** {h['requerente']}\n- **Ação:** {h['acao']}\n"
                   f"- **Comentários:** {h['comentarios']}\n- **Prioridade:** {h['prioridade']} · **Pontos:** {h['pontos']}\n")
        out.append("**Critérios de aceitação**\n")
        out += [f"{k}. {t}" for k, t in enumerate(h["ca"], 1)]
        out.append("\n**Regras de negócio:** " + ", ".join(h["rn"]) + "  \n**RNF:** " + ", ".join(h["rnf"]) + "\n")
    (d / "historias.md").write_text("\n".join(out), encoding="utf-8")

    out = ["# Backlog, requisitos e tarefas\n", "## Backlog priorizado\n", "| Ordem | ID | Tema | História | Pontos | Prioridade |", "|---|---|---|---|---|---|"]
    for i, u in enumerate(C.ORDEM_BACKLOG, 1):
        h = H[u]
        out.append(f"| {i} | {u} | {C.TEMAS[h['tema']][0]} | {h['acao']} | {h['pontos']} | {h['prioridade']} |")
    out += ["\n## Escala de prioridade\n"] + [f"- **{a}** – {b}" for a, b in C.ESCALA_PRIORIDADE]
    out += ["\n## Requisitos funcionais\n", "| ID | Requisito | Histórias |", "|---|---|---|"] + [f"| {a} | {b} | {', '.join(c)} |" for a, b, c in C.RFS]
    out += ["\n## Requisitos não funcionais\n", "| ID | Nome | Descrição |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in C.RNFS]
    out += ["\n## Regras de negócio\n", "| ID | Regra | Descrição |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in C.REGRAS]
    out += ["\n## Tarefas (2 a 12 h)\n", "| História | Tarefa | Horas |", "|---|---|---|"]
    for u in C.ORDEM_BACKLOG:
        out += [f"| {u} | {t} | {hh} |" for t, hh in C.TAREFAS[u]]
    out.append(f"\n**Total:** {sum(hh for v in C.TAREFAS.values() for _, hh in v)} horas")
    (d / "backlog-requisitos-tarefas.md").write_text("\n".join(out), encoding="utf-8")

    out = ["# Casos de uso e diagramas UML\n", "## Diagrama de caso de uso geral\n", "![Casos de uso](img/01-diagrama-casos-de-uso.png)\n"]
    for uc in C.CASOS_DE_USO:
        out.append(f"## {uc['id']} – {uc['nome']}\n")
        out.append(f"- **Atores:** {uc['atores']}\n- **Descrição:** {uc['descricao']}\n- **Pré-condições:** {uc['pre']}\n"
                   f"- **Pós-condições:** {uc['pos']}\n- **Histórias:** {uc['historias']}\n\n**Curso básico de ação**\n")
        out += [f"{i}. {p}" for i, p in enumerate(uc["basico"], 1)]
        for nome, passos in uc["alternativos"]:
            out.append(f"\n**Curso alternativo {nome}**\n")
            out += [f"- {p}" for p in passos]
        out.append("")
    out += ["## Diagrama de classes\n", "![Classes](img/03-diagrama-de-classes.png)\n",
            "## Diagramas de sequência\n", "![Login](img/04-sequencia-login.png)\n",
            "![Pedido e pagamento](img/05-sequencia-pedido-pagamento.png)\n", "![Status](img/06-sequencia-status-pedido.png)\n",
            "## Diagrama de atividades\n", "![Atividades](img/07-diagrama-de-atividades-compra.png)\n",
            "Os códigos-fonte dos diagramas estão em [diagramas/](diagramas/)."]
    (d / "uml.md").write_text("\n".join(out), encoding="utf-8")

    out = ["# IHC – telas, mapas, wireframes e mockups\n", "## Mapa conceitual\n", "![Mapa conceitual](img/08-mapa-conceitual.png)\n",
           "## Mapa navegacional\n", "![Mapa navegacional](img/09-mapa-navegacional.png)\n", "## Telas\n",
           "| ID | Tela | Wireframe | Mockup |", "|---|---|---|---|"]
    out += [f"| {t} | {n} | [ver](img/wireframes/{t}.png) | [ver](img/mockups/{t}.png) |" for t, n in C.TELAS]
    (d / "ihc.md").write_text("\n".join(out), encoding="utf-8")


def main(template, saida):
    doc = docx.Document(template)
    preencher_identificacao(doc)
    preencher_cartoes(doc)
    preencher_backlog(doc)
    secoes_finais(doc)
    doc.core_properties.author = C.ALUNO["nome"]
    doc.core_properties.title = f"Planejamento – {C.LOJA}"
    doc.save(saida)
    gerar_markdown()
    print("ok", saida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
