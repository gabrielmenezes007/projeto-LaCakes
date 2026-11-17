"""Testes da área administrativa e das páginas de erro."""
import io

import pytest

from app.extensions import db
from app.models import Pedido, StatusPedido
from tests.conftest import ADMIN, criar_pedido, entrar, produto


def texto(resposta):
    return resposta.get_data(as_text=True)


def form_produto(**mudancas):
    cat = produto("Red Velvet Clássico").categoria_id
    dados = {"nome": "Pistache Supremo", "categoria_id": str(cat), "descricao": "Teste", "ingredientes": "Pistache",
             "alergenicos": "Castanhas", "preco": "14,90", "estoque": "20", "ativo": "on"}
    dados.update(mudancas)
    return dados


class TestAcessoAdmin:
    def test_visitante_vai_para_login(self, client):
        resposta = client.get("/admin/produtos")
        assert resposta.status_code == 302 and "/login" in resposta.headers["Location"]

    def test_cliente_recebe_403(self, cliente_logado):
        resposta = cliente_logado.get("/admin/pedidos")
        assert resposta.status_code == 403
        assert "Acesso negado" in texto(resposta)

    def test_admin_acessa(self, admin_logado):
        assert admin_logado.get("/admin/").status_code == 302
        assert "Produtos e estoque do dia" in texto(admin_logado.get("/admin/produtos"))
        assert "Administração" in texto(admin_logado.get("/vitrine"))


class TestProdutosAdmin:
    def test_cadastrar_produto_aparece_na_vitrine(self, admin_logado):
        resposta = admin_logado.post("/admin/produtos/novo", data=form_produto())
        assert resposta.status_code == 302
        p = produto("Pistache Supremo")
        assert p.preco_centavos == 1490 and p.caminho_imagem == "img/cupcakes/padrao.svg"
        assert "Pistache Supremo" in texto(admin_logado.get("/vitrine"))

    def test_nome_duplicado_e_preco_fora_da_faixa(self, admin_logado):
        resposta = admin_logado.post("/admin/produtos/novo",
                                     data=form_produto(nome="red velvet clássico", preco="250,00", estoque="-1"))
        assert resposta.status_code == 422
        html = texto(resposta)
        assert "Já existe um cupcake com este nome" in html
        assert "O preço deve ficar entre R$ 1,00 e R$ 200,00" in html
        assert "O estoque deve ser um número de 0 a 500" in html

    def test_upload_de_foto(self, admin_logado, app, tmp_path):
        app.config["PASTA_UPLOADS"] = tmp_path
        dados = form_produto(imagem=(io.BytesIO(b"fake-png"), "foto.png"))
        admin_logado.post("/admin/produtos/novo", data=dados, content_type="multipart/form-data")
        caminho = produto("Pistache Supremo").imagem
        assert caminho.startswith("uploads/") and caminho.endswith(".png")
        assert (tmp_path / caminho.split("/")[1]).exists()

    def test_upload_com_extensao_invalida(self, admin_logado):
        dados = form_produto(imagem=(io.BytesIO(b"x"), "virus.exe"))
        resposta = admin_logado.post("/admin/produtos/novo", data=dados, content_type="multipart/form-data")
        assert resposta.status_code == 422 and "Envie uma imagem JPG, PNG ou WEBP" in texto(resposta)

    def test_editar_preco_e_desativar(self, admin_logado):
        pid = produto("Red Velvet Clássico").id
        assert 'value="9,90"' in texto(admin_logado.get(f"/admin/produtos/{pid}/editar"))
        admin_logado.post(f"/admin/produtos/{pid}/editar",
                          data=form_produto(nome="Red Velvet Clássico", preco="11,00", ativo=""))
        p = produto("Red Velvet Clássico")
        assert p.preco_centavos == 1100 and not p.ativo
        assert '<h2 class="nome">Red Velvet Clássico</h2>' not in texto(admin_logado.get("/vitrine"))

    def test_editar_produto_inexistente(self, admin_logado):
        assert admin_logado.get("/admin/produtos/999/editar").status_code == 404

    def test_atualizar_estoque_do_dia(self, admin_logado):
        morango = produto("Morango com Chantilly").id
        limao = produto("Limão Siciliano").id
        admin_logado.post("/admin/produtos/estoque", data={f"estoque_{morango}": "12", f"estoque_{limao}": "0"})
        assert produto("Morango com Chantilly").estoque == 12
        assert produto("Limão Siciliano").estoque == 0

    def test_estoque_invalido_nao_salva_nada(self, admin_logado):
        morango = produto("Morango com Chantilly").id
        limao = produto("Limão Siciliano").id
        resposta = admin_logado.post("/admin/produtos/estoque",
                                     data={f"estoque_{morango}": "12", f"estoque_{limao}": "900"})
        assert resposta.status_code == 422
        assert "Nada foi salvo" in texto(resposta)
        assert produto("Morango com Chantilly").estoque == 0


