"""Carrinho de compras (US08 e US09)."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.excecoes import RegraDeNegocio
from app.extensions import db
from app.models import Produto
from app.services.carrinho import Carrinho
from app.services.frete import PEDIDO_MINIMO
from app.utils import para_inteiro, url_segura

bp = Blueprint("carrinho", __name__, url_prefix="/carrinho")


@bp.get("/")
def ver():
    carrinho = Carrinho(session)
    itens = carrinho.itens()
    subtotal = sum(i.subtotal_centavos for i in itens)
    return render_template("carrinho/carrinho.html", itens=itens, subtotal=subtotal, pedido_minimo=PEDIDO_MINIMO)


@bp.post("/adicionar/<int:produto_id>")
def adicionar(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    quantidade = para_inteiro(request.form.get("quantidade"), 1)
    voltar = request.form.get("voltar")
    destino = voltar if url_segura(voltar) else url_for("vitrine.produto", produto_id=produto_id)
    try:
        Carrinho(session).adicionar(produto, quantidade)
    except RegraDeNegocio as e:
        flash(e.mensagem, "erro")
        return redirect(destino)
    unidade = "unidade" if quantidade == 1 else "unidades"
    flash(f"{quantidade} {unidade} de {produto.nome} no carrinho.", "ok")
    return redirect(destino)


@bp.post("/atualizar/<int:produto_id>")
def atualizar(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    quantidade = para_inteiro(request.form.get("quantidade"), 0)
    try:
        Carrinho(session).atualizar(produto, quantidade)
    except RegraDeNegocio as e:
        flash(e.mensagem, "erro")
    return redirect(url_for("carrinho.ver"))


@bp.post("/remover/<int:produto_id>")
def remover(produto_id):
    Carrinho(session).remover(produto_id)
    flash("Item removido do carrinho.", "ok")
    return redirect(url_for("carrinho.ver"))
