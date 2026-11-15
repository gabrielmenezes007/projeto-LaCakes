"""Funções auxiliares de formatação e conversão usadas nos controllers e templates."""
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse


def formatar_moeda(centavos):
    """1234 -> 'R$ 12,34'; 123456 -> 'R$ 1.234,56'."""
    centavos = int(centavos or 0)
    reais, cent = divmod(abs(centavos), 100)
    inteiro = f"{reais:,}".replace(",", ".")
    sinal = "-" if centavos < 0 else ""
    return f"{sinal}R$ {inteiro},{cent:02d}"


def reais_para_centavos(texto):
    """Converte '14,90', '14.90', 'R$ 1.234,56' em centavos. Retorna None se não for um número válido."""
    if texto is None:
        return None
    s = str(texto).replace("R$", "").replace(" ", "").strip()
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d{1,2})?", s):
        return None
    try:
        return int((Decimal(s) * 100).quantize(Decimal("1")))
    except InvalidOperation:
        return None


def centavos_para_texto(centavos):
    """1490 -> '14,90' (para preencher campos de formulário)."""
    return f"{int(centavos) // 100},{int(centavos) % 100:02d}"


def formatar_cep(cep):
    if cep and len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    return cep or ""


def formatar_data(dt):
    return dt.strftime("%d/%m/%Y às %H:%M") if dt else ""


def url_segura(destino):
    """Aceita só caminhos internos no parâmetro 'next' (evita redirecionar para outro site)."""
    if not destino:
        return False
    partes = urlparse(destino)
    return not partes.netloc and not partes.scheme and destino.startswith("/") and not destino.startswith("//")


def para_inteiro(valor, padrao=None):
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return padrao


def registrar_filtros(app):
    app.jinja_env.filters["moeda"] = formatar_moeda
    app.jinja_env.filters["cep"] = formatar_cep
    app.jinja_env.filters["data"] = formatar_data
