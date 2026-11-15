"""Vitrine virtual: lista de cupcakes e página de detalhes (US01 a US04)."""
from flask import Blueprint, abort, render_template, request, session

from app.extensions import db
from app.models import Produto
from app.services import produtos
from app.services.carrinho import MAXIMO_POR_ITEM, Carrinho
from app.utils import para_inteiro

bp = Blueprint("vitrine", __name__)


@bp.get("/")
def index():
    categoria_id = para_inteiro(request.args.get("categoria"))
    categorias = produtos.categorias()
    categoria_ativa = next((c for c in categorias if c.id == categoria_id), None)
    lista = produtos.produtos_da_vitrine(categoria_ativa.id if categoria_ativa else None)
    return render_template("vitrine/index.html", produtos=lista, categorias=categorias,
                           categoria_ativa=categoria_ativa)


@bp.get("/produto/<int:produto_id>")
def produto(produto_id):
    item = db.session.get(Produto, produto_id)
    if item is None or not item.ativo:
        abort(404)
    no_carrinho = Carrinho(session).quantidade_de(item.id)
    maximo = max(0, min(item.estoque, MAXIMO_POR_ITEM) - no_carrinho)
    return render_template("vitrine/produto.html", produto=item, no_carrinho=no_carrinho, maximo=maximo)
