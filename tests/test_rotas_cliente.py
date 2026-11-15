"""Testes de integração das rotas do cliente: vitrine, conta, carrinho, checkout, pagamento e acompanhamento."""
from app.extensions import db
from app.models import MetodoPagamento, Pedido, StatusPagamento, StatusPedido
from tests.conftest import (CARTAO_OK, CARTAO_RECUSADO, ENDERECO, adicionar, criar_pedido, entrar, produto,
                            usuario)


def texto(resposta):
    return resposta.get_data(as_text=True)


# ------------------------------------------------------------------ vitrine
class TestVitrine:
    def test_mostra_produtos_ativos_e_esconde_inativos(self, client):
        html = texto(client.get("/"))
        assert "Red Velvet Clássico" in html
        assert "R$ 9,90" in html
        assert "Panetone Trufado" not in html

    def test_selos_esgotado_e_ultimas_unidades(self, client):
        html = texto(client.get("/"))
        assert "Esgotado" in html
        assert "Últimas unidades" in html

    def test_filtro_por_categoria(self, client):
        cat = produto("Chocolate 70% Zero Açúcar").categoria_id
        html = texto(client.get(f"/?categoria={cat}"))
        assert "Chocolate 70% Zero Açúcar" in html
        assert "Red Velvet Clássico" not in html

    def test_categoria_sem_produtos(self, client):
        cat = produto("Panetone Trufado").categoria_id  # só tem o panetone, que está inativo
        assert "Nenhum cupcake nesta categoria hoje" in texto(client.get(f"/?categoria={cat}"))

    def test_vitrine_vazia(self, client, app):
        for p in db.session.scalars(db.select(type(produto("Red Velvet Clássico")))):
            p.ativo = False
        db.session.commit()
        assert "Nenhum cupcake disponível hoje" in texto(client.get("/"))

    def test_detalhe_mostra_alergenicos(self, client):
        html = texto(client.get(f"/produto/{produto('Ninho com Nutella').id}"))
        assert "Contém:" in html and "avelã" in html

    def test_produto_inexistente_ou_inativo_404(self, client):
        assert client.get("/produto/9999").status_code == 404
        resposta = client.get(f"/produto/{produto('Panetone Trufado').id}")
        assert resposta.status_code == 404
        assert "Página não encontrada" in texto(resposta)


# ------------------------------------------------------------------ conta
class TestConta:
    DADOS = {"nome": "Bruno Lima", "email": "bruno@exemplo.test", "telefone": "(14) 98888-7777",
             "senha": "senha1234", "confirmacao": "senha1234"}

    def test_cadastro_com_sucesso_ja_entra_logado(self, client):
        resposta = client.post("/cadastro", data=self.DADOS, follow_redirects=True)
        assert "Conta criada com sucesso" in texto(resposta)
        assert usuario("bruno@exemplo.test") is not None

    def test_cadastro_email_duplicado_mantem_campos(self, client):
        resposta = client.post("/cadastro", data={**self.DADOS, "email": "cliente@lacakes.test"})
        assert resposta.status_code == 422
        html = texto(resposta)
        assert "Este e-mail já possui conta" in html
        assert 'value="Bruno Lima"' in html

    def test_cadastro_senha_fraca_e_senhas_diferentes(self, client):
        resposta = client.post("/cadastro", data={**self.DADOS, "senha": "abc", "confirmacao": "xyz"})
        html = texto(resposta)
        assert "pelo menos 8 caracteres" in html
        assert "As senhas não conferem" in html

    def test_login_valido_e_invalido(self, client):
        ruim = client.post("/login", data={"email": "cliente@lacakes.test", "senha": "errada123"})
        assert ruim.status_code == 401
        assert "E-mail ou senha inválidos" in texto(ruim)
        bom = entrar(client)
        assert bom.status_code == 302

    def test_login_volta_para_pagina_de_origem(self, client):
        resposta = client.post("/login?next=/meus-pedidos",
                               data={"email": "cliente@lacakes.test", "senha": "Cliente@2026"})
        assert resposta.headers["Location"] == "/meus-pedidos"

    def test_login_nao_redireciona_para_outro_site(self, client):
        resposta = client.post("/login?next=https://site-malicioso.com",
                               data={"email": "cliente@lacakes.test", "senha": "Cliente@2026"})
        assert resposta.headers["Location"] == "/"

    def test_carrinho_mantido_apos_login(self, client):
        adicionar(client, "Red Velvet Clássico", 2)
        entrar(client)
        assert "Red Velvet Clássico" in texto(client.get("/carrinho/"))

    def test_logout_encerra_sessao(self, cliente_logado):
        resposta = cliente_logado.post("/logout", follow_redirects=True)
        assert "Você saiu da sua conta" in texto(resposta)
        assert cliente_logado.get("/meus-pedidos").status_code == 302


