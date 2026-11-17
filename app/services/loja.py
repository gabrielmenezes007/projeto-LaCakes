"""Dados da loja e horário de funcionamento: loja aberta/fechada e dia de preparo dos pedidos (US24 e US25)."""
import re
from datetime import time, timedelta

from sqlalchemy.exc import SQLAlchemyError

from app.excecoes import ErroValidacao
from app.extensions import db
from app.models import Loja
from app.models.base import agora
from app.models.loja import formatar_hora

PADRAO = {"endereco": "Rua das Flores, 120 – Jaú/SP", "dias_funcionamento": "012345",
          "abre_as": time(9, 0), "fecha_as": time(19, 0)}
DIAS_ABREVIADOS = ["seg.", "ter.", "qua.", "qui.", "sex.", "sáb.", "dom."]
DIAS_POR_EXTENSO = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado",
                    "domingo"]


def relogio():
    """Momento atual usado nas regras de horário. Os testes trocam esta função para fixar o dia e a hora."""
    return agora()


def dados_da_loja():
    """Registro da loja no banco. Se ainda não existir, usa os dados padrão (sem gravar)."""
    try:
        loja = db.session.scalar(db.select(Loja).order_by(Loja.id).limit(1))
    except SQLAlchemyError:
        db.session.rollback()
        loja = None
    return loja or Loja(**PADRAO)


# ------------------------------------------------------------------ regras de horário
def esta_aberta(loja, momento):
    """A loja está aberta se hoje é dia de funcionamento e o horário está entre a abertura e o fechamento."""
    return momento.weekday() in loja.dias and loja.abre_as <= momento.time() < loja.fecha_as


def dia_de_preparo(loja, momento):
    """Dia em que um pedido pago neste momento será preparado e entregue.

    Hoje, se a loja funciona hoje e ainda não fechou (antes das 9h, o pedido sai quando a loja abrir).
    Depois do fechamento ou em dia sem funcionamento, o próximo dia em que a loja abre
    (ex.: segunda a sexta depois das 19h -> amanhã; sábado depois das 19h -> segunda).
    """
    if not loja.dias:
        return None
    hoje = momento.date()
    if momento.weekday() in loja.dias and momento.time() < loja.fecha_as:
        return hoje
    for n in range(1, 8):
        dia = hoje + timedelta(days=n)
        if dia.weekday() in loja.dias:
            return dia
    return None


def dia_relativo(dia, hoje):
    """'hoje', 'amanhã', o dia da semana (até 6 dias à frente) ou a data."""
    diferenca = (dia - hoje).days
    if diferenca == 0:
        return "hoje"
    if diferenca == 1:
        return "amanhã"
    if 1 < diferenca < 7:
        return DIAS_POR_EXTENSO[dia.weekday()]
    return f"em {dia:%d/%m}"


def texto_previsao(dia, loja=None, momento=None):
    """Texto do selo de pedido feito com a loja fechada, ex.: 'Preparado e entregue amanhã (ter., 17/11)'."""
    loja = loja or dados_da_loja()
    momento = momento or relogio()
    hoje = momento.date()
    relativo = dia_relativo(dia, hoje)
    if dia < hoje:
        return f"Previsto para {dia:%d/%m}"
    if relativo == "hoje":
        if momento.time() < loja.abre_as:
            return f"Preparado e entregue hoje, a partir das {formatar_hora(loja.abre_as)}"
        return "Preparado e entregue hoje"
    if relativo == "amanhã":
        return f"Preparado e entregue amanhã ({DIAS_ABREVIADOS[dia.weekday()]}, {dia:%d/%m})"
    if relativo.startswith("em "):
        return f"Preparado e entregue {relativo}"
    return f"Preparado e entregue {relativo} ({dia:%d/%m})"


def situacao(loja, momento):
    """Resumo para as telas: aberta/fechada, quando abre e o aviso para quem pedir agora."""
    if esta_aberta(loja, momento):
        return {"aberta": True, "resumo": f"Aberto agora · fecha às {formatar_hora(loja.fecha_as)}",
                "aviso": None, "dia_preparo": momento.date(), "fecha_as": formatar_hora(loja.fecha_as)}
    dia = dia_de_preparo(loja, momento)
    if dia is None:
        return {"aberta": False, "resumo": "Fechado no momento", "dia_preparo": None,
                "aviso": "A loja está sem dias de funcionamento cadastrados."}
    abre = f"{dia_relativo(dia, momento.date())} às {formatar_hora(loja.abre_as)}"
    previsao = texto_previsao(dia, loja, momento)
    return {"aberta": False, "resumo": f"Fechado agora · abre {abre}", "dia_preparo": dia,
            "aviso": f"A loja está fechada agora e abre {abre}. Pedidos feitos agora serão "
                     f"{previsao.replace('Preparado e entregue', 'preparados e entregues')}."}


# ------------------------------------------------------------------ cadastro (área administrativa)
def ler_hora(texto):
    """'09:00' ou '9:00' -> time(9, 0). Retorna None se não for um horário válido."""
    achado = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", (texto or "").strip())
    return time(int(achado.group(1)), int(achado.group(2))) if achado else None


def form_da_loja(loja):
    return {"endereco": loja.endereco, "dias": [str(d) for d in loja.dias],
            "abre_as": loja.abre_as.strftime("%H:%M"), "fecha_as": loja.fecha_as.strftime("%H:%M")}


def salvar_dados(dados, dias_marcados):
    """US24: valida e grava endereço, dias e horário de funcionamento."""
    erros = {}
    endereco = (dados.get("endereco") or "").strip()
    if not 10 <= len(endereco) <= 150:
        erros["endereco"] = "Informe o endereço completo, com rua, número e cidade (10 a 150 caracteres)."
    dias = sorted({int(d) for d in dias_marcados if len(d) == 1 and d in "0123456"})
    if not dias:
        erros["dias"] = "Marque pelo menos um dia de funcionamento."
    abre, fecha = ler_hora(dados.get("abre_as")), ler_hora(dados.get("fecha_as"))
    if abre is None:
        erros["abre_as"] = "Informe o horário de abertura (ex.: 09:00)."
    if fecha is None:
        erros["fecha_as"] = "Informe o horário de fechamento (ex.: 19:00)."
    if abre is not None and fecha is not None and fecha <= abre:
        erros["fecha_as"] = "O fechamento precisa ser depois da abertura."
    if erros:
        raise ErroValidacao(erros)

    loja = db.session.scalar(db.select(Loja).order_by(Loja.id).limit(1))
    if loja is None:
        loja = Loja()
        db.session.add(loja)
    loja.endereco = endereco
    loja.dias_funcionamento = "".join(str(d) for d in dias)
    loja.abre_as, loja.fecha_as = abre, fecha
    db.session.commit()
    return loja

