"""Configuração comum dos testes: aplicação com banco SQLite em memória e dados iniciais."""
import pytest

from app import create_app
from app.config import ConfigTeste
from app.extensions import db
from app.models import Produto, Usuario
from app.seed import popular

ADMIN = ("admin@lacakes.test", "Admin@2026")
CLIENTE = ("cliente@lacakes.test", "Cliente@2026")
CEP_JAU = "17201-000"
ENDERECO = {"modalidade": "ENTREGA", "cep": CEP_JAU, "logradouro": "Rua das Palmeiras", "numero": "85",
            "complemento": "Apto 52", "bairro": "Centro"}
CARTAO_OK = {"nome_cartao": "ANA SOUZA", "numero_cartao": "4111 1111 1111 1111", "validade": "12/35", "cvv": "123"}
CARTAO_RECUSADO = {**CARTAO_OK, "numero_cartao": "4111 1111 1111 0000"}


@pytest.fixture
def app():
    aplicacao = create_app(ConfigTeste)
    with aplicacao.app_context():
        popular(recriar=True)
        yield aplicacao
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def entrar(client, credenciais=CLIENTE):
    return client.post("/login", data={"email": credenciais[0], "senha": credenciais[1]})


def produto(nome):
    return db.session.scalar(db.select(Produto).where(Produto.nome == nome))


def usuario(email):
    return db.session.scalar(db.select(Usuario).where(Usuario.email == email))


def adicionar(client, nome, quantidade=1):
    return client.post(f"/carrinho/adicionar/{produto(nome).id}", data={"quantidade": quantidade})


@pytest.fixture
def cliente_logado(client):
    entrar(client)
    return client


@pytest.fixture
def admin_logado(client):
    entrar(client, ADMIN)
    return client


def criar_pedido(client, itens=(("Red Velvet Clássico", 3),), endereco=None):
    """Monta o carrinho e confirma o checkout. Retorna o id do pedido criado."""
    for nome, qtd in itens:
        adicionar(client, nome, qtd)
    resposta = client.post("/checkout", data=endereco or ENDERECO)
    assert resposta.status_code == 302, resposta.get_data(as_text=True)
    return int(resposta.headers["Location"].split("/")[2])