# ------------------------------------------------------------------ carrinho
class TestCarrinho:
    def test_adicionar_e_somar(self, client):
        adicionar(client, "Red Velvet Clássico", 2)
        adicionar(client, "Red Velvet Clássico", 1)
        html = texto(client.get("/carrinho/"))
        assert "R$ 29,70" in html  # 3 x 9,90

    def test_nao_passa_do_estoque(self, client):
        resposta = adicionar(client, "Limão Siciliano", 5)  # só tem 4
        assert resposta.status_code == 302
        html = texto(client.get(resposta.headers["Location"]))
        assert "Só temos 4 unidades deste sabor hoje" in html

    def test_nao_adiciona_esgotado(self, client):
        adicionar(client, "Morango com Chantilly", 1)
        assert "Este cupcake esgotou hoje" in texto(client.get("/"))

    def test_limite_de_24_por_sabor(self, client, app):
        produto("Ninho com Nutella").estoque = 100
        db.session.commit()
        adicionar(client, "Ninho com Nutella", 25)
        assert "O limite é de 24 unidades por sabor" in texto(client.get("/"))

    def test_atualizar_e_remover(self, client):
        adicionar(client, "Red Velvet Clássico", 2)
        pid = produto("Red Velvet Clássico").id
        client.post(f"/carrinho/atualizar/{pid}", data={"quantidade": 5})
        assert "R$ 49,50" in texto(client.get("/carrinho/"))
        client.post(f"/carrinho/remover/{pid}")
        assert "Seu carrinho está vazio" in texto(client.get("/carrinho/"))

    def test_atualizar_para_zero_remove(self, client):
        adicionar(client, "Red Velvet Clássico", 2)
        client.post(f"/carrinho/atualizar/{produto('Red Velvet Clássico').id}", data={"quantidade": 0})
        assert "Seu carrinho está vazio" in texto(client.get("/carrinho/"))

    def test_aviso_de_pedido_minimo_no_carrinho(self, client):
        adicionar(client, "Red Velvet Clássico", 1)
        assert "O pedido mínimo é de R$ 25,00" in texto(client.get("/carrinho/"))


# ------------------------------------------------------------------ checkout
class TestCheckout:
    def test_exige_login(self, client):
        adicionar(client, "Red Velvet Clássico", 3)
        resposta = client.get("/checkout")
        assert resposta.status_code == 302
        assert "/login?next=%2Fcheckout" in resposta.headers["Location"]

    def test_carrinho_vazio_volta_para_carrinho(self, cliente_logado):
        resposta = cliente_logado.get("/checkout")
        assert resposta.headers["Location"].endswith("/carrinho/")

    def test_cep_fora_de_jau(self, cliente_logado):
        adicionar(cliente_logado, "Red Velvet Clássico", 3)
        resposta = cliente_logado.post("/checkout", data={**ENDERECO, "cep": "13010-000"})
        assert resposta.status_code == 422
        assert "Ainda não entregamos neste CEP" in texto(resposta)

    def test_endereco_incompleto(self, cliente_logado):
        adicionar(cliente_logado, "Red Velvet Clássico", 3)
        resposta = cliente_logado.post("/checkout", data={**ENDERECO, "logradouro": "", "numero": "", "bairro": ""})
        html = texto(resposta)
        assert "Informe a rua" in html and "Informe o número" in html and "Informe o bairro" in html

    def test_pedido_minimo(self, cliente_logado):
        adicionar(cliente_logado, "Red Velvet Clássico", 2)  # R$ 19,80
        resposta = cliente_logado.post("/checkout", data=ENDERECO)
        assert resposta.status_code == 422
        assert "O pedido mínimo é de R$ 25,00" in texto(resposta)

    def test_cria_pedido_com_taxa_e_precos_congelados(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.status == StatusPedido.AGUARDANDO_PAGAMENTO
        assert pedido.subtotal_centavos == 2970 and pedido.taxa_entrega_centavos == 800
        assert pedido.cep == "17201000"
        assert cliente_logado.get("/carrinho/").get_data(as_text=True).count("Seu carrinho está vazio") == 1
        produto("Red Velvet Clássico").preco_centavos = 2000  # RN15: mudança de preço não afeta o pedido
        db.session.commit()
        assert db.session.get(Pedido, pedido_id).itens[0].preco_unitario_centavos == 990

    def test_retirada_sem_endereco_e_sem_taxa(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado, endereco={"modalidade": "RETIRADA"})
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.taxa_entrega_centavos == 0 and pedido.cep is None

    def test_entrega_gratis_acima_de_120(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado, itens=(("Ninho com Nutella", 10),))  # R$ 129,00
        assert db.session.get(Pedido, pedido_id).taxa_entrega_centavos == 0


# ------------------------------------------------------------------ pagamento
class TestPagamento:
    def test_credito_aprovado_baixa_estoque(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "CREDITO", **CARTAO_OK})
        assert resposta.headers["Location"] == f"/pedidos/{pedido_id}/confirmado"
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.status == StatusPedido.PAGO
        assert pedido.pagamento_aprovado.cartao_final == "1111"
        assert produto("Red Velvet Clássico").estoque == 15
        assert "Pedido #%d confirmado" % pedido_id in texto(cliente_logado.get(resposta.headers["Location"]))

    def test_debito_registra_modalidade(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "DEBITO", **CARTAO_OK})
        pagamento = db.session.get(Pedido, pedido_id).pagamento_aprovado
        assert pagamento.metodo == MetodoPagamento.DEBITO
        assert "Cartão de débito •••• 1111" in texto(cliente_logado.get(f"/pedidos/{pedido_id}/confirmado"))

    def test_pix(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        html = texto(cliente_logado.get(f"/pedidos/{pedido_id}/pagamento?metodo=PIX"))
        assert "BR.GOV.BCB.PIX" in html and "Já paguei" in html
        cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "PIX"})
        assert db.session.get(Pedido, pedido_id).pagamento_aprovado.metodo == MetodoPagamento.PIX

    def test_cartao_recusado_mantem_aguardando(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "CREDITO", **CARTAO_RECUSADO})
        html = texto(resposta)
        assert "Pagamento recusado" in html and "Nenhum valor foi cobrado" in html
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.status == StatusPedido.AGUARDANDO_PAGAMENTO
        assert pedido.pagamentos[0].status == StatusPagamento.RECUSADO
        assert produto("Red Velvet Clássico").estoque == 18

    def test_dados_do_cartao_invalidos(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/pagar",
                                       data={"metodo": "CREDITO", "nome_cartao": "", "numero_cartao": "123",
                                             "validade": "99/99", "cvv": "1"})
        assert resposta.status_code == 422
        assert "16 dígitos" in texto(resposta)

    def test_metodo_invalido(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "BOLETO"})
        assert resposta.status_code == 422

    def test_estoque_acabou_antes_de_pagar(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        produto("Red Velvet Clássico").estoque = 1
        db.session.commit()
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "CREDITO", **CARTAO_OK})
        assert resposta.status_code == 409
        assert "Estoque insuficiente para: Red Velvet Clássico" in texto(resposta)
        assert db.session.get(Pedido, pedido_id).pagamentos == []

    def test_nao_paga_duas_vezes(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "PIX"})
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "PIX"}, follow_redirects=True)
        assert "não está aguardando pagamento" in texto(resposta)
        assert cliente_logado.get(f"/pedidos/{pedido_id}/pagamento").status_code == 302


