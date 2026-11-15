"""Gera o diagrama de casos de uso (SVG) e o mapa de afinidade (HTML) e renderiza em PNG.

Uso: python scripts/gerar_figuras.py
"""
import html
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from conteudo_planejamento import HISTORIAS, TEMAS, LOJA  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DIAG = RAIZ / "docs" / "planejamento" / "diagramas"
IMG = RAIZ / "docs" / "planejamento" / "img"

RX, RY = 112, 30
COL_A, COL_B = 400, 780
UCS = {
    "UC01": (COL_A, 90, "Consultar vitrine"),
    "UC02": (COL_A, 180, "Ver detalhes do cupcake"),
    "UC03": (COL_A, 270, "Cadastrar cliente"),
    "UC05": (COL_A, 360, "Gerenciar carrinho"),
    "UC04": (COL_A, 460, "Autenticar usuário"),
    "UC06": (COL_A, 570, "Finalizar pedido"),
    "UC08": (COL_A, 680, "Acompanhar pedido"),
    "UC09": (COL_A, 780, "Cancelar pedido"),
    "UC10": (COL_B, 170, "Manter produtos"),
    "UC11": (COL_B, 300, "Gerenciar pedidos da loja"),
    "UC07": (COL_B, 570, "Realizar pagamento"),
}
ATORES = {
    "Visitante": (110, 230),
    "Cliente": (110, 610),
    "Administrador": (1100, 300),
    "Serviço de pagamento": (1100, 570),
}
ASSOC = [("Visitante", u) for u in ("UC01", "UC02", "UC03", "UC05")] + \
        [("Cliente", u) for u in ("UC04", "UC06", "UC08", "UC09")] + \
        [("Administrador", u) for u in ("UC10", "UC11", "UC04")] + \
        [("Serviço de pagamento", "UC07")]


def ator(nome, x, y, externo=False):
    s = [f'<circle cx="{x}" cy="{y-48}" r="13" class="tr"/>',
         f'<line x1="{x}" y1="{y-35}" x2="{x}" y2="{y}" class="tr"/>',
         f'<line x1="{x-22}" y1="{y-22}" x2="{x+22}" y2="{y-22}" class="tr"/>',
         f'<line x1="{x}" y1="{y}" x2="{x-18}" y2="{y+28}" class="tr"/>',
         f'<line x1="{x}" y1="{y}" x2="{x+18}" y2="{y+28}" class="tr"/>',
         f'<text x="{x}" y="{y+48}" class="at">{html.escape(nome)}</text>']
    if externo:
        s.append(f'<text x="{x}" y="{y+66}" class="st">«sistema externo»</text>')
    return "\n".join(s)


def borda_elipse(cx, cy, px, py):
    """Ponto na borda da elipse na direção de (px, py)."""
    import math
    ang = math.atan2(py - cy, px - cx)
    return cx + RX * math.cos(ang), cy + RY * math.sin(ang)