class TestPedidosAdmin:
    def _pedido_pago(self, client):
        entrar(client)
        pedido_id = criar_pedido(client)
        client.post(f"/pedidos/{pedido_id}/pagar", data={"metodo": "PIX"})
        client.post("/logout")
        entrar(client, ADMIN)
        return pedido_id

    def test_avancar_ate_entregue(self, client):
        pedido_id = self._pedido_pago(client)
        assert "Avançar → Em preparo" in texto(client.get("/admin/pedidos"))
        for esperado in ("Em preparo", "Saiu para entrega", "Entregue"):
            resposta = client.post(f"/admin/pedidos/{pedido_id}/avancar", follow_redirects=True)
            assert f"atualizado para {esperado}" in texto(resposta)
        assert db.session.get(Pedido, pedido_id).status == StatusPedido.ENTREGUE
        resposta = client.post(f"/admin/pedidos/{pedido_id}/avancar", follow_redirects=True)
        assert "já foi finalizado" in texto(resposta)

    def test_nao_avanca_pedido_sem_pagamento(self, client):
        entrar(client)
        pedido_id = criar_pedido(client)
        client.post("/logout")
        entrar(client, ADMIN)
        resposta = client.post(f"/admin/pedidos/{pedido_id}/avancar", follow_redirects=True)
        assert "Este pedido ainda não foi pago" in texto(resposta)

    def test_filtro_por_status(self, client):
        pedido_id = self._pedido_pago(client)
        assert f"#{pedido_id}" in texto(client.get("/admin/pedidos?status=PAGO"))
        assert f"#{pedido_id}" not in texto(client.get("/admin/pedidos?status=ENTREGUE"))
        assert client.get("/admin/pedidos?status=INVALIDO").status_code == 200

    def test_cliente_ve_mudanca_de_status(self, client):
        pedido_id = self._pedido_pago(client)
        client.post(f"/admin/pedidos/{pedido_id}/avancar")
        client.post("/logout")
        entrar(client)
        html = texto(client.get(f"/pedidos/{pedido_id}"))
        assert '<span class="status s-prep">Em preparo</span>' in html


class TestErros:
    def test_pagina_404(self, client):
        resposta = client.get("/nao-existe")
        assert resposta.status_code == 404
        assert "Voltar à vitrine" in texto(resposta)

    def test_pagina_500_amigavel(self, app):
        app.config["PROPAGATE_EXCEPTIONS"] = False

        @app.get("/forcar-erro")
        def forcar_erro():
            raise RuntimeError("erro de teste")

        resposta = app.test_client().get("/forcar-erro")
        assert resposta.status_code == 500
        assert "Algo deu errado" in texto(resposta)

    def test_csrf_ativo_fora_dos_testes(self, app):
        app.config["WTF_CSRF_ENABLED"] = True
        resposta = app.test_client().post("/login", data={"email": "x", "senha": "y"})
        assert resposta.status_code == 400
        assert "Página expirada" in texto(resposta)

    def test_arquivo_grande_413(self, admin_logado, app):
        app.config["MAX_CONTENT_LENGTH"] = 10
        resposta = admin_logado.post("/admin/produtos/novo", data=form_produto(imagem=(io.BytesIO(b"x" * 100), "a.png")),
                                     content_type="multipart/form-data")
        assert resposta.status_code == 413
        assert "Arquivo muito grande" in texto(resposta)


@pytest.mark.parametrize("url", ["/", "/vitrine", "/carrinho/", "/login", "/cadastro"])
def test_paginas_publicas_respondem(client, url):
    assert client.get(url).status_code == 200
