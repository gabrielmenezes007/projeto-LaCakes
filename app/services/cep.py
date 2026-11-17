"""Busca do endereço pelo CEP (US28), para preencher rua e bairro no checkout.

Usa o serviço público ViaCEP (https://viacep.com.br). Se ele estiver fora do ar, o cliente digita o endereço
normalmente: a busca só ajuda, nunca impede o pedido.
"""
import json
from urllib.request import Request, urlopen

from app.services import frete

URL_VIACEP = "https://viacep.com.br/ws/{cep}/json/"
TEMPO_LIMITE = 4  # segundos


def consultar_viacep(cep):
    """Consulta o ViaCEP. Retorna o dicionário da resposta, ou None se o CEP não existir.

    Levanta OSError (sem internet, tempo esgotado) ou ValueError (resposta inválida).
    """
    pedido = Request(URL_VIACEP.format(cep=cep), headers={"User-Agent": "LaCakes/1.0"})
    with urlopen(pedido, timeout=TEMPO_LIMITE) as resposta:  # noqa: S310 (URL fixa, https)
        dados = json.loads(resposta.read().decode("utf-8"))
    if not isinstance(dados, dict):
        raise ValueError("resposta inesperada do ViaCEP")
    return None if dados.get("erro") else dados


def buscar_endereco(cep_digitado):
    """Resultado para a tela: {'ok': True, 'logradouro', 'bairro', 'cidade', 'uf'} ou {'ok': False, 'mensagem'}."""
    cep = frete.normalizar_cep(cep_digitado)
    if cep is None:
        return {"ok": False, "mensagem": "Informe um CEP com 8 dígitos."}
    if not frete.cep_atendido(cep):
        # Nem consulta: a loja só entrega em Jaú (RN07)
        return {"ok": False, "fora_da_area": True,
                "mensagem": "Ainda não entregamos neste CEP. Você pode escolher Retirar na loja."}
    try:
        dados = consultar_viacep(cep)
    except (OSError, ValueError):
        return {"ok": False, "mensagem": "Não foi possível buscar o CEP agora. Preencha a rua e o bairro."}
    if dados is None:
        return {"ok": False, "mensagem": "CEP não encontrado. Confira o número ou preencha a rua e o bairro."}
    return {"ok": True, "cep": cep, "logradouro": dados.get("logradouro") or "", "bairro": dados.get("bairro") or "",
            "cidade": dados.get("localidade") or "", "uf": dados.get("uf") or ""}
