"""Testes das melhorias pedidas nos testes com usuários: tela inicial, busca de CEP, estatísticas de vendas,
horário de funcionamento (loja fechada) e dados da loja (US24 a US28)."""
from datetime import date, datetime, time

import pytest
from sqlalchemy import inspect, text

from app.excecoes import ErroValidacao
from app.extensions import db
from app.models import Loja, Pedido, StatusPedido
from app.models.loja import descrever_dias, formatar_hora
from app.seed import popular
from app.services import cep, estatisticas
from app.services import loja as servico_loja
from app.services import produtos as servico_produtos
from tests.conftest import ADMIN, CARTAO_OK, MOMENTO_PADRAO, adicionar, criar_pedido, entrar, fixar_relogio

SEGUNDA_10H = datetime(2026, 11, 16, 10, 0)
SEGUNDA_8H = datetime(2026, 11, 16, 8, 0)
SEGUNDA_20H = datetime(2026, 11, 16, 20, 0)
SEXTA_20H = datetime(2026, 11, 20, 20, 0)
SABADO_20H = datetime(2026, 11, 21, 20, 0)
DOMINGO_12H = datetime(2026, 11, 22, 12, 0)


def texto(resposta):
    return resposta.get_data(as_text=True)


def loja_padrao():
    return Loja(**servico_loja.PADRAO)


def pagar(client, pedido_id):
    return client.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "CREDITO", **CARTAO_OK})


# ------------------------------------------------------------------ dados e horário da loja (unidade)
class TestHorarioDaLoja:
    def test_textos_de_dias_e_horas(self):
        assert descrever_dias([0, 1, 2, 3, 4, 5]) == "Segunda a sábado"
        assert descrever_dias([5, 6]) == "Sábado e domingo"
        assert descrever_dias([0, 2, 4]) == "Segunda, quarta e sexta"
        assert descrever_dias(list(range(7))) == "Todos os dias"
        assert formatar_hora(time(9)) == "9h" and formatar_hora(time(18, 30)) == "18h30"
        assert loja_padrao().horario_texto == "Segunda a sábado, das 9h às 19h"

    @pytest.mark.parametrize("momento,aberta", [
        (SEGUNDA_10H, True), (SEGUNDA_8H, False), (datetime(2026, 11, 16, 19, 0), False),
        (datetime(2026, 11, 16, 18, 59), True), (SABADO_20H, False), (DOMINGO_12H, False),
    ])
    def test_loja_aberta_ou_fechada(self, momento, aberta):
        assert servico_loja.esta_aberta(loja_padrao(), momento) is aberta

    @pytest.mark.parametrize("momento,dia_esperado", [
        (SEGUNDA_10H, date(2026, 11, 16)),   # aberta: mesmo dia
        (SEGUNDA_8H, date(2026, 11, 16)),    # antes de abrir: hoje, quando abrir
        (SEGUNDA_20H, date(2026, 11, 17)),   # segunda a sexta depois das 19h: amanhã
        (SEXTA_20H, date(2026, 11, 21)),     # sexta à noite: sábado
        (SABADO_20H, date(2026, 11, 23)),    # sábado depois das 19h: segunda
        (DOMINGO_12H, date(2026, 11, 23)),   # domingo: segunda
    ])
    def test_dia_de_preparo(self, momento, dia_esperado):
        assert servico_loja.dia_de_preparo(loja_padrao(), momento) == dia_esperado

    def test_textos_da_previsao(self):
        loja = loja_padrao()
        assert (servico_loja.texto_previsao(date(2026, 11, 17), loja, SEGUNDA_20H)
                == "Preparado e entregue amanhã (ter., 17/11)")
        assert (servico_loja.texto_previsao(date(2026, 11, 23), loja, SABADO_20H)
                == "Preparado e entregue segunda-feira (23/11)")
        assert (servico_loja.texto_previsao(date(2026, 11, 16), loja, SEGUNDA_8H)
                == "Preparado e entregue hoje, a partir das 9h")
        assert servico_loja.texto_previsao(date(2026, 11, 16), loja, datetime(2026, 11, 18, 9)) == "Previsto para 16/11"

    def test_situacao_para_as_telas(self):
        aberta = servico_loja.situacao(loja_padrao(), SEGUNDA_10H)
        assert aberta["aberta"] and aberta["resumo"] == "Aberto agora · fecha às 19h"
        fechada = servico_loja.situacao(loja_padrao(), SABADO_20H)
        assert fechada["resumo"] == "Fechado agora · abre segunda-feira às 9h"
        assert "serão preparados e entregues segunda-feira (23/11)" in fechada["aviso"]

    def test_horario_configuravel(self):
        loja = Loja(endereco="Rua Teste, 1 – Jaú/SP", dias_funcionamento="0123456", abre_as=time(8), fecha_as=time(22))
        assert servico_loja.esta_aberta(loja, datetime(2026, 11, 22, 21, 0))   # domingo às 21h
        assert servico_loja.dia_de_preparo(loja, datetime(2026, 11, 22, 23, 0)) == date(2026, 11, 23)

    @pytest.mark.parametrize("texto_hora,esperado", [("09:00", time(9)), ("9:30", time(9, 30)), ("24:00", None),
                                                     ("", None), ("abc", None)])
    def test_ler_hora(self, texto_hora, esperado):
        assert servico_loja.ler_hora(texto_hora) == esperado


