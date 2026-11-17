"""Checkout, pagamento e acompanhamento de pedidos (US10 a US18)."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.excecoes import ErroValidacao, EstoqueInsuficiente, RegraDeNegocio
from app.extensions import db
from app.models import Modalidade, Pedido, StatusPagamento, StatusPedido
from app.services import cep as servico_cep
from app.services import frete
from app.services import pedidos as servico
from app.services.carrinho import Carrinho
from app.services.pagamento import gerar_codigo_pix

bp = Blueprint("pedidos", __name__)


def _pedido_do_cliente(pedido_id):
    """RN12: o cliente só acessa os próprios pedidos."""
    pedido = db.get_or_404(Pedido, pedido_id)
    if pedido.usuario_id != current_user.id and not current_user.eh_admin:
        abort(403)
    return pedido


def _render_checkout(itens, form, erros=None, alerta=None, codigo=200):
    subtotal = sum(i.subtotal_centavos for i in itens)
    modalidade = form.get("modalidade", "ENTREGA")
    taxa = frete.calcular_taxa(Modalidade.RETIRADA if modalidade == "RETIRADA" else Modalidade.ENTREGA, subtotal)
    return render_template("pedidos/checkout.html", itens=itens, subtotal=subtotal, taxa=taxa,
                           taxa_entrega=frete.calcular_taxa(Modalidade.ENTREGA, subtotal),
                           form=form, modalidade=modalidade, erros=erros or {}, alerta=alerta,
                           pedido_minimo=frete.PEDIDO_MINIMO), codigo


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    carrinho = Carrinho(session)
    itens = carrinho.itens()
    if not itens:
        flash("Seu carrinho está vazio.", "aviso")
        return redirect(url_for("carrinho.ver"))
    if request.method == "POST":
        try:
            pedido = servico.criar_pedido(current_user, carrinho, request.form.get("modalidade"), request.form)
        except ErroValidacao as e:
            return _render_checkout(itens, request.form, e.erros, e.mensagem, 422)
        except RegraDeNegocio as e:
            return _render_checkout(itens, request.form, alerta=e.mensagem, codigo=422)
        return redirect(url_for("pedidos.pagamento", pedido_id=pedido.id))
    return _render_checkout(itens, {"modalidade": "ENTREGA"})


@bp.get("/cep/<cep>")
@login_required
def buscar_cep(cep):
    """US28: devolve rua e bairro do CEP em JSON (usado pelo JavaScript do checkout)."""
    return jsonify(servico_cep.buscar_endereco(cep))


def _render_pagamento(pedido, metodo="CREDITO", erros=None, alerta=None, form=None, codigo=200):
    return render_template("pedidos/pagamento.html", pedido=pedido, metodo=metodo, erros=erros or {},
                           alerta=alerta, form=form or {}, codigo_pix=gerar_codigo_pix(pedido)), codigo


@bp.get("/pedidos/<int:pedido_id>/pagamento")
@login_required
def pagamento(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    return _render_pagamento(pedido, request.args.get("metodo", "CREDITO").upper())


@bp.post("/pedidos/<int:pedido_id>/pagar")
@login_required
def pagar(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    metodo = (request.form.get("metodo") or "").upper()
    try:
        registro = servico.pagar_pedido(pedido, metodo, request.form)
    except ErroValidacao as e:
        return _render_pagamento(pedido, metodo or "CREDITO", e.erros, e.mensagem, request.form, 422)
    except EstoqueInsuficiente as e:
        return _render_pagamento(pedido, metodo or "CREDITO", alerta=e.mensagem, codigo=409)
    except RegraDeNegocio as e:
        flash(e.mensagem, "aviso")
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    if registro.status == StatusPagamento.RECUSADO:
        return render_template("pedidos/recusado.html", pedido=pedido, pagamento=registro)
    return redirect(url_for("pedidos.confirmado", pedido_id=pedido.id))


@bp.get("/pedidos/<int:pedido_id>/confirmado")
@login_required
def confirmado(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    if pedido.pagamento_aprovado is None:
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    return render_template("pedidos/confirmado.html", pedido=pedido)


@bp.get("/meus-pedidos")
@login_required
def lista():
    return render_template("pedidos/lista.html", pedidos=current_user.pedidos)


@bp.get("/pedidos/<int:pedido_id>")
@login_required
def detalhe(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    return render_template("pedidos/detalhe.html", pedido=pedido, StatusPedido=StatusPedido)


@bp.post("/pedidos/<int:pedido_id>/cancelar")
@login_required
def cancelar(pedido_id):
    pedido = _pedido_do_cliente(pedido_id)
    estava_pago = pedido.status == StatusPedido.PAGO
    try:
        servico.cancelar_pedido(pedido)
    except RegraDeNegocio as e:
        flash(e.mensagem, "erro")
    else:
        flash("Pedido cancelado." + (" O pagamento foi estornado." if estava_pago else ""), "ok")
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
