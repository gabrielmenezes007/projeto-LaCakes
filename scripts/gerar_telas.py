"""Gera o protótipo das telas (HTML) e as imagens de wireframe e mockup.

Uso: python scripts/gerar_telas.py
Saída:
  docs/planejamento/prototipo/<ID>.html          (protótipo navegável em modo mockup)
  docs/planejamento/img/wireframes/<ID>.png
  docs/planejamento/img/mockups/<ID>.png
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from conteudo_planejamento import TELAS  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PROTO = RAIZ / "docs" / "planejamento" / "prototipo"
IMG = RAIZ / "docs" / "planejamento" / "img"


def topo(qtd=3, logado=True):
    conta = '<span class="avatar" title="Minha conta">AS</span>' if logado else "Entrar"
    return (f'<div class="topo"><div class="logo">🧁 LaCakes<small>Cupcakes gourmet</small></div>'
            f'<div class="icones"><span class="carrinho-ico">🛒<span class="badge-n">{qtd}</span></span>'
            f'<span style="font-size:14px">{conta}</span></div></div>')


def topo_admin():
    return ('<div class="topo admin-topo"><div class="logo">🧁 LaCakes<small>Administração</small></div>'
            '<div class="icones"><span style="font-size:13px">Laysa (admin) · Sair</span></div></div>')


def nav(ativo):
    itens = [("🏠", "Vitrine"), ("🛒", "Carrinho"), ("📦", "Pedidos"), ("👤", "Conta")]
    return '<div class="rodape-nav">' + "".join(
        f'<div class="{"ativo" if n == ativo else ""}"><span>{i}</span>{n}</div>' for i, n in itens) + "</div>"


def card(nome, preco, cor, selo=""):
    s = f'<span class="selo">{selo}</span>' if selo == "Esgotado" else (f'<span class="selo ultimas">{selo}</span>' if selo else "")
    btn = '<div class="btn peq des">Esgotado</div>' if selo == "Esgotado" else '<div class="btn peq">+ Adicionar</div>'
    return (f'<div class="card">{s}<div class="img {cor}">🧁</div><div class="info">'
            f'<div class="nome">{nome}</div><div class="preco">R$ {preco}</div>{btn}</div></div>')


def campo(rot, valor="", ph="", erro="", dica=""):
    cls = "campo preenchido" if valor else "campo"
    if erro:
        cls += " invalido"
    h = f'<label>{rot}</label><div class="{cls}">{valor or ph}</div>'
    if erro:
        h += f'<div class="msg-campo">⚠ {erro}</div>'
    if dica:
        h += f'<div class="dica">{dica}</div>'
    return h


def item_carrinho(nome, preco, qtd, cor, total):
    return (f'<div class="item"><div class="img mini {cor}">🧁</div><div class="det"><b>{nome}</b>'
            f'<small>R$ {preco} cada</small><div class="qtd" style="margin:6px 0 0"><b>−</b><span>{qtd}</span><b>+</b>'
            f'<span class="remover">Remover</span></div></div><b>R$ {total}</b></div>')


RESUMO_ITENS = (item_carrinho("Red Velvet Clássico", "9,90", 2, "c1", "19,80")
                + item_carrinho("Ninho com Nutella", "12,90", 2, "c2", "25,80")
                + item_carrinho("Limão Siciliano", "9,50", 2, "c3", "19,00"))


def vitrine():
    return (topo() + '<div class="conteudo"><div class="banner"><b>Feitos hoje, fresquinhos 💗</b>'
            'Peça até 17h e receba no mesmo dia.</div><div class="chips"><span class="chip ativo">Todos</span>'
            '<span class="chip">Clássicos</span><span class="chip">Recheados</span><span class="chip">Zero açúcar</span></div>'
            '<div class="grade">' + card("Red Velvet Clássico", "9,90", "c1") + card("Ninho com Nutella", "12,90", "c2")
            + card("Limão Siciliano", "9,50", "c3", "Últimas unidades") + card("Cenoura com Brigadeiro", "11,50", "c4")
            + card("Chocolate 70% Zero Açúcar", "13,90", "c5") + card("Morango com Chantilly", "10,90", "c6", "Esgotado")
            + "</div></div>" + nav("Vitrine"))


def detalhe(alerta=""):
    return (topo() + '<div class="conteudo"><span class="voltar">← Voltar à vitrine</span>' + alerta
            + '<div class="img grande c3">🧁</div><h1 style="margin-top:12px">Limão Siciliano</h1>'
            '<span class="tag">Clássicos</span><div class="preco-g">R$ 9,50</div>'
            '<span class="selo ultimas" style="position:static">Últimas unidades: restam 4</span>'
            '<p style="margin-top:10px">Massa leve de limão siciliano com cobertura de merengue suíço maçaricado e raspas de limão.</p>'
            '<h2>Ingredientes</h2><p>Farinha de trigo, açúcar, ovos, manteiga, leite, suco e raspas de limão siciliano, claras.</p>'
            '<div class="contem"><b>Contém:</b> glúten, leite e ovos. Pode conter traços de castanhas.</div>'
            '<div class="qtd"><b>−</b><span>2</span><b>+</b><span style="font-weight:normal;color:#6B5E5A;font-size:13px">máx. 4 hoje</span></div>'
            '<div class="btn">Adicionar ao carrinho · R$ 19,00</div></div>' + nav("Vitrine"))


def login(erro=False):
    alerta = '<div class="alerta erro">⚠ <span>E-mail ou senha inválidos. Confira os dados e tente de novo.</span></div>' if erro else ""
    return (topo(3, False) + '<div class="conteudo"><h1>Entrar</h1><p>Acesse sua conta para finalizar o pedido.</p>'
            + alerta + campo("E-mail", "ana.souza@email.com" if erro else "", "seu@email.com")
            + campo("Senha", "••••••••" if erro else "", "Sua senha")
            + '<div style="height:18px"></div><div class="btn">Entrar</div>'
            '<p class="centro" style="margin-top:16px">Ainda não tem conta? <span class="link">Criar conta</span></p></div>' + nav("Conta"))


def cadastro(erro=False):
    if erro:
        corpo = (campo("Nome completo", "Ana Souza") + campo("E-mail", "ana.souza@email.com", erro="Este e-mail já possui conta. Faça login.")
                 + campo("Telefone (WhatsApp)", "(11) 98888-7777") + campo("Senha", "••••", erro="A senha precisa ter pelo menos 8 caracteres, com letras e números.")
                 + campo("Confirmar senha", "•••••", erro="As senhas não conferem."))
        topo_alerta = '<div class="alerta erro">⚠ <span>Corrija os campos destacados para continuar.</span></div>'
    else:
        corpo = (campo("Nome completo", ph="Como devemos te chamar?") + campo("E-mail", ph="seu@email.com")
                 + campo("Telefone (WhatsApp)", ph="(11) 90000-0000") + campo("Senha", ph="Crie uma senha", dica="Mínimo de 8 caracteres, com letras e números.")
                 + campo("Confirmar senha", ph="Repita a senha"))
        topo_alerta = ""
    return (topo(3, False) + '<div class="conteudo"><h1>Criar conta</h1>' + topo_alerta + corpo
            + '<div style="height:18px"></div><div class="btn">Criar conta</div>'
            '<p class="centro" style="margin-top:14px">Já tem conta? <span class="link">Entrar</span></p></div>' + nav("Conta"))


def carrinho():
    return (topo(6) + '<div class="conteudo"><h1>Meu carrinho</h1>' + RESUMO_ITENS
            + '<div class="caixa"><div class="linha"><span>Subtotal (6 itens)</span><b>R$ 64,60</b></div>'
            '<div class="linha"><span>Entrega</span><span>calculada no próximo passo</span></div></div>'
            '<div class="btn">Finalizar pedido</div><div class="btn sec">Continuar comprando</div></div>' + nav("Carrinho"))


def checkout(erro=False):
    alerta = ('<div class="alerta erro">⚠ <span>O pedido mínimo é de R$ 25,00. Adicione mais itens para continuar.</span></div>' if erro else "")
    cep = campo("CEP", "13010-000", erro="Ainda não entregamos neste CEP. Você pode escolher Retirar na loja.") if erro else campo("CEP", "04538-132")
    sub, taxa, total = ("19,80", "8,00", "27,80") if erro else ("64,60", "8,00", "72,60")
    return (topo(6) + '<div class="conteudo"><span class="voltar">← Voltar ao carrinho</span><h1>Entrega e resumo</h1>' + alerta
            + '<div class="opcoes"><div class="opcao sel"><b>🚚 Entrega</b>R$ 8,00 · grátis acima de R$ 120</div>'
            '<div class="opcao"><b>🏪 Retirar na loja</b>Sem taxa · R. das Flores, 120</div></div>'
            + cep + '<div class="duas"><div>' + campo("Rua", "" if erro else "Av. Brig. Faria Lima", "Rua / avenida")
            + '</div></div><div class="duas"><div>' + campo("Número", "" if erro else "1200", "Nº") + '</div><div>'
            + campo("Complemento", "" if erro else "Apto 52", "Opcional") + '</div></div>' + campo("Bairro", "" if erro else "Itaim Bibi", "Bairro")
            + f'<div class="caixa"><div class="linha"><span>Subtotal</span><span>R$ {sub}</span></div>'
            f'<div class="linha"><span>Entrega</span><span>R$ {taxa}</span></div><div class="linha total"><span>Total</span><span>R$ {total}</span></div></div>'
            '<div class="btn">Confirmar pedido</div></div>')


def pagamento():
    return (topo(0) + '<div class="conteudo"><h1>Pagamento</h1><div class="caixa"><div class="linha"><span>Pedido #1024</span><span></span></div>'
            '<div class="linha total"><span>Total a pagar</span><span>R$ 72,60</span></div></div>'
            '<div class="abas"><div class="ativo">💳 Crédito</div><div>💳 Débito</div><div>⚡ Pix</div></div>'
            + campo("Nome impresso no cartão", "ANA SOUZA") + campo("Número do cartão", "4111 1111 1111 1111")
            + '<div class="duas"><div>' + campo("Validade", "08/28") + '</div><div>' + campo("CVV", "•••") + '</div></div>'
            '<div style="height:16px"></div><div class="btn verde">🔒 Pagar R$ 72,60</div>'
            '<p class="demo">Ambiente de demonstração: o pagamento é simulado e nenhum valor é cobrado.</p></div>')


def confirmado():
    return (topo(0) + '<div class="conteudo centro"><div class="icone-g">✅</div><h1>Pedido #1024 confirmado!</h1>'
            '<p>Pagamento aprovado. A confeitaria já recebeu seu pedido.</p><div class="caixa" style="text-align:left">'
            '<div class="linha"><span>6 cupcakes</span><span>R$ 64,60</span></div><div class="linha"><span>Entrega</span><span>R$ 8,00</span></div>'
            '<div class="linha total"><span>Total pago</span><span>R$ 72,60</span></div>'
            '<div class="linha"><span>Forma de pagamento</span><span>Crédito •••• 1111</span></div>'
            '<p style="margin-top:10px"><b>Entrega em:</b> Av. Brig. Faria Lima, 1200 – Apto 52, Itaim Bibi</p></div>'
            '<div class="btn">Acompanhar pedido</div><div class="btn sec">Voltar à vitrine</div></div>' + nav("Pedidos"))


def meus_pedidos():
    def ped(n, data, total, st, cls):
        return (f'<div class="pedido"><div class="linha"><b>Pedido #{n}</b><span class="status {cls}">{st}</span></div>'
                f'<div class="linha"><span>{data}</span><b>R$ {total}</b></div><span class="link">Ver detalhes →</span></div>')
    return (topo(0) + '<div class="conteudo"><h1>Meus pedidos</h1>' + ped("1024", "14/11 · 14:02", "72,60", "Pago", "s-pago")
            + ped("1017", "08/11 · 10:40", "45,40", "Entregue", "s-ent") + ped("1009", "30/10 · 16:15", "38,00", "Entregue", "s-ent")
            + ped("1003", "21/10 · 09:12", "29,80", "Cancelado", "s-canc") + "</div>" + nav("Pedidos"))


def acompanhamento():
    passos = [("feito", "Pedido recebido", "14/11 às 14:02"), ("feito", "Pagamento aprovado", "14/11 às 14:03"),
              ("atual", "Em preparo", "aguardando a confeitaria"), ("pend", "Saiu para entrega", ""), ("pend", "Entregue", "")]
    tl = "".join(f'<div class="passo {c}"><b>{t}</b><small>{s}</small></div>' for c, t, s in passos)
    return (topo(0) + '<div class="conteudo"><span class="voltar">← Meus pedidos</span><h1>Pedido #1024</h1>'
            '<span class="status s-pago">Pago</span><div class="caixa"><h2 style="margin-top:0">Andamento</h2>' + tl + '</div>'
            '<div class="caixa"><div class="linha"><span>2× Red Velvet Clássico</span><span>R$ 19,80</span></div>'
            '<div class="linha"><span>2× Ninho com Nutella</span><span>R$ 25,80</span></div><div class="linha"><span>2× Limão Siciliano</span><span>R$ 19,00</span></div>'
            '<div class="linha total"><span>Total</span><span>R$ 72,60</span></div></div>'
            '<div class="btn sec">Cancelar pedido</div><p class="demo">É possível cancelar até o pedido entrar em preparo.</p></div>' + nav("Pedidos"))


def admin_produtos():
    def linha(nome, preco, est, cor, ativo=True):
        st = '<span class="status s-ent">Ativo</span>' if ativo else '<span class="status s-ag">Inativo</span>'
        return (f'<div class="prod-adm {"" if ativo else "inativo"}"><div class="img mini {cor}">🧁</div><div class="det"><b>{nome}</b><br>R$ {preco} · {st}'
                f'<br><span class="link">Editar</span></div><div class="centro"><small>Estoque</small><div class="estq">{est}</div></div></div>')
    return (topo_admin() + '<div class="conteudo"><div class="admin-abas"><div class="ativo">Produtos</div><div>Pedidos</div></div>'
            '<div class="alerta ok">✔ <span>Produto salvo.</span></div><div class="btn" style="margin-bottom:12px">+ Novo cupcake</div>'
            + linha("Red Velvet Clássico", "9,90", 18, "c1") + linha("Ninho com Nutella", "12,90", 24, "c2")
            + linha("Limão Siciliano", "9,50", 4, "c3") + linha("Morango com Chantilly", "10,90", 0, "c6")
            + linha("Panetone Trufado (Natal)", "15,90", 0, "c5", ativo=False)
            + '<div class="btn sec">Salvar estoques do dia</div></div>')


def admin_form():
    return (topo_admin() + '<div class="conteudo"><span class="voltar">← Produtos</span><h1>Novo cupcake</h1>'
            + campo("Nome *", "Pistache com Frutas Vermelhas") + campo("Categoria *", "Recheados ▾")
            + campo("Descrição", "Massa de pistache, recheio de geleia de frutas vermelhas.")
            + campo("Ingredientes", "Farinha, pistache, açúcar, ovos, manteiga, frutas vermelhas")
            + campo("Alergênicos", "Glúten, leite, ovos, castanhas")
            + '<div class="duas"><div>' + campo("Preço (R$) *", "14,90") + '</div><div>' + campo("Estoque do dia *", "20") + '</div></div>'
            '<label>Foto</label><div class="upload">📷 Toque para escolher uma imagem<br><small>JPG ou PNG até 2 MB · opcional</small></div>'
            '<div class="check"><b>✓</b> Produto ativo (aparece na vitrine)</div>'
            '<div class="btn">Salvar produto</div><div class="btn sec">Cancelar</div></div>')


def admin_pedidos():
    def ped(n, cli, mod, total, st, cls, acao):
        b = f'<div class="btn peq" style="margin-top:8px">{acao}</div>' if acao else ""
        return (f'<div class="pedido"><div class="linha"><b>#{n} · {cli}</b><span class="status {cls}">{st}</span></div>'
                f'<div class="linha"><span>{mod} · 14/11</span><b>R$ {total}</b></div>{b}</div>')
    return (topo_admin() + '<div class="conteudo"><div class="admin-abas"><div>Produtos</div><div class="ativo">Pedidos</div></div>'
            '<label style="margin-top:0">Filtrar por status</label><div class="campo preenchido">Todos ▾</div>'
            '<div class="alerta ok" style="margin-top:12px">✔ <span>Status do pedido #1022 atualizado para Saiu para entrega.</span></div>'
            + ped("1024", "Ana Souza", "Entrega", "72,60", "Pago", "s-pago", "Avançar → Em preparo")
            + ped("1023", "Bruno Lima", "Retirada", "39,60", "Em preparo", "s-prep", "Avançar → Pronto para retirada")
            + ped("1022", "Carla Dias", "Entrega", "128,40", "Saiu para entrega", "s-saiu", "Avançar → Entregue")
            + ped("1021", "Diego Reis", "Entrega", "31,90", "Aguardando pagamento", "s-ag", "") + "</div>")


def carrinho_vazio():
    return (topo(0) + '<div class="conteudo centro"><div class="icone-g">🛒</div><h1>Seu carrinho está vazio</h1>'
            '<p>Que tal escolher alguns cupcakes fresquinhos de hoje?</p><div style="height:16px"></div>'
            '<div class="btn">Ver a vitrine</div></div>' + nav("Carrinho"))


def pagamento_recusado():
    return (topo(0) + '<div class="conteudo centro"><div class="icone-g">💳❌</div><h1>Pagamento recusado</h1>'
            '<div class="alerta erro" style="text-align:left">⚠ <span>O cartão final 0000 não foi aprovado. <b>Nenhum valor foi cobrado.</b></span></div>'
            '<p>Seu pedido #1024 continua guardado como <b>Aguardando pagamento</b>. Você pode tentar outro cartão ou pagar com Pix.</p>'
            '<div style="height:12px"></div><div class="btn">Tentar novamente</div><div class="btn sec">Ver meus pedidos</div></div>')


def estoque_insuficiente():
    return detalhe('<div class="alerta erro">⚠ <span>Só temos 4 unidades deste sabor hoje. Ajuste a quantidade para adicionar.</span></div>')


def erro_404():
    return (topo(0) + '<div class="conteudo centro"><div class="cod-erro">404</div><div class="icone-g" style="margin-top:0">🧁❓</div>'
            '<h1>Página não encontrada</h1><p>O cupcake ou a página que você procurou não existe ou saiu da vitrine.</p>'
            '<div style="height:16px"></div><div class="btn">Voltar à vitrine</div></div>' + nav(""))


def erro_403():
    return (topo(0) + '<div class="conteudo centro"><div class="cod-erro">403</div><div class="icone-g" style="margin-top:0">🔒</div>'
            '<h1>Acesso negado</h1><p>Você não tem permissão para ver esta página. Se acha que isso é um engano, entre com outra conta.</p>'
            '<div style="height:16px"></div><div class="btn">Voltar à vitrine</div><div class="btn sec">Entrar com outra conta</div></div>' + nav(""))


GERADORES = {
    "TELA01": vitrine, "TELA02": detalhe, "TELA03": login, "TELA04": cadastro, "TELA05": carrinho,
    "TELA06": checkout, "TELA07": pagamento, "TELA08": confirmado, "TELA09": meus_pedidos,
    "TELA10": acompanhamento, "TELA11": admin_produtos, "TELA12": admin_form, "TELA13": admin_pedidos,
    "ERRO01": lambda: login(True), "ERRO02": lambda: cadastro(True), "ERRO03": carrinho_vazio,
    "ERRO04": lambda: checkout(True), "ERRO05": pagamento_recusado, "ERRO06": estoque_insuficiente,
    "ERRO07": erro_404, "ERRO08": erro_403,
}


def pagina(tid, nome, corpo, wf=False):
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{tid} – {nome}</title>'
            f'<link rel="stylesheet" href="estilo.css"></head><body class="{"wf" if wf else ""}">'
            f'<div id="quadro" style="display:inline-block"><p class="rotulo">{tid} · {nome}</p><div class="tela">{corpo}</div></div></body></html>')


def main():
    (IMG / "wireframes").mkdir(parents=True, exist_ok=True)
    (IMG / "mockups").mkdir(parents=True, exist_ok=True)
    nomes = dict(TELAS)
    with sync_playwright() as p:
        nav_ = p.chromium.launch(channel="msedge", headless=True)
        pg = nav_.new_page(device_scale_factor=2, viewport={"width": 460, "height": 900})
        for tid, ger in GERADORES.items():
            corpo = ger()
            for wf, pasta in ((False, "mockups"), (True, "wireframes")):
                arq = PROTO / (f"{tid}{'-wf' if wf else ''}.html")
                arq.write_text(pagina(tid, nomes[tid], corpo, wf), encoding="utf-8")
                pg.goto(arq.as_uri())
                pg.wait_for_timeout(80)
                pg.locator("#quadro").screenshot(path=str(IMG / pasta / f"{tid}.png"))
                if wf:
                    arq.unlink()
            print("ok", tid)
        nav_.close()
    # índice navegável do protótipo
    links = "".join(f'<li><a href="{t}.html">{t} – {n}</a></li>' for t, n in TELAS)
    (PROTO / "index.html").write_text(
        f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Protótipo LaCakes</title></head>'
        f'<body style="font-family:Arial;padding:20px"><h1>Protótipo de telas – LaCakes</h1><ul>{links}</ul></body></html>',
        encoding="utf-8")


if __name__ == "__main__":
    main()
