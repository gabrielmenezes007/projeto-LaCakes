"""Testes unitários das regras de negócio (frete, pagamento simulado, contas, utilitários)."""
from datetime import date

import pytest

from app.excecoes import ErroValidacao
from app.models import MetodoPagamento, Modalidade
from app.services import contas, frete, pagamento
from app.utils import centavos_para_texto, formatar_cep, formatar_moeda, reais_para_centavos, url_segura


class TestFrete:
    def test_taxa_de_entrega(self):
        assert frete.calcular_taxa(Modalidade.ENTREGA, 5000) == 800
        assert frete.calcular_taxa(Modalidade.ENTREGA, 11999) == 800

    def test_entrega_gratis_a_partir_de_120(self):
        assert frete.calcular_taxa(Modalidade.ENTREGA, 12000) == 0

    def test_retirada_sem_taxa(self):
        assert frete.calcular_taxa(Modalidade.RETIRADA, 3000) == 0

    @pytest.mark.parametrize("cep,esperado", [
        ("17200-001", True), ("17229-999", True), ("17201000", True),
        ("17200-000", False), ("17230-000", False), ("01001-000", False), ("1720", False), ("", False), (None, False),
    ])
    def test_area_de_entrega_jau(self, cep, esperado):
        assert frete.cep_atendido(cep) is esperado

    def test_pedido_minimo(self):
        assert not frete.atinge_pedido_minimo(2499)
        assert frete.atinge_pedido_minimo(2500)


class TestPagamentoSimulado:
    HOJE = date(2026, 11, 15)

    def test_cartao_valido(self):
        assert pagamento.validar_cartao("ANA SOUZA", "4111 1111 1111 1111", "12/30", "123", self.HOJE) == {}

    def test_cartao_com_erros(self):
        erros = pagamento.validar_cartao("", "1234", "13/30", "12", self.HOJE)
        assert set(erros) == {"nome_cartao", "numero_cartao", "validade", "cvv"}

    def test_cartao_vencido(self):
        erros = pagamento.validar_cartao("ANA SOUZA", "4111111111111111", "10/26", "123", self.HOJE)
        assert erros["validade"] == "Este cartão está vencido."

    def test_validade_no_mes_atual_e_aceita(self):
        assert pagamento.validar_cartao("ANA SOUZA", "4111111111111111", "11/2026", "123", self.HOJE) == {}

    @pytest.mark.parametrize("metodo", [MetodoPagamento.CREDITO, MetodoPagamento.DEBITO])
    def test_final_0000_e_recusado(self, metodo):
        assert not pagamento.cobrar(metodo, 1000, "4111111111110000").aprovado
        assert pagamento.cobrar(metodo, 1000, "4111111111111111").aprovado

    def test_pix_sempre_aprovado(self):
        assert pagamento.cobrar(MetodoPagamento.PIX, 1000).aprovado

    def test_metodo_de_texto(self):
        assert pagamento.metodo_de_texto("debito") == MetodoPagamento.DEBITO
        assert pagamento.metodo_de_texto("boleto") is None


class TestContas:
    @pytest.mark.parametrize("senha,ok", [("abc12345", True), ("Cliente@2026", True), ("abcdefgh", False),
                                          ("12345678", False), ("ab1", False), ("", False)])
    def test_senha_forte(self, senha, ok):
        assert contas.senha_forte(senha) is ok

    def test_cadastro_valida_todos_os_campos(self, app):
        with pytest.raises(ErroValidacao) as e:
            contas.cadastrar_cliente("A", "email-invalido", "123", "fraca", "outra")
        assert set(e.value.erros) == {"nome", "email", "telefone", "senha", "confirmacao"}

    def test_autenticar_ignora_maiusculas_no_email(self, app):
        assert contas.autenticar("CLIENTE@LaCakes.test", "Cliente@2026") is not None
        assert contas.autenticar("cliente@lacakes.test", "errada123") is None
        assert contas.autenticar("ninguem@lacakes.test", "Cliente@2026") is None


class TestUtilitarios:
    def test_formatar_moeda(self):
        assert formatar_moeda(990) == "R$ 9,90"
        assert formatar_moeda(123456) == "R$ 1.234,56"
        assert formatar_moeda(0) == "R$ 0,00"

    @pytest.mark.parametrize("texto,centavos", [("14,90", 1490), ("14.90", 1490), ("R$ 1.234,56", 123456),
                                                ("10", 1000), ("abc", None), ("", None), ("1,999", None)])
    def test_reais_para_centavos(self, texto, centavos):
        assert reais_para_centavos(texto) == centavos

    def test_outros_formatos(self):
        assert centavos_para_texto(1490) == "14,90"
        assert formatar_cep("17201000") == "17201-000"

    def test_url_segura(self):
        assert url_segura("/checkout")
        assert not url_segura("https://site-malicioso.com")
        assert not url_segura("//site-malicioso.com")
        assert not url_segura(None)
