"""Testes unitários dos models (regras que ficam nas entidades)."""
import pytest
from sqlalchemy.exc import IntegrityError

from app.excecoes import EstoqueInsuficiente, TransicaoInvalida
from app.extensions import db
from app.models import Categoria, ItemPedido, Modalidade, Pedido, Produto, StatusPedido, Usuario
from tests.conftest import produto, usuario


def novo_pedido(modalidade=Modalidade.ENTREGA, status=StatusPedido.PAGO):
    cliente, red_velvet = usuario("cliente@lacakes.test"), produto("Red Velvet Clássico")
    p = Pedido(usuario=cliente, modalidade=modalidade)
    db.session.add(p)
    p.itens.append(ItemPedido(produto=red_velvet, quantidade=2, preco_unitario_centavos=990))
    p.calcular_totais(800)
    p.registrar_status(status)
    return p


class TestUsuario:
    def test_senha_guardada_como_hash(self, app):
        u = usuario("cliente@lacakes.test")
        assert u.senha_hash != "Cliente@2026"
        assert u.verificar_senha("Cliente@2026")
        assert not u.verificar_senha("errada123")

    def test_perfil_e_iniciais(self, app):
        assert usuario("admin@lacakes.test").eh_admin
        cliente = usuario("cliente@lacakes.test")
        assert not cliente.eh_admin
        assert cliente.iniciais == "AS"
        assert cliente.primeiro_nome == "Ana"

    def test_email_unico_no_banco(self, app):
        u = Usuario(nome="Outra", email="cliente@lacakes.test", telefone="14999990000")
        u.definir_senha("abc12345")
        db.session.add(u)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


class TestProduto:
    def test_disponivel_e_esgotado(self, app):
        assert produto("Red Velvet Clássico").disponivel
        assert not produto("Morango com Chantilly").disponivel  # estoque 0
        assert not produto("Panetone Trufado").disponivel       # inativo

    def test_ultimas_unidades(self, app):
        assert produto("Limão Siciliano").ultimas_unidades       # estoque 4
        assert not produto("Red Velvet Clássico").ultimas_unidades

    def test_baixar_e_repor_estoque(self, app):
        p = produto("Limão Siciliano")
        p.baixar_estoque(3)
        assert p.estoque == 1
        with pytest.raises(EstoqueInsuficiente):
            p.baixar_estoque(2)
        p.repor_estoque(3)
        assert p.estoque == 4

    def test_imagem_padrao(self, app):
        p = Produto(nome="Teste", preco_centavos=500)
        assert p.caminho_imagem == "img/cupcakes/padrao.svg"

    def test_restricao_de_preco_no_banco(self, app):
        cat = db.session.scalar(db.select(Categoria))
        db.session.add(Produto(nome="Caro demais", categoria=cat, preco_centavos=99999, estoque=1))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


class TestPedido:
    def test_totais(self, app):
        p = novo_pedido()
        assert p.subtotal_centavos == 1980
        assert p.taxa_entrega_centavos == 800
        assert p.total_centavos == 2780
        assert p.quantidade_itens == 2

    def test_fluxo_de_status_entrega(self, app):
        p = novo_pedido(Modalidade.ENTREGA)
        assert p.avancar_status() == StatusPedido.EM_PREPARO
        assert p.avancar_status() == StatusPedido.SAIU_PARA_ENTREGA
        assert p.avancar_status() == StatusPedido.ENTREGUE
        with pytest.raises(TransicaoInvalida, match="finalizado"):
            p.avancar_status()

    def test_fluxo_de_status_retirada(self, app):
        p = novo_pedido(Modalidade.RETIRADA, StatusPedido.EM_PREPARO)
        assert p.proximo_status() == StatusPedido.PRONTO_PARA_RETIRADA
        assert p.etapas[3] == StatusPedido.PRONTO_PARA_RETIRADA

    def test_nao_avanca_sem_pagamento(self, app):
        p = novo_pedido(status=StatusPedido.AGUARDANDO_PAGAMENTO)
        with pytest.raises(TransicaoInvalida, match="ainda não foi pago"):
            p.avancar_status()

    def test_pode_cancelar_so_antes_do_preparo(self, app):
        assert novo_pedido(status=StatusPedido.AGUARDANDO_PAGAMENTO).pode_cancelar
        assert novo_pedido(status=StatusPedido.PAGO).pode_cancelar
        assert not novo_pedido(status=StatusPedido.EM_PREPARO).pode_cancelar
        assert not novo_pedido(status=StatusPedido.ENTREGUE).pode_cancelar

    def test_historico_registra_momento(self, app):
        p = novo_pedido()
        db.session.flush()  # aplica o valor padrão de criado_em
        assert p.momento_do_status(StatusPedido.PAGO) is not None
        assert p.momento_do_status(StatusPedido.ENTREGUE) is None

    def test_rotulos(self):
        assert StatusPedido.SAIU_PARA_ENTREGA.rotulo == "Saiu para entrega"
        assert Modalidade.RETIRADA.rotulo == "Retirada na loja"
