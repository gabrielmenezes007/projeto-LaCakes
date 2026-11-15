"""Páginas amigáveis de erro (RNF10): 400, 403, 404, 413 e 500."""
from flask import render_template
from flask_wtf.csrf import CSRFError

from app.extensions import db

MENSAGENS = {
    400: ("Requisição inválida", "Não conseguimos entender o envio do formulário. Volte e tente de novo."),
    403: ("Acesso negado", "Você não tem permissão para ver esta página. Se acha que isso é um engano, "
                           "entre com outra conta."),
    404: ("Página não encontrada", "O cupcake ou a página que você procurou não existe ou saiu da vitrine."),
    413: ("Arquivo muito grande", "A imagem enviada passa de 2 MB. Escolha uma foto menor."),
    500: ("Algo deu errado", "Tivemos um problema inesperado. Tente de novo em alguns instantes."),
}


def pagina_de_erro(codigo, titulo=None, mensagem=None):
    t, m = MENSAGENS[codigo]
    return render_template("erros/erro.html", codigo=codigo, titulo=titulo or t, mensagem=mensagem or m), codigo


def registrar(app):
    @app.errorhandler(CSRFError)
    def erro_csrf(_e):
        return pagina_de_erro(400, "Página expirada", "O formulário ficou aberto por muito tempo ou veio de "
                                                      "outro lugar. Volte, recarregue a página e tente de novo.")

    @app.errorhandler(400)
    def erro_400(_e):
        return pagina_de_erro(400)

    @app.errorhandler(403)
    def erro_403(_e):
        return pagina_de_erro(403)

    @app.errorhandler(404)
    def erro_404(_e):
        return pagina_de_erro(404)

    @app.errorhandler(413)
    def erro_413(_e):
        return pagina_de_erro(413)

    @app.errorhandler(500)
    def erro_500(_e):
        db.session.rollback()
        return pagina_de_erro(500)
