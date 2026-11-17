"""Aplicação web da LaCakes Cupcakes Gourmet (Flask, padrão MVC).

- Model: app/models (entidades) e app/services (regras de negócio)
- View: app/templates (Jinja2) e app/static (CSS, JS, imagens)
- Controller: app/controllers (rotas organizadas em blueprints)
"""
import click
from flask import Flask

from app.config import Config
from app.extensions import csrf, db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app import models  # noqa: F401  (registra as tabelas)
    from app.controllers import admin, auth, carrinho, erros, pedidos, vitrine
    from app.utils import registrar_filtros

    app.register_blueprint(vitrine.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(carrinho.bp)
    app.register_blueprint(pedidos.bp)
    app.register_blueprint(admin.bp)
    erros.registrar(app)
    registrar_filtros(app)

    from app.services import loja as servico_loja
    app.jinja_env.filters["previsao"] = servico_loja.texto_previsao

    @app.context_processor
    def dados_globais():
        from app.services.carrinho import Carrinho
        from flask import session
        dados = servico_loja.dados_da_loja()
        return {
            "qtd_carrinho": Carrinho(session).total_itens(),
            "loja": {"nome": app.config["LOJA_NOME"], "endereco": dados.endereco, "horario": dados.horario_texto},
            "situacao_loja": servico_loja.situacao(dados, servico_loja.relogio()),
        }

    @app.cli.command("seed")
    @click.option("--recriar", is_flag=True, help="Apaga todas as tabelas e cria de novo.")
    def comando_seed(recriar):
        """Cria as tabelas e os dados iniciais (cardápio e contas de teste)."""
        from app.seed import popular
        print(popular(recriar=recriar))

    if not app.config.get("TESTING"):
        app.instance_path and __import__("os").makedirs(app.instance_path, exist_ok=True)
        app.config["PASTA_UPLOADS"].mkdir(parents=True, exist_ok=True)

    return app
