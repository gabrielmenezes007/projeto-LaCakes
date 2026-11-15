"""Cadastro, login e logout (US05 a US07)."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.excecoes import ErroValidacao
from app.services import contas
from app.utils import url_segura

bp = Blueprint("auth", __name__)


def _destino_apos_login():
    destino = request.args.get("next") or request.form.get("next")
    return destino if url_segura(destino) else url_for("vitrine.index")


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("vitrine.index"))
    if request.method == "POST":
        try:
            usuario = contas.cadastrar_cliente(request.form.get("nome"), request.form.get("email"),
                                               request.form.get("telefone"), request.form.get("senha"),
                                               request.form.get("confirmacao"))
        except ErroValidacao as e:
            return render_template("auth/cadastro.html", erros=e.erros, mensagem=e.mensagem,
                                   form=request.form), 422
        login_user(usuario)
        session.permanent = True
        flash("Conta criada com sucesso. Boas compras!", "ok")
        return redirect(_destino_apos_login())
    return render_template("auth/cadastro.html", erros={}, form={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("vitrine.index"))
    if request.method == "POST":
        usuario = contas.autenticar(request.form.get("email"), request.form.get("senha"))
        if usuario is None:
            return render_template("auth/login.html", erro="E-mail ou senha inválidos. Confira os dados e tente de novo.",
                                   form=request.form), 401
        login_user(usuario)  # o carrinho da sessão é mantido (US06)
        session.permanent = True
        flash(f"Olá, {usuario.primeiro_nome}!", "ok")
        return redirect(_destino_apos_login())
    return render_template("auth/login.html", form={})


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()  # limpa também o carrinho (US07: outra pessoa pode usar o mesmo aparelho)
    flash("Você saiu da sua conta.", "ok")
    return redirect(url_for("vitrine.index"))
