"""Gera os formulários de teste com usuários (Word) e a capa da consolidação.

Uso: python scripts/gerar_formularios_teste.py <pasta_de_saida> [quantidade]
Saída:
  <pasta>/Formulario_Teste_Testador_1.docx ... _5.docx   (um para cada testador preencher)
  <pasta>/00_Capa_Consolidacao.docx                     (resumo, problemas consolidados e laudo)
Depois de preenchidos, junte tudo num PDF com: scripts/consolidar_testes.ps1 <pasta>
"""
import pathlib
import sys

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROXO = RGBColor(0x5D, 0x24, 0x52)
VERDE = RGBColor(0x11, 0x2F, 0x24)
FUNDO = "EADBE6"

CENARIOS = [
    ("Ver a vitrine e filtrar por categoria", "Abrir a página inicial e tocar em Clássicos, Recheados etc."),
    ("Ver os detalhes de um cupcake", "Abrir um cupcake e conferir ingredientes e alergênicos (\"Contém:\")."),
    ("Criar uma conta nova", "Tela Criar conta. Testar também senha fraca e e-mail já cadastrado."),
    ("Entrar e sair da conta", "Testar senha errada e depois a certa. Sair pelo menu das iniciais."),
    ("Montar o carrinho", "Adicionar sabores, alterar quantidades com − e +, remover um item."),
    ("Limite de estoque", "Tentar colocar mais de 4 unidades de Limão Siciliano."),
    ("Finalizar com entrega em Jaú", "CEP 17201-000 e endereço completo. Conferir taxa e total."),
    ("CEP fora da área de entrega", "Tentar o CEP 13010-000."),
    ("Retirar na loja", "Escolher Retirar na loja e conferir que a taxa some."),
    ("Pagar com cartão de crédito", "Cartão 4111 1111 1111 1111, validade futura, CVV 123."),
    ("Pagar com cartão de débito", "Mesmos dados, na aba Débito."),
    ("Pagar com Pix", "Aba Pix: copiar o código e tocar em Já paguei."),
    ("Pagamento recusado", "Cartão terminado em 0000; depois Tentar novamente."),
    ("Acompanhar o pedido", "Meus pedidos → abrir o pedido → ver a linha do tempo."),
    ("Cancelar um pedido", "Cancelar um pedido que ainda não entrou em preparo."),
    ("Admin: cadastrar um cupcake", "Entrar como administradora, Novo cupcake (testar também preço inválido)."),
    ("Admin: estoque do dia e desativar", "Alterar estoques e salvar; desativar um sabor e ver se sumiu da vitrine."),
    ("Admin: avançar o status de um pedido", "Aba Pedidos → Avançar. Depois conferir na conta do cliente."),
    ("Aparência no celular (opcional)", "Se possível, testar em tela estreita (F12 → modo celular no navegador)."),
]


def fonte(run, tam=None, negrito=None, cor=None, italico=None):
    run.font.name = "Arial"
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "Arial")
    if tam:
        run.font.size = Pt(tam)
    if negrito is not None:
        run.bold = negrito
    if cor:
        run.font.color.rgb = cor
    if italico:
        run.italic = True
    return run


def par(doc, texto="", tam=10, negrito=False, cor=None, depois=4, italico=False, alinhar=None):
    p = doc.add_paragraph()
    if texto:
        fonte(p.add_run(texto), tam, negrito, cor, italico)
    p.paragraph_format.space_after = Pt(depois)
    if alinhar == "centro":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def titulo(doc, texto, tam=13):
    p = par(doc, texto, tam, True, VERDE, 6)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.keep_with_next = True
    return p


def bordas(tabela):
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{lado}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "999999")
        b.append(e)
    tabela._tbl.tblPr.append(b)


def sombra(celula, cor=FUNDO):
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), cor)
    celula._tc.get_or_add_tcPr().append(s)


def texto_celula(celula, texto, tam=9, negrito=False):
    p = celula.paragraphs[0]
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    fonte(p.add_run(texto), tam, negrito)