# ------------------------------------------------------------------ acompanhamento
class TestAcompanhamento:
    def test_lista_vazia(self, cliente_logado):
        assert "Você ainda não fez pedidos" in texto(cliente_logado.get("/meus-pedidos"))

    def test_lista_e_detalhe_com_linha_do_tempo(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "PIX"})
        assert f"Pedido #{pedido_id}" in texto(cliente_logado.get("/meus-pedidos"))
        html = texto(cliente_logado.get(f"/pedidos/{pedido_id}"))
        assert '<li class="passo atual" aria-current="step">\n          <b>Pago</b>' in html
        assert "Em preparo" in html and "Saiu para entrega" in html and 'aria-current="step"' in html

    def test_cliente_nao_ve_pedido_de_outro(self, client):
        entrar(client)
        pedido_id = criar_pedido(client)
        client.post("/logout")
        client.post("/cadastro", data={"nome": "Outra Pessoa", "email": "outra@exemplo.test",
                                       "telefone": "14988887777", "senha": "senha1234", "confirmacao": "senha1234"})
        resposta = client.get(f"/pedidos/{pedido_id}")
        assert resposta.status_code == 403
        assert "Acesso negado" in texto(resposta)

    def test_cancelar_pedido_pago_estorna_e_repoe_estoque(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "CREDITO", **CARTAO_OK})
        assert produto("Red Velvet Clássico").estoque == 15
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/cancelar", follow_redirects=True)
        assert "O pagamento foi estornado" in texto(resposta)
        pedido = db.session.get(Pedido, pedido_id)
        assert pedido.status == StatusPedido.CANCELADO
        assert pedido.pagamento_aprovado.status == StatusPagamento.ESTORNADO
        assert produto("Red Velvet Clássico").estoque == 18

    def test_nao_cancela_em_preparo(self, cliente_logado):
        pedido_id = criar_pedido(cliente_logado)
        cliente_logado.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "PIX"})
        pedido = db.session.get(Pedido, pedido_id)
        pedido.avancar_status()
        db.session.commit()
        resposta = cliente_logado.post(f"/pedidos/{pedido_id}/cancelar", follow_redirects=True)
        assert "não pode mais ser cancelado" in texto(resposta)
        assert "Cancelar pedido" not in texto(cliente_logado.get(f"/pedidos/{pedido_id}"))
