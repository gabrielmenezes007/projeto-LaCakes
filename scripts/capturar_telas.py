"""Captura as telas reais do sistema (evidência de implementação) em docs/desenvolvimento/img/telas.

Sobe a aplicação num banco SQLite temporário (o banco do usuário não é alterado), percorre os fluxos
principais no Microsoft Edge (Playwright, tamanho de celular) e salva um PNG por tela.

Uso: python scripts/capturar_telas.py   (rodar com o Python do .venv, que tem Flask instalado)
"""
import os
import pathlib
import sys
import tempfile
import threading
from datetime import date, datetime, time

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TEMP = pathlib.Path(tempfile.mkdtemp(prefix="lacakes-telas-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(TEMP / 'telas.db').as_posix()}"
sys.path.insert(0, str(RAIZ))

from playwright.sync_api import sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from app import create_app  # noqa: E402
from app.seed import popular  # noqa: E402
from app.services import loja as servico_loja  # noqa: E402

DESTINO = RAIZ / "docs" / "desenvolvimento" / "img" / "telas"
PORTA = 5077
BASE = f"http://127.0.0.1:{PORTA}"
# Relógio das capturas: hoje às 10h (loja aberta) e hoje às 20h (loja fechada). Segunda a sábado.
HOJE = date.today()
ABERTA, FECHADA = datetime.combine(HOJE, time(10)), datetime.combine(HOJE, time(20))
CARTAO = {"nome": "ANA SOUZA", "ok": "4111111111111111", "recusado": "4111111111110000", "validade": "12/30", "cvv": "123"}


def fixar_relogio(momento):
    servico_loja.relogio = lambda: momento


def subir_servidor():
    app = create_app()
    app.config["PASTA_UPLOADS"] = TEMP / "uploads"
    with app.app_context():
        popular(recriar=True)
    servidor = make_server("127.0.0.1", PORTA, app)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    fixar_relogio(ABERTA)
    servidor = subir_servidor()
    with sync_playwright() as p:
        nav = p.chromium.launch(channel="msedge", headless=True)
        ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="pt-BR")
        pg = ctx.new_page()

        def foto(nome, pagina_inteira=True):
            pg.wait_for_timeout(150)
            # na foto da página inteira, a barra fixa do rodapé vai para o fim (no celular ela fica presa na tela)
            pg.add_style_tag(content=".rodape-nav{position:static!important} body{padding-bottom:0!important}")
            pg.screenshot(path=str(DESTINO / f"{nome}.png"), full_page=pagina_inteira)
            print("ok", nome)

        def entrar(email, senha, erro=False):
            pg.goto(f"{BASE}/login")
            pg.fill("#email", email)
            pg.fill("#senha", senha)
            pg.click("main button[type=submit]")
            if erro:
                foto("06-login-invalido")

        pg.goto(BASE)
        foto("23-tela-inicial")
        pg.goto(f"{BASE}/vitrine")
        foto("01-vitrine")
        pg.goto(f"{BASE}/vitrine?categoria=2")
        foto("02-vitrine-filtro-recheados")
        pg.goto(f"{BASE}/produto/3")
        foto("03-detalhe-produto")
        pg.fill("#quantidade", "9")
        pg.evaluate("document.querySelector('#quantidade').removeAttribute('max')")
        pg.click("main form.form-qtd button[type=submit]")
        foto("04-erro-estoque-insuficiente")
        pg.goto(f"{BASE}/cadastro")
        pg.fill("#nome", "Bruno Lima")
        pg.fill("#email", "cliente@lacakes.test")
        pg.fill("#telefone", "(14) 98888-7777")
        pg.fill("#senha", "abc")
        pg.fill("#confirmacao", "xyz")
        pg.click("main form button[type=submit]")
        foto("05-cadastro-com-erros")
        entrar("cliente@lacakes.test", "senha-errada1", erro=True)

        entrar("cliente@lacakes.test", "Cliente@2026")
        pg.goto(f"{BASE}/carrinho/")
        foto("07-carrinho-vazio")
        for pid, qtd in ((4, 2), (2, 1)):
            pg.goto(f"{BASE}/produto/{pid}")
            pg.fill("#quantidade", str(qtd))
            pg.click("main form.form-qtd button[type=submit]")
        pg.goto(f"{BASE}/carrinho/")
        foto("08-carrinho")
        pg.goto(f"{BASE}/checkout")
        pg.fill("#cep", "17201-000")
        pg.wait_for_selector("[data-cep-status].ok-texto", timeout=10000)
        foto("24-checkout-cep-preenchido")
        pg.fill("#cep", "13010-000")
        pg.fill("#logradouro", "Rua das Palmeiras")
        pg.fill("#numero", "85")
        pg.fill("#bairro", "Centro")
        pg.click("aside button[type=submit]")
        foto("09-checkout-cep-fora-da-area")
        pg.fill("#cep", "17201-000")
        pg.click("aside button[type=submit]")
        pg.wait_for_url("**/pagamento")
        foto("10-pagamento-credito")
        pg.goto(pg.url + "?metodo=PIX")
        foto("11-pagamento-pix")
        pg.goto(pg.url.split("?")[0] + "?metodo=DEBITO")
        pg.fill("#nome_cartao", CARTAO["nome"])
        pg.fill("#numero_cartao", CARTAO["recusado"])
        pg.fill("#validade", CARTAO["validade"])
        pg.fill("#cvv", CARTAO["cvv"])
        pg.click("main form button[type=submit].verde")
        foto("12-pagamento-recusado")
        pg.click("text=Tentar novamente")
        pg.goto(pg.url.split("?")[0] + "?metodo=DEBITO")
        pg.fill("#nome_cartao", CARTAO["nome"])
        pg.fill("#numero_cartao", CARTAO["ok"])
        pg.fill("#validade", CARTAO["validade"])
        pg.fill("#cvv", CARTAO["cvv"])
        pg.click("main form button[type=submit].verde")
        pg.wait_for_url("**/confirmado")
        foto("13-pedido-confirmado")
        pedido_url = pg.url.replace("/confirmado", "")
        pg.goto(f"{BASE}/meus-pedidos")
        foto("14-meus-pedidos")
        pg.goto(pedido_url)
        foto("15-acompanhamento")
        pg.goto(f"{BASE}/admin/produtos")
        foto("16-acesso-negado-403")
        pg.goto(f"{BASE}/produto/999")
        foto("17-pagina-nao-encontrada-404")

        ctx.clear_cookies()
        entrar("admin@lacakes.test", "Admin@2026")
        pg.goto(f"{BASE}/admin/pedidos")
        pg.click("text=Avançar → Em preparo")
        foto("18-admin-pedidos")
        pg.goto(f"{BASE}/admin/produtos")
        foto("19-admin-produtos-estoque")
        pg.goto(f"{BASE}/admin/produtos/novo")
        pg.fill("#nome", "Red Velvet Clássico")
        pg.fill("#preco", "250")
        pg.click("main form button[type=submit]")
        foto("20-admin-produto-com-erros")

        ctx.clear_cookies()
        entrar("cliente@lacakes.test", "Cliente@2026")
        pg.goto(pedido_url)
        foto("21-acompanhamento-em-preparo")

        # Loja fechada: aviso nas telas e pedido com previsão para o próximo dia de funcionamento
        fixar_relogio(FECHADA)
        pg.goto(f"{BASE}/vitrine")
        foto("27-loja-fechada-vitrine")
        pg.goto(f"{BASE}/produto/2")
        pg.fill("#quantidade", "2")
        pg.click("main form.form-qtd button[type=submit]")
        pg.goto(f"{BASE}/checkout")
        pg.click("text=Retirar na loja")
        pg.click("aside button[type=submit]")
        pg.wait_for_url("**/pagamento")
        pg.goto(pg.url + "?metodo=PIX")
        pg.click("main button:has-text('Já paguei')")
        pg.wait_for_url("**/confirmado")
        foto("28-pedido-loja-fechada")

        ctx.clear_cookies()
        entrar("admin@lacakes.test", "Admin@2026")
        pg.goto(f"{BASE}/admin/vendas")
        foto("25-admin-vendas")
        pg.goto(f"{BASE}/admin/loja")
        foto("26-admin-dados-da-loja")
        fixar_relogio(ABERTA)

        desk = nav.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        desk.goto(f"{BASE}/vitrine")
        desk.wait_for_timeout(150)
        desk.screenshot(path=str(DESTINO / "22-vitrine-computador.png"))
        print("ok 22-vitrine-computador")
        desk.goto(BASE)
        desk.wait_for_timeout(150)
        desk.screenshot(path=str(DESTINO / "29-tela-inicial-computador.png"), full_page=True)
        print("ok 29-tela-inicial-computador")
        desk.goto(f"{BASE}/login")
        desk.fill("#email", "admin@lacakes.test")
        desk.fill("#senha", "Admin@2026")
        desk.click("main button[type=submit]")
        desk.goto(f"{BASE}/admin/vendas")
        desk.wait_for_timeout(150)
        desk.screenshot(path=str(DESTINO / "30-admin-vendas-computador.png"), full_page=True)
        print("ok 30-admin-vendas-computador")
        nav.close()
    servidor.shutdown()


if __name__ == "__main__":
    main()