def tabela(doc, cabecalho, linhas, larguras, altura_linha=None):
    t = doc.add_table(rows=1 + len(linhas), cols=len(cabecalho))
    bordas(t)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, c in enumerate(cabecalho):
        texto_celula(t.rows[0].cells[i], c, 9, True)
        sombra(t.rows[0].cells[i])
    for li, linha in enumerate(linhas, 1):
        for ci, valor in enumerate(linha):
            texto_celula(t.rows[li].cells[ci], valor)
        if altura_linha:
            t.rows[li].height = Cm(altura_linha)
    for row in t.rows:
        for ci, w in enumerate(larguras):
            row.cells[ci].width = Cm(w)
        nao_partir = OxmlElement("w:cantSplit")  # a linha não é dividida entre duas páginas
        nao_partir.set(qn("w:val"), "true")
        row._tr.get_or_add_trPr().append(nao_partir)
    par(doc, depois=2)
    return t


def caixa(doc, rotulo, linhas_vazias=5, dica=""):
    titulo(doc, rotulo, 11)
    if dica:
        par(doc, dica, 9, italico=True, cor=RGBColor(0x55, 0x55, 0x55))
    t = doc.add_table(rows=1, cols=1)
    bordas(t)
    c = t.rows[0].cells[0]
    for _ in range(linhas_vazias - 1):
        c.add_paragraph()
    par(doc, depois=2)


def novo_documento():
    d = docx.Document()
    s = d.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2)
    s.top_margin = s.bottom_margin = Cm(1.8)
    return d


def formulario(numero):
    d = novo_documento()
    par(d, "LaCakes Cupcakes Gourmet", 18, True, ROXO, 0, alinhar="centro")
    par(d, f"Formulário de teste do sistema – Testador {numero}", 13, True, VERDE, 10, alinhar="centro")
    par(d, "Obrigado por testar! Use o sistema como um cliente e como a dona da loja usariam. Marque o resultado de "
           "cada cenário e descreva com sinceridade o que não funcionou: os problemas encontrados ajudam a melhorar o "
           "sistema. Para registrar um erro, tire uma captura de tela (Windows: tecla Windows + Shift + S) e cole no "
           "fim deste formulário.", 10)
    par(d, "Contas de teste – Cliente: cliente@lacakes.test · Administradora: admin@lacakes.test "
           "(senhas informadas pelo responsável pelo teste). Os pagamentos são simulados: nenhum valor é cobrado.",
        9, italico=True)

    titulo(d, "1. Identificação")
    tabela(d, ["Campo", "Resposta"], [
        ["Nome de quem testou", ""], ["Data do teste", "___/___/______"], ["Horário (início – fim)", ""],
        ["Perfil", "(  ) Colega de curso   (  ) Profissional da área   (  ) Outro: ____________"],
        ["Navegador e aparelho", ""],
    ], [5, 12], 0.8)

    titulo(d, "2. Roteiro de cenários")
    par(d, "Marque com X uma das colunas. Use \"Obs.\" para detalhes ou para o número da captura de tela.", 9,
        italico=True)
    linhas = [[str(i), f"{nome}\n{como}", "", "", "", ""] for i, (nome, como) in enumerate(CENARIOS, 1)]
    t = tabela(d, ["#", "Cenário / como testar", "Funcionou", "Não funcionou", "Não testei", "Obs."], linhas,
               [0.8, 8.2, 1.8, 1.8, 1.8, 2.6])
    for row in t.rows[1:]:
        cel = row.cells[1]
        p = cel.paragraphs[0]
        nome_run = p.runs[0]
        nome, como = nome_run.text.split("\n", 1)
        nome_run.text = nome
        nome_run.bold = True
        fonte(cel.add_paragraph().add_run(como), 8, italico=True)

    caixa(d, "3. O que testou e FUNCIONOU", 6, "Descreva as funcionalidades que você usou e que deram certo.")
    titulo(d, "4. O que testou e NÃO FUNCIONOU – e o que deve ser corrigido", 11)
    par(d, "Um problema por linha. Gravidade: Alta (impede a compra), Média (atrapalha), Baixa (detalhe visual).", 9,
        italico=True)
    tabela(d, ["#", "Funcionalidade", "O que aconteceu", "O que deveria acontecer / como corrigir", "Gravidade",
               "Captura nº"], [[str(i), "", "", "", "", ""] for i in range(1, 6)], [0.8, 3.2, 4.4, 4.6, 1.8, 1.8], 1.4)
    caixa(d, "5. Funcionalidades NÃO testadas – e por quê", 5,
          "Ex.: faltou tempo, não encontrei a opção, não entendi como usar, a funcionalidade não existe no sistema.")
    caixa(d, "6. Sugestões de melhoria", 5)
    titulo(d, "7. Avaliação geral", 11)
    tabela(d, ["Pergunta", "Resposta (1 = muito ruim, 5 = ótimo)"], [
        ["Facilidade de uso", "(  ) 1   (  ) 2   (  ) 3   (  ) 4   (  ) 5"],
        ["Aparência e organização das telas", "(  ) 1   (  ) 2   (  ) 3   (  ) 4   (  ) 5"],
        ["Clareza das mensagens de erro", "(  ) 1   (  ) 2   (  ) 3   (  ) 4   (  ) 5"],
        ["Você compraria cupcakes por este sistema?", "(  ) Sim   (  ) Talvez   (  ) Não"],
    ], [8, 9], 0.8)
    titulo(d, "8. Capturas de tela", 11)
    par(d, "Cole aqui as capturas, numerando como \"Captura 1\", \"Captura 2\"... (as mesmas citadas no item 4).", 9,
        italico=True)
    caixa(d, "Capturas", 10)
    titulo(d, "9. Autorização", 11)
    par(d, "(  ) Autorizo o uso das respostas deste formulário, com meu nome, na documentação do projeto.", 10)
    par(d, "Assinatura: ________________________________________", 10)
    return d


