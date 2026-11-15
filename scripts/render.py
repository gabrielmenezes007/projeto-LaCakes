"""Renderiza diagramas Mermaid (.mmd) e páginas HTML em PNG.

Uso:
    python scripts/render.py mmd <entrada.mmd> <saida.png>
    python scripts/render.py html <entrada.html> <saida.png> [largura] [seletor]
    python scripts/render.py lote <pasta_mmd> <pasta_png>

Usa o Playwright com o Microsoft Edge já instalado no Windows (channel="msedge"),
então não é preciso baixar navegador. O Mermaid vem de scripts/node_modules
(instalado com `npm install` dentro de scripts/).
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).resolve().parent
MERMAID_JS = AQUI / "node_modules" / "mermaid" / "dist" / "mermaid.min.js"

PAGINA_MERMAID = """<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0;padding:24px;background:#fff;font-family:Arial,Helvetica,sans-serif}</style>
</head><body><pre class="mermaid" id="d"></pre>
<script>%s</script>
<script>
mermaid.initialize({startOnLoad:false, theme:'default',
  themeVariables:{fontFamily:'Arial, Helvetica, sans-serif', fontSize:'15px'},
  flowchart:{htmlLabels:true, curve:'basis'}, sequence:{useMaxWidth:false},
  class:{useMaxWidth:false}, er:{useMaxWidth:false}});
window.renderizar = async (codigo) => {
  const {svg} = await mermaid.render('g', codigo);
  document.getElementById('d').innerHTML = svg;
  const s = document.querySelector('#d svg');
  s.style.maxWidth = 'none';
  return true;
};
</script></body></html>"""


def _navegador(p):
    return p.chromium.launch(channel="msedge", headless=True)


def mmd_para_png(pagina, entrada, saida):
    codigo = pathlib.Path(entrada).read_text(encoding="utf-8")
    pagina.set_content(PAGINA_MERMAID % MERMAID_JS.read_text(encoding="utf-8"))
    pagina.evaluate("c => window.renderizar(c)", codigo)
    pagina.locator("#d svg").screenshot(path=str(saida))


def html_para_png(pagina, entrada, saida, largura=1200, seletor="body"):
    pagina.set_viewport_size({"width": int(largura), "height": 900})
    pagina.goto(pathlib.Path(entrada).resolve().as_uri())
    pagina.wait_for_timeout(150)
    if seletor == "body":
        pagina.screenshot(path=str(saida), full_page=True)
    else:
        pagina.locator(seletor).first.screenshot(path=str(saida))


def main(args):
    modo = args[0]
    with sync_playwright() as p:
        nav = _navegador(p)
        pagina = nav.new_page(device_scale_factor=2)
        if modo == "mmd":
            mmd_para_png(pagina, args[1], args[2])
        elif modo == "html":
            html_para_png(pagina, args[1], args[2], *(args[3:5]))
        elif modo == "lote":
            origem, destino = pathlib.Path(args[1]), pathlib.Path(args[2])
            destino.mkdir(parents=True, exist_ok=True)
            for arq in sorted(origem.glob("*.mmd")):
                mmd_para_png(pagina, arq, destino / (arq.stem + ".png"))
                print("ok", arq.name)
        nav.close()


if __name__ == "__main__":
    main(sys.argv[1:])