class TestCadastroDaLoja:
    def test_salva_dados_validos(self, app):
        servico_loja.salvar_dados({"endereco": "Av. Brasil, 500 – Jaú/SP", "abre_as": "10:00", "fecha_as": "18:00"},
                                  ["0", "1", "2", "3", "4"])
        loja = servico_loja.dados_da_loja()
        assert loja.horario_texto == "Segunda a sexta, das 10h às 18h"
        assert db.session.scalar(db.select(db.func.count(Loja.id))) == 1

    def test_valida_campos(self, app):
        with pytest.raises(ErroValidacao) as erro:
            servico_loja.salvar_dados({"endereco": "Rua", "abre_as": "19:00", "fecha_as": "09:00"}, [])
        assert set(erro.value.erros) == {"endereco", "dias", "fecha_as"}

    def test_seed_atualiza_banco_de_versao_anterior(self, app):
        """Banco criado antes desta versão: sem a coluna previsao_preparo e sem a tabela loja preenchida."""
        db.session.execute(text("ALTER TABLE pedido DROP COLUMN previsao_preparo"))
        db.session.execute(text("DELETE FROM loja"))
        db.session.commit()
        popular()
        colunas = {c["name"] for c in inspect(db.engine).get_columns("pedido")}
        assert "previsao_preparo" in colunas
        assert db.session.scalar(db.select(db.func.count(Loja.id))) == 1


# ------------------------------------------------------------------ busca de CEP (unidade)
class TestBuscaDeCep:
    def test_preenche_rua_e_bairro(self, monkeypatch):
        monkeypatch.setattr(cep, "consultar_viacep", lambda c: {"logradouro": "Rua Lourenço Prado", "bairro": "Centro",
                                                                 "localidade": "Jaú", "uf": "SP"})
        resultado = cep.buscar_endereco("17201-000")
        assert resultado["ok"] and resultado["logradouro"] == "Rua Lourenço Prado" and resultado["bairro"] == "Centro"

    def test_cep_fora_de_jau_nem_consulta(self, monkeypatch):
        def nao_deveria_chamar(_c):
            raise AssertionError("não deveria consultar CEP fora da área")
        monkeypatch.setattr(cep, "consultar_viacep", nao_deveria_chamar)
        resultado = cep.buscar_endereco("13010-000")
        assert not resultado["ok"] and resultado["fora_da_area"]
        assert "Ainda não entregamos neste CEP" in resultado["mensagem"]

    def test_cep_inexistente(self, monkeypatch):
        monkeypatch.setattr(cep, "consultar_viacep", lambda c: None)
        assert "CEP não encontrado" in cep.buscar_endereco("17229-999")["mensagem"]

    def test_servico_fora_do_ar(self, monkeypatch):
        def sem_internet(_c):
            raise OSError("sem conexão")
        monkeypatch.setattr(cep, "consultar_viacep", sem_internet)
        assert "Preencha a rua e o bairro" in cep.buscar_endereco("17201-000")["mensagem"]

    def test_cep_incompleto(self):
        assert cep.buscar_endereco("1720")["mensagem"] == "Informe um CEP com 8 dígitos."

    def test_rota_exige_login_e_devolve_json(self, client, monkeypatch):
        monkeypatch.setattr(cep, "consultar_viacep", lambda c: {"logradouro": "Rua A", "bairro": "Centro",
                                                                 "localidade": "Jaú", "uf": "SP"})
        assert client.get("/cep/17201000").status_code == 302
        entrar(client)
        dados = client.get("/cep/17201000").get_json()
        assert dados["ok"] and dados["logradouro"] == "Rua A"

    def test_checkout_tem_ligacao_com_a_busca(self, cliente_logado):
        adicionar(cliente_logado, "Red Velvet Clássico", 3)
        html = texto(cliente_logado.get("/checkout"))
        assert 'data-url-cep="/cep/00000000"' in html
        assert "a rua e o bairro são preenchidos" in html


