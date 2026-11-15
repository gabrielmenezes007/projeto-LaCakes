"""Gera as ilustrações SVG dos cupcakes do cardápio inicial (app/static/img/cupcakes) e o favicon.

Uso: python scripts/gerar_ilustracoes.py
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "app" / "static" / "img" / "cupcakes"

# nome do arquivo: (fundo1, fundo2, cobertura, sombra da cobertura, enfeite, cor do enfeite)
SABORES = {
    "red-velvet": ("#FAD0DC", "#F3A6BC", "#FFF8F2", "#F1DCD2", "migalhas", "#B3202A"),
    "ninho-nutella": ("#F9E3C4", "#E9B98A", "#FFFDF7", "#EFE6D6", "calda", "#5A3825"),
    "limao-siciliano": ("#FFF6B8", "#F4DC6A", "#FFFBEA", "#EED9A8", "limao", "#E6C619"),
    "cenoura-brigadeiro": ("#FFD9B8", "#F2A36B", "#5A3220", "#47271A", "granulado", "#3A1F14"),
    "chocolate-70": ("#D9C2B5", "#8D6656", "#3B2219", "#2B1811", "raspas", "#5C3A2C"),
    "morango-chantilly": ("#FFD1D6", "#F28B9A", "#FFFFFF", "#F0E4E6", "morango", "#D7263D"),
    "pistache-frutas-vermelhas": ("#DCEFD0", "#A9D18E", "#C5DE9A", "#A9C67E", "frutas", "#B0172E"),
    "panetone-trufado": ("#F5E1C8", "#D9A86C", "#F7E7C6", "#E6CFA2", "frutas-cristalizadas", "#C0392B"),
    "padrao": ("#F3E8F1", "#EADBE6", "#FFFFFF", "#EFE3EC", "cereja", "#5D2452"),
}

FORMINHA = "#5D2452"
FORMINHA_LISTRA = "#7B3A6F"


def enfeite(tipo, cor):
    if tipo == "migalhas":
        return "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{cor}"/>' for x, y in [(185, 92), (205, 84), (222, 96), (198, 104), (214, 110)])
    if tipo == "calda":
        return f'<path d="M150 128 q15 18 30 0 q15 18 30 0 q15 18 30 0 q15 18 30 0" stroke="{cor}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    if tipo == "limao":
        return (f'<circle cx="200" cy="82" r="22" fill="{cor}"/><circle cx="200" cy="82" r="17" fill="#FFF3A0"/>'
                + "".join(f'<line x1="200" y1="82" x2="{x}" y2="{y}" stroke="{cor}" stroke-width="2"/>'
                          for x, y in [(200, 65), (215, 74), (215, 90), (200, 99), (185, 90), (185, 74)]))
    if tipo == "granulado":
        cores = [cor, "#6B3B24", cor]
        pts = [(170, 110, 20), (190, 96, -30), (212, 104, 45), (230, 118, -10), (182, 126, 70), (220, 88, 15), (200, 116, -60)]
        return "".join(f'<rect x="{x}" y="{y}" width="12" height="4" rx="2" fill="{cores[i % 3]}" transform="rotate({r} {x} {y})"/>'
                       for i, (x, y, r) in enumerate(pts))
    if tipo == "raspas":
        return "".join(f'<path d="M{x} {y} q6 -8 12 0" stroke="{cor}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                       for x, y in [(178, 96), (204, 86), (222, 104), (190, 116)])
    if tipo == "morango":
        return (f'<path d="M200 60 c-22 0 -26 22 -14 38 l14 16 l14 -16 c12 -16 8 -38 -14 -38z" fill="{cor}"/>'
                '<path d="M188 62 l12 -10 l12 10 l-12 4z" fill="#3E8E41"/>'
                + "".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#FFE08A"/>' for x, y in [(194, 76), (206, 78), (200, 90), (192, 92), (208, 92)]))
    if tipo == "frutas":
        return "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="{cor}"/><circle cx="{x - 3}" cy="{y - 3}" r="2.5" fill="#fff" opacity=".6"/>'
                       for x, y in [(186, 84), (206, 76), (222, 92)]) + '<path d="M196 70 q8 -12 18 -10" stroke="#3E8E41" stroke-width="3" fill="none"/>'
    if tipo == "frutas-cristalizadas":
        cores = [cor, "#2E8B57", "#F39C12", cor, "#2E8B57"]
        return "".join(f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" fill="{cores[i]}" transform="rotate({15 * i} {x} {y})"/>'
                       for i, (x, y) in enumerate([(176, 100), (196, 88), (216, 98), (186, 116), (210, 114)]))
    # cereja
    return (f'<circle cx="200" cy="74" r="14" fill="{cor}"/><circle cx="195" cy="69" r="4" fill="#fff" opacity=".5"/>'
            f'<path d="M202 60 q6 -16 18 -18" stroke="#3E5A2E" stroke-width="3" fill="none"/>')


def cupcake(fundo1, fundo2, cobertura, sombra, tipo, cor):
    listras = "".join(f'<line x1="{x}" y1="172" x2="{x + (200 - x) * 0.12:.0f}" y2="262" stroke="{FORMINHA_LISTRA}" stroke-width="6"/>'
                      for x in range(152, 252, 16))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img">
<defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{fundo1}"/><stop offset="1" stop-color="{fundo2}"/></linearGradient>
<clipPath id="c"><polygon points="138,170 262,170 246,262 154,262"/></clipPath></defs>
<rect width="400" height="300" fill="url(#f)"/>
<ellipse cx="200" cy="268" rx="78" ry="10" fill="#000" opacity=".12"/>
<polygon points="138,170 262,170 246,262 154,262" fill="{FORMINHA}"/>
<g clip-path="url(#c)">{listras}</g>
<ellipse cx="200" cy="168" rx="80" ry="22" fill="{sombra}"/>
<ellipse cx="200" cy="158" rx="76" ry="24" fill="{cobertura}"/>
<ellipse cx="200" cy="134" rx="60" ry="22" fill="{sombra}"/>
<ellipse cx="200" cy="126" rx="56" ry="21" fill="{cobertura}"/>
<ellipse cx="200" cy="104" rx="38" ry="18" fill="{sombra}"/>
<ellipse cx="200" cy="98" rx="34" ry="17" fill="{cobertura}"/>
<ellipse cx="184" cy="120" rx="14" ry="5" fill="#fff" opacity=".35"/>
{enfeite(tipo, cor)}
</svg>
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#5D2452"/>
<polygon points="18,34 46,34 42,54 22,54" fill="#FAF4ED"/>
<ellipse cx="32" cy="32" rx="16" ry="7" fill="#F3E8F1"/><ellipse cx="32" cy="25" rx="11" ry="6" fill="#F3E8F1"/>
<circle cx="32" cy="16" r="4" fill="#29604C"/>
</svg>
"""


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, cores in SABORES.items():
        (DESTINO / f"{nome}.svg").write_text(cupcake(*cores), encoding="utf-8")
    (DESTINO.parent / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    print(f"{len(SABORES)} ilustrações geradas em {DESTINO}")


if __name__ == "__main__":
    main()
