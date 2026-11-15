"""Entrega: área atendida (RN07), taxa (RN06) e pedido mínimo (RN05)."""
import re

from app.models import Modalidade

TAXA_ENTREGA = 800                # R$ 8,00
ENTREGA_GRATIS_A_PARTIR = 12000   # R$ 120,00
PEDIDO_MINIMO = 2500              # R$ 25,00
CEP_INICIAL = 17200001            # faixa de CEP de Jaú/SP
CEP_FINAL = 17229999


def normalizar_cep(cep):
    """Mantém só os dígitos. Retorna None se não tiver exatamente 8 dígitos."""
    digitos = re.sub(r"\D", "", cep or "")
    return digitos if len(digitos) == 8 else None


def cep_atendido(cep):
    digitos = normalizar_cep(cep)
    return digitos is not None and CEP_INICIAL <= int(digitos) <= CEP_FINAL


def calcular_taxa(modalidade, subtotal_centavos):
    if modalidade == Modalidade.RETIRADA:
        return 0
    if subtotal_centavos >= ENTREGA_GRATIS_A_PARTIR:
        return 0
    return TAXA_ENTREGA


def atinge_pedido_minimo(subtotal_centavos):
    return subtotal_centavos >= PEDIDO_MINIMO
