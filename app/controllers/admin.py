"""Área administrativa: produtos, estoque do dia e pedidos (US19 a US23)."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.excecoes import ErroValidacao, RegraDeNegocio
from app.extensions import db, login_manager
from app.models import Pedido, Produto, StatusPedido
from app.services import pedidos as servico_pedidos
from app.services import produtos as servico_produtos
from app.utils import centavos_para_texto

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
def exigir_admin():
    """RN13: só administradores. Visitante vai para o login; cliente recebe 403."""
    if not current_user.is_authenticated:
        return login_manager.unauthorized()
    if not current_user.eh_admin:
        abort(403)
    return None


@bp.get("/")
def inicio():
    return redirect(url_for("admin.produtos"))


@bp.get("/produtos")
def produtos():
    lista = db.session.scalars(db.select(Produto).order_by(Produto.ativo.desc(), Produto.nome)).all()
    return render_template("admin/produtos.html", produtos=lista, erros={}, area_admin=True)


@bp.post("/produtos/estoque")
def salvar_estoques():
    valores = {int(chave.split("_", 1)[1]): valor for chave, valor in request.form.items()
               if chave.startswith("estoque_") and chave.split("_", 1)[1].isdigit()}
    try:
        total = servico_produtos.atualizar_estoques(valores)
    except ErroValidacao as e:
        lista = db.session.scalars(db.select(Produto).order_by(Produto.ativo.desc(), Produto.nome)).all()
        return render_template("admin/produtos.html", produtos=lista, erros=e.erros, alerta=e.mensagem,
                               valores=request.form, area_admin=True), 422
    flash(f"Estoque do dia salvo ({total} produtos).", "ok")
    return redirect(url_for("admin.produtos"))


def _form_de_produto(produto):
    return {"nome": produto.nome, "categoria_id": str(produto.categoria_id), "descricao": produto.descricao or "",
            "ingredientes": produto.ingredientes or "", "alergenicos": produto.alergenicos or "",
            "preco": centavos_para_texto(produto.preco_centavos), "estoque": str(produto.estoque),
            "ativo": "on" if produto.ativo else ""}


@bp.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    if request.method == "POST":
        try:
            produto = servico_produtos.salvar_produto(request.form, request.files.get("imagem"))
        except ErroValidacao as e:
            return render_template("admin/produto_form.html", produto=None, form=request.form, erros=e.erros,
                                   alerta=e.mensagem, categorias=servico_produtos.categorias(),
                                   area_admin=True), 422
        flash(f"Produto \"{produto.nome}\" salvo.", "ok")
        return redirect(url_for("admin.produtos"))
    return render_template("admin/produto_form.html", produto=None, form={"ativo": "on", "estoque": "0"}, erros={},
                           categorias=servico_produtos.categorias(), area_admin=True)


@bp.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
def editar_produto(produto_id):
    produto = db.get_or_404(Produto, produto_id)
    if request.method == "POST":
        try:
            servico_produtos.salvar_produto(request.form, request.files.get("imagem"), produto)
        except ErroValidacao as e:
            db.session.rollback()
            return render_template("admin/produto_form.html", produto=produto, form=request.form, erros=e.erros,
                                   alerta=e.mensagem, categorias=servico_produtos.categorias(),
                                   area_admin=True), 422
        flash(f"Produto \"{produto.nome}\" salvo.", "ok")
        return redirect(url_for("admin.produtos"))
    return render_template("admin/produto_form.html", produto=produto, form=_form_de_produto(produto), erros={},
                           categorias=servico_produtos.categorias(), area_admin=True)


@bp.get("/pedidos")
def pedidos():
    filtro = request.args.get("status") or ""
    try:
        status = StatusPedido(filtro) if filtro else None
    except ValueError:
        status, filtro = None, ""
    lista = servico_pedidos.pedidos_para_admin(status)
    return render_template("admin/pedidos.html", pedidos=lista, filtro=filtro, todos_status=list(StatusPedido),
                           area_admin=True)


@bp.post("/pedidos/<int:pedido_id>/avancar")
def avancar(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id)
    try:
        novo = servico_pedidos.avancar_pedido(pedido)
    except RegraDeNegocio as e:
        flash(f"Pedido #{pedido.id}: {e.mensagem}", "erro")
    else:
        flash(f"Status do pedido #{pedido.id} atualizado para {novo.rotulo}.", "ok")
    return redirect(url_for("admin.pedidos", status=request.form.get("filtro") or None))