# ------------------------------------------------------------------ tela inicial
class TestTelaInicial:
    def test_tela_inicial_antes_da_vitrine(self, client):
        html = texto(client.get("/"))
        assert "Feitos hoje, fresquinhos" in html
        assert "Ver cupcakes" in html and 'href="/vitrine"' in html
        assert "Destaques de hoje" in html and "Como funciona" in html
        assert "Rua das Flores, 120 – Jaú/SP" in html and "Segunda a sábado, das 9h às 19h" in html
        assert "Aberto agora · fecha às 19h" in html

    def test_destaques_mostram_os_mais_vendidos_disponiveis(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado, itens=(("Pistache com Frutas Vermelhas", 2),))
        pagar(cliente_logado, pedido_id)
        destaques = servico_produtos.destaques(3)
        assert destaques[0].nome == "Pistache com Frutas Vermelhas"
        assert all(p.disponivel for p in destaques)
        assert "Morango com Chantilly" not in [p.nome for p in destaques]  # esgotado


# ------------------------------------------------------------------ loja fechada (rotas)
class TestLojaFechada:
    def test_sem_aviso_com_a_loja_aberta(self, client):
        assert "A loja está fechada agora" not in texto(client.get("/vitrine"))

    def test_aviso_de_loja_fechada(self, client, monkeypatch):
        fixar_relogio(monkeypatch, SEGUNDA_20H)
        assert "Fechado agora · abre amanhã às 9h" in texto(client.get("/"))
        html = texto(client.get("/vitrine"))
        assert "A loja está fechada agora e abre amanhã às 9h" in html
        assert "serão preparados e entregues amanhã (ter., 17/11)" in html

    def test_pedido_de_segunda_a_noite_fica_para_amanha(self, cliente_logado, monkeypatch):
        fixar_relogio(monkeypatch, SEGUNDA_20H)
        pedido_id = criar_pedido(cliente_logado)
        resposta = pagar(cliente_logado, pedido_id)
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.status == StatusPedido.PAGO and pedido.previsao_preparo == date(2026, 11, 17)
        assert pedido.agendado
        html = texto(cliente_logado.get(resposta.headers["Location"]))
        assert "Preparado e entregue amanhã (ter., 17/11)" in html
        assert "Preparado e entregue amanhã" in texto(cliente_logado.get("/meus-pedidos"))

    def test_pedido_de_sabado_a_noite_fica_para_segunda(self, cliente_logado, monkeypatch):
        fixar_relogio(monkeypatch, SABADO_20H)
        pedido_id = criar_pedido(cliente_logado)
        pagar(cliente_logado, pedido_id)
        assert db.session.get(Pedido, pedido_id).previsao_preparo == date(2026, 11, 23)
        assert "Preparado e entregue segunda-feira (23/11)" in texto(cliente_logado.get(f"/pedidos/{pedido_id}"))

    def test_pedido_com_loja_aberta_sai_no_mesmo_dia(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        pagar(cliente_logado, pedido_id)
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.previsao_preparo is None and not pedido.agendado
        assert "Preparado e entregue" not in texto(cliente_logado.get(f"/pedidos/{pedido_id}"))

    def test_selo_some_quando_o_pedido_entra_em_preparo(self, client, monkeypatch):
        fixar_relogio(monkeypatch, SEGUNDA_20H)
        entrar(client)
        pedido_id = criar_pedido(client)
        pagar(client, pedido_id)
        client.post("/logout")
        entrar(client, ADMIN)
        assert "Preparado e entregue amanhã" in texto(client.get("/admin/pedidos"))
        client.post(f"/admin/pedidos/{pedido_id}/avancar")
        assert not db.session.get(Pedido, pedido_id).agendado


# ------------------------------------------------------------------ área administrativa
class TestDadosDaLojaAdmin:
    def test_tela_mostra_os_dados_atuais(self, admin_logado):
        html = texto(admin_logado.get("/admin/loja"))
        assert "Dados da loja" in html and 'value="Rua das Flores, 120 – Jaú/SP"' in html
        assert 'value="09:00"' in html and 'value="19:00"' in html

    def test_salvar_muda_o_site(self, admin_logado):
        resposta = admin_logado.post("/admin/loja", data={"endereco": "Rua Nova, 45 – Jaú/SP", "dias": ["0", "1", "2"],
                                                          "abre_as": "08:00", "fecha_as": "12:00"},
                                     follow_redirects=True)
        assert "Dados da loja salvos" in texto(resposta)
        html = texto(admin_logado.get("/"))
        assert "Rua Nova, 45 – Jaú/SP" in html and "Segunda a quarta, das 8h às 12h" in html
        assert "Aberto agora · fecha às 12h" in html   # relógio dos testes: segunda às 10h

    def test_dados_invalidos(self, admin_logado):
        resposta = admin_logado.post("/admin/loja", data={"endereco": "", "abre_as": "18:00", "fecha_as": "08:00"})
        assert resposta.status_code == 422
        html = texto(resposta)
        assert "Marque pelo menos um dia de funcionamento" in html
        assert "O fechamento precisa ser depois da abertura" in html

    def test_cliente_nao_acessa(self, cliente_logado):
        assert cliente_logado.get("/admin/loja").status_code == 403
        assert cliente_logado.get("/admin/vendas").status_code == 403


class TestEstatisticasDeVendas:
    def _vendas_do_dia(self, client):
        """Dois pedidos pagos, um cancelado e um aguardando pagamento, todos no dia do relógio fixo."""
        entrar(client)
        pago1 = criar_pedido(client, itens=(("Red Velvet Clássico", 3),))
        pagar(client, pago1)
        pago2 = criar_pedido(client, itens=(("Red Velvet Clássico", 1), ("Ninho com Nutella", 2)),
                             endereco={"modalidade": "RETIRADA"})
        client.post(f"/pedidos/{pago2}/pagar", data={"metodo": "PIX"})
        cancelado = criar_pedido(client, itens=(("Ninho com Nutella", 2),))
        pagar(client, cancelado)
        client.post(f"/pedidos/{cancelado}/cancelar")
        criar_pedido(client, itens=(("Ninho com Nutella", 2),))
        for pedido in db.session.scalars(db.select(Pedido)):
            pedido.criado_em = MOMENTO_PADRAO
        db.session.commit()
        client.post("/logout")
        return pago1, pago2

    def test_resumo_do_dia(self, client):
        self._vendas_do_dia(client)
        resumo = estatisticas.resumo_do_dia(MOMENTO_PADRAO.date())
        # pedido 1: 3 × 9,90 + 8,00 de entrega = 37,70 · pedido 2: 9,90 + 2 × 12,90 (retirada) = 35,70
        assert resumo["pedidos"] == 2 and resumo["cupcakes"] == 6
        assert resumo["total"] == 3770 + 3570 and resumo["ticket_medio"] == 3670
        assert resumo["cancelados"] == 1 and resumo["aguardando"] == 1
        assert resumo["por_sabor"][0] == {"nome": "Red Velvet Clássico", "quantidade": 4, "valor": 3960,
                                          "percentual": 100}
        assert {linha["nome"] for linha in resumo["por_pagamento"]} == {"Cartão de crédito", "Pix"}

    def test_ultimos_7_dias(self, client):
        self._vendas_do_dia(client)
        semana = estatisticas.ultimos_dias(date(2026, 11, 17))
        assert len(semana) == 7 and semana[0]["dia"] == date(2026, 11, 17)
        assert semana[1]["pedidos"] == 2 and semana[1]["total"] == 7340

    def test_tela_de_vendas(self, client):
        self._vendas_do_dia(client)
        entrar(client, ADMIN)
        html = texto(client.get("/admin/vendas"))
        assert "Estatísticas de vendas" in html and "R$ 73,40" in html and "Red Velvet Clássico" in html
        assert "Últimos 7 dias" in html
        assert "Hoje:</b> 2 pedidos pagos · 6 cupcakes · R$ 73,40" in texto(client.get("/admin/pedidos"))

    def test_dia_sem_vendas_e_data_invalida(self, admin_logado):
        assert "Sem vendas neste dia" in texto(admin_logado.get("/admin/vendas?data=2026-11-01"))
        assert admin_logado.get("/admin/vendas?data=abc").status_code == 200
        assert "16/11/2026" in texto(admin_logado.get("/admin/vendas?data=2030-01-01"))  # futuro vira hoje