def capa_consolidacao(quantidade):
    d = novo_documento()
    par(d, "LaCakes Cupcakes Gourmet", 18, True, ROXO, 0, alinhar="centro")
    par(d, f"Testes com usuários – consolidação das {quantidade} avaliações", 14, True, VERDE, 10, alinhar="centro")
    titulo(d, "1. Como os testes foram feitos")
    par(d, "Cada testador usou o sistema no computador do responsável pelo projeto (execução local com iniciar.bat), "
           "seguiu o roteiro de cenários e preencheu o formulário de teste. Os formulários originais estão anexados "
           "a seguir, na ordem dos testadores.")
    tabela(d, ["Item", "Informação"], [["Período dos testes", "a preencher"], ["Local / forma", "a preencher"],
                                       ["Versão testada (commit)", "a preencher"]], [5, 12], 0.7)
    titulo(d, "2. Resumo por testador")
    tabela(d, ["Testador", "Data", "Cenários que funcionaram", "Problemas encontrados", "Não testados", "Nota média"],
           [[f"{i}. a preencher", "", "", "", "", ""] for i in range(1, quantidade + 1)],
           [3.4, 1.8, 3.2, 3.6, 2.6, 2.0], 1.0)
    titulo(d, "3. Problemas consolidados e correções")
    par(d, "Junte os problemas iguais apontados por mais de um testador. Na coluna Correção, diga o que foi alterado "
           "no sistema (ou por que não foi corrigido) e o commit correspondente.", 9, italico=True)
    tabela(d, ["#", "Problema", "Testadores", "Gravidade", "Correção feita", "Commit"],
           [[str(i), "", "", "", "", ""] for i in range(1, 7)], [0.8, 4.6, 2.2, 1.8, 5.4, 1.8], 1.2)
    titulo(d, "4. Sugestões de melhoria recebidas")
    tabela(d, ["Sugestão", "Testadores", "Decisão (feita / futura / descartada) e motivo"],
           [["", "", ""] for _ in range(4)], [6.5, 2.5, 8.6], 1.0)
    titulo(d, "5. Laudo de qualidade")
    par(d, "a preencher após os testes: conclusão sobre a qualidade do sistema, com base nos testes automatizados "
           "(123 testes aprovados, 95% de cobertura) e nas avaliações dos usuários.", 10, italico=True)
    caixa(d, "Laudo", 8)
    titulo(d, "6. Anexos – formulários originais dos testadores")
    par(d, "Os formulários preenchidos seguem nas próximas páginas.", 10)
    return d


def main():
    saida = pathlib.Path(sys.argv[1])
    quantidade = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    saida.mkdir(parents=True, exist_ok=True)
    for i in range(1, quantidade + 1):
        formulario(i).save(saida / f"Formulario_Teste_Testador_{i}.docx")
    capa_consolidacao(quantidade).save(saida / "00_Capa_Consolidacao.docx")
    print(f"{quantidade} formulários e a capa da consolidação gerados em {saida}")


if __name__ == "__main__":
    main()