def diagrama_casos_de_uso():
    w, h = 1220, 860
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Arial, Helvetica, sans-serif">',
         '<defs><marker id="seta" markerWidth="12" markerHeight="10" refX="11" refY="5" orient="auto"><path d="M0,0 L12,5 L0,10" fill="none" stroke="#333" stroke-width="1.5"/></marker>'
         '<marker id="tri" markerWidth="18" markerHeight="16" refX="17" refY="8" orient="auto"><path d="M0,0 L18,8 L0,16 Z" fill="#fff" stroke="#333" stroke-width="1.5"/></marker></defs>',
         '<style>.tr{stroke:#333;stroke-width:2;fill:#fff}.at{font-size:15px;text-anchor:middle;font-weight:bold}'
         '.st{font-size:12px;text-anchor:middle;fill:#555}.uc{fill:#F3E8F1;stroke:#5D2452;stroke-width:1.6}'
         '.ut{font-size:14px;text-anchor:middle;dominant-baseline:middle}.id{font-size:11px;text-anchor:middle;fill:#5D2452;font-weight:bold}'
         '.as{stroke:#444;stroke-width:1.4}.dep{stroke:#444;stroke-width:1.4;stroke-dasharray:6 4;fill:none}.rot{font-size:12px;fill:#333;font-style:italic}</style>',
         '<rect x="0" y="0" width="100%" height="100%" fill="#fff"/>',
         f'<rect x="250" y="30" width="720" height="810" rx="6" fill="#FAF4ED" stroke="#112F24" stroke-width="2"/>',
         f'<text x="610" y="55" font-size="16" font-weight="bold" text-anchor="middle" fill="#112F24">Sistema {html.escape(LOJA)}</text>']
    for a, u in ASSOC:
        ax, ay = ATORES[a]
        cx, cy, _ = UCS[u]
        ox = ax + (28 if ax < 600 else -28)
        bx, by = borda_elipse(cx, cy, ox, ay - 20)
        p.append(f'<line x1="{ox}" y1="{ay-20}" x2="{bx:.0f}" y2="{by:.0f}" class="as"/>')
    # generalização Cliente -> Visitante
    p.append('<line x1="110" y1="530" x2="110" y2="312" class="as" marker-end="url(#tri)"/>')
    # include / extend
    def dep(o, d, rot, dx=0):
        ox, oy, _ = UCS[o]
        tx, ty, _ = UCS[d]
        x1, y1 = borda_elipse(ox, oy, tx, ty)
        x2, y2 = borda_elipse(tx, ty, ox, oy)
        p.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" class="dep" marker-end="url(#seta)"/>')
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2
        p.append(f'<text x="{mx:.0f}" y="{my-6:.0f}" class="rot">{rot}</text>')
    dep("UC06", "UC04", "«include»", 8)
    dep("UC06", "UC07", "«include»", -30)
    dep("UC02", "UC01", "«extend»", 8)
    dep("UC09", "UC08", "«extend»", 8)
    for uid, (cx, cy, nome) in UCS.items():
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{RX}" ry="{RY}" class="uc"/>')
        p.append(f'<text x="{cx}" y="{cy-10}" class="id">{uid}</text>')
        p.append(f'<text x="{cx}" y="{cy+8}" class="ut">{html.escape(nome)}</text>')
    for nome, (x, y) in ATORES.items():
        p.append(ator(nome, x, y, externo=nome.startswith("Serviço")))
    p.append("</svg>")
    return "\n".join(p)


def mapa_afinidade():
    cols = []
    for tid, (nome, cor) in TEMAS.items():
        notas = "".join(
            f'<div class="nota" style="background:{cor}"><b>{h["id"]}</b> {html.escape(h["titulo"])}'
            f'<small>{html.escape(h["requerente"])} · Prioridade {h["prioridade"]} · {h["pontos"]} pts</small></div>'
            for h in HISTORIAS if h["tema"] == tid)
        cols.append(f'<section><h2 style="border-color:{cor}">{tid} · {html.escape(nome)}</h2>{notas}</section>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;padding:28px;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#2b2b2b;width:1400px}}
h1{{margin:0 0 6px;font-size:24px;color:#112F24}} p{{margin:0 0 20px;color:#555}}
.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}}
section{{background:#f7f5f2;border-radius:10px;padding:12px}}
h2{{font-size:15px;margin:0 0 12px;padding-bottom:6px;border-bottom:4px solid}}
.nota{{padding:10px 10px 8px;margin-bottom:10px;border-radius:3px;box-shadow:2px 3px 6px rgba(0,0,0,.18);font-size:14px;line-height:1.3}}
.nota small{{display:block;margin-top:6px;font-size:11px;color:#444}}
</style></head><body><div id="mapa"><h1>Mapa de afinidade – histórias de usuário da {html.escape(LOJA)}</h1>
<p>Cartões agrupados por eixo temático (6 temas, {len(HISTORIAS)} histórias).</p>
<div class="grid">{''.join(cols)}</div></div></body></html>"""


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    svg = diagrama_casos_de_uso()
    (DIAG / "01-diagrama-casos-de-uso.svg").write_text(svg, encoding="utf-8")
    pagina = DIAG / "01-diagrama-casos-de-uso.html"
    pagina.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0}}</style></head><body>{svg}</body></html>', encoding="utf-8")
    afin = DIAG / "00-mapa-de-afinidade.html"
    afin.write_text(mapa_afinidade(), encoding="utf-8")
    r = [sys.executable, str(RAIZ / "scripts" / "render.py"), "html"]
    subprocess.run(r + [str(pagina), str(IMG / "01-diagrama-casos-de-uso.png"), "1220", "svg"], check=True)
    subprocess.run(r + [str(afin), str(IMG / "00-mapa-de-afinidade.png"), "1460", "#mapa"], check=True)
    pagina.unlink()
    print("figuras geradas")


if __name__ == "__main__":
    main()
