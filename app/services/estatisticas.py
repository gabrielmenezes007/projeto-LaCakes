"""Estatísticas de vendas para a área administrativa (US26).

Conta como venda o pedido com pagamento aprovado que não foi cancelado (STATUS_VENDIDOS), pelo dia em que o
pedido foi feito.
"""
from datetime import datetime, time, timedelta

from app.extensions import db
from app.models import Pedido, StatusPedido
from app.models.pedido import STATUS_VENDIDOS


def _pedidos_entre(inicio, fim):
    """Pedidos feitos de `inicio` (inclusive) até `fim` (exclusive), datas sem hora."""
    return db.session.scalars(
        db.select(Pedido).where(Pedido.criado_em >= datetime.combine(inicio, time.min),
                                Pedido.criado_em < datetime.combine(fim, time.min))
    ).all()


def _ranking(contagem):
    """{chave: [quantidade, valor]} -> lista ordenada pela quantidade, com a % da maior (para a barra)."""
    maior = max((q for q, _ in contagem.values()), default=0)
    linhas = [{"nome": nome, "quantidade": q, "valor": v, "percentual": round(100 * q / maior) if maior else 0}
              for nome, (q, v) in contagem.items()]
    return sorted(linhas, key=lambda linha: (-linha["quantidade"], linha["nome"]))


def resumo_do_dia(dia):
    """Totais do dia: valor vendido, pedidos, cupcakes, ticket médio e quebras por sabor, categoria etc."""
    pedidos = _pedidos_entre(dia, dia + timedelta(days=1))
    vendidos = [p for p in pedidos if p.status in STATUS_VENDIDOS]
    total = sum(p.total_centavos for p in vendidos)

    por_sabor, por_categoria, por_modalidade, por_pagamento = {}, {}, {}, {}
    for pedido in vendidos:
        for item in pedido.itens:
            for chave, destino in ((item.produto.nome, por_sabor), (item.produto.categoria.nome, por_categoria)):
                atual = destino.setdefault(chave, [0, 0])
                atual[0] += item.quantidade
                atual[1] += item.subtotal_centavos
        atual = por_modalidade.setdefault(pedido.modalidade.rotulo, [0, 0])
        atual[0] += 1
        atual[1] += pedido.total_centavos
        pagamento = pedido.pagamento_aprovado
        if pagamento:
            atual = por_pagamento.setdefault(pagamento.metodo.rotulo, [0, 0])
            atual[0] += 1
            atual[1] += pedido.total_centavos

    return {
        "dia": dia,
        "total": total,
        "pedidos": len(vendidos),
        "cupcakes": sum(p.quantidade_itens for p in vendidos),
        "ticket_medio": total // len(vendidos) if vendidos else 0,
        "taxas_entrega": sum(p.taxa_entrega_centavos for p in vendidos),
        "cancelados": sum(1 for p in pedidos if p.status == StatusPedido.CANCELADO),
        "aguardando": sum(1 for p in pedidos if p.status == StatusPedido.AGUARDANDO_PAGAMENTO),
        "por_sabor": _ranking(por_sabor),
        "por_categoria": _ranking(por_categoria),
        "por_modalidade": _ranking(por_modalidade),
        "por_pagamento": _ranking(por_pagamento),
    }


def ultimos_dias(ate, quantidade=7):
    """Vendas de cada um dos últimos `quantidade` dias até `ate` (inclusive), do mais recente para o mais antigo."""
    inicio = ate - timedelta(days=quantidade - 1)
    dias = {inicio + timedelta(days=n): {"pedidos": 0, "cupcakes": 0, "total": 0} for n in range(quantidade)}
    for pedido in _pedidos_entre(inicio, ate + timedelta(days=1)):
        if pedido.status in STATUS_VENDIDOS:
            linha = dias[pedido.criado_em.date()]
            linha["pedidos"] += 1
            linha["cupcakes"] += pedido.quantidade_itens
            linha["total"] += pedido.total_centavos
    maior = max((d["total"] for d in dias.values()), default=0)
    return [{"dia": dia, **valores, "percentual": round(100 * valores["total"] / maior) if maior else 0}
            for dia, valores in sorted(dias.items(), reverse=True)]
