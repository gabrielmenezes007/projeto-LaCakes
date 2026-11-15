"""Serviço de pagamento SIMULADO (RN09). Não há cobrança real.

Regra de teste: cartões (crédito ou débito) terminados em 0000 são recusados.
"""
import re
import secrets
from dataclasses import dataclass
from datetime import date

from app.models import MetodoPagamento

FINAL_RECUSADO = "0000"


@dataclass
class ResultadoCobranca:
    aprovado: bool
    codigo_transacao: str
    motivo: str = ""


def limpar_numero_cartao(numero):
    return re.sub(r"\D", "", numero or "")


def validar_cartao(nome, numero, validade, cvv, hoje=None):
    """Retorna um dicionário campo -> mensagem com os erros encontrados (vazio se estiver tudo certo)."""
    hoje = hoje or date.today()
    erros = {}
    if len((nome or "").strip()) < 3:
        erros["nome_cartao"] = "Informe o nome como está impresso no cartão."
    digitos = limpar_numero_cartao(numero)
    if len(digitos) != 16:
        erros["numero_cartao"] = "O número do cartão precisa ter 16 dígitos."
    m = re.fullmatch(r"\s*(\d{2})\s*/\s*(\d{2}|\d{4})\s*", validade or "")
    if not m:
        erros["validade"] = "Use o formato MM/AA."
    else:
        mes, ano = int(m.group(1)), int(m.group(2))
        ano = ano + 2000 if ano < 100 else ano
        if not 1 <= mes <= 12:
            erros["validade"] = "Mês inválido."
        elif (ano, mes) < (hoje.year, hoje.month):
            erros["validade"] = "Este cartão está vencido."
    if not re.fullmatch(r"\d{3}", (cvv or "").strip()):
        erros["cvv"] = "O CVV tem 3 dígitos."
    return erros


def cobrar(metodo, valor_centavos, numero_cartao=None):
    """Simula a resposta de um serviço de pagamento."""
    codigo = f"SIM-{secrets.token_hex(6).upper()}"
    if metodo.usa_cartao and limpar_numero_cartao(numero_cartao).endswith(FINAL_RECUSADO):
        return ResultadoCobranca(False, codigo, "Cartão não autorizado pelo emissor (simulação).")
    return ResultadoCobranca(True, codigo)


def gerar_codigo_pix(pedido):
    """Código "copia e cola" fictício, só para demonstração."""
    valor = f"{pedido.total_centavos / 100:.2f}"
    return (f"00020126580014BR.GOV.BCB.PIX0136lacakes-demo-{pedido.id:06d}"
            f"5204000053039865406{valor}5802BR5907LACAKES6004JAU62070503***6304DEMO")


def metodo_de_texto(texto):
    try:
        return MetodoPagamento((texto or "").upper())
    except ValueError:
        return None
