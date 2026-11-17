"""Criação, pagamento, cancelamento e andamento de pedidos."""
from app.excecoes import ErroValidacao, EstoqueInsuficiente, RegraDeNegocio, TransicaoInvalida
from app.extensions import db
from app.models import (ItemPedido, Modalidade, Pagamento, Pedido, StatusPagamento, StatusPedido)
from app.services import frete, pagamento
from app.services import loja as servico_loja
from app.utils import formatar_moeda


def ler_modalidade(texto):
    try:
        return Modalidade((texto or "").upper())
    except ValueError:
        return None


def validar_endereco(modalidade, dados):
    """Valida o endereço quando a modalidade é entrega (RN07). Retorna (endereco_normalizado, erros)."""
    if modalidade != Modalidade.ENTREGA:
        return {}, {}
    erros = {}
    cep = frete.normalizar_cep(dados.get("cep"))
    if cep is None:
        erros["cep"] = "Informe um CEP com 8 dígitos."
    elif not frete.cep_atendido(cep):
        erros["cep"] = "Ainda não entregamos neste CEP. Você pode escolher Retirar na loja."
    endereco = {
        "cep": cep,
        "logradouro": (dados.get("logradouro") or "").strip(),
        "numero": (dados.get("numero") or "").strip(),
        "complemento": (dados.get("complemento") or "").strip() or None,
        "bairro": (dados.get("bairro") or "").strip(),
    }
    if len(endereco["logradouro"]) < 3:
        erros["logradouro"] = "Informe a rua ou avenida."
    if not endereco["numero"]:
        erros["numero"] = "Informe o número."
    if len(endereco["bairro"]) < 2:
        erros["bairro"] = "Informe o bairro."
    return endereco, erros


def criar_pedido(usuario, carrinho, modalidade_texto, dados_endereco):
    """US12: transforma o carrinho em pedido 'Aguardando pagamento', congelando os preços (RN15)."""
    itens = carrinho.itens()
    if not itens:
        raise RegraDeNegocio("Seu carrinho está vazio.")
    modalidade = ler_modalidade(modalidade_texto)
    if modalidade is None:
        raise ErroValidacao({"modalidade": "Escolha entrega ou retirada na loja."})
    endereco, erros = validar_endereco(modalidade, dados_endereco)
    if erros:
        raise ErroValidacao(erros)
    subtotal = sum(i.subtotal_centavos for i in itens)
    if not frete.atinge_pedido_minimo(subtotal):
        raise RegraDeNegocio(f"O pedido mínimo é de {formatar_moeda(frete.PEDIDO_MINIMO)}. "
                             "Adicione mais itens para continuar.")

    pedido = Pedido(usuario=usuario, modalidade=modalidade, **endereco)
    for item in itens:
        pedido.itens.append(ItemPedido(produto=item.produto, quantidade=item.quantidade,
                                       preco_unitario_centavos=item.produto.preco_centavos))
    pedido.calcular_totais(frete.calcular_taxa(modalidade, subtotal))
    pedido.registrar_status(StatusPedido.AGUARDANDO_PAGAMENTO, "Pedido recebido")
    db.session.add(pedido)
    db.session.commit()
    carrinho.limpar()
    return pedido


def pagar_pedido(pedido, metodo_texto, dados):
    """US13/US14/US15: processa o pagamento simulado. Retorna o Pagamento registrado (aprovado ou recusado)."""
    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        raise RegraDeNegocio("Este pedido não está aguardando pagamento.")
    metodo = pagamento.metodo_de_texto(metodo_texto)
    if metodo is None:
        raise ErroValidacao({"metodo": "Escolha crédito, débito ou Pix."})

    numero = None
    if metodo.usa_cartao:
        erros = pagamento.validar_cartao(dados.get("nome_cartao"), dados.get("numero_cartao"),
                                         dados.get("validade"), dados.get("cvv"))
        if erros:
            raise ErroValidacao(erros)
        numero = pagamento.limpar_numero_cartao(dados.get("numero_cartao"))

    # RN08: confere o estoque de novo antes de cobrar
    faltando = [i.produto.nome for i in pedido.itens
                if not i.produto.ativo or i.produto.estoque < i.quantidade]
    if faltando:
        raise EstoqueInsuficiente("Estoque insuficiente para: " + ", ".join(faltando)
                                  + ". Nenhum valor foi cobrado.")

    resultado = pagamento.cobrar(metodo, pedido.total_centavos, numero)
    registro = Pagamento(metodo=metodo, valor_centavos=pedido.total_centavos,
                         cartao_final=numero[-4:] if numero else None,
                         codigo_transacao=resultado.codigo_transacao,
                         status=StatusPagamento.APROVADO if resultado.aprovado else StatusPagamento.RECUSADO)
    pedido.pagamentos.append(registro)
    if resultado.aprovado:
        for item in pedido.itens:
            item.produto.baixar_estoque(item.quantidade)
        observacao = f"Pagamento aprovado – {metodo.rotulo}"
        # US25: pago com a loja fechada -> preparo e entrega no próximo dia de funcionamento
        loja, momento = servico_loja.dados_da_loja(), servico_loja.relogio()
        if not servico_loja.esta_aberta(loja, momento):
            pedido.previsao_preparo = servico_loja.dia_de_preparo(loja, momento)
            if pedido.previsao_preparo:
                observacao += f" (loja fechada: preparo em {pedido.previsao_preparo:%d/%m})"
        pedido.registrar_status(StatusPedido.PAGO, observacao)
    db.session.commit()
    return registro


def cancelar_pedido(pedido):
    """US18 / RN11: cancela antes do preparo; se estava pago, devolve o estoque e estorna (simulado)."""
    if not pedido.pode_cancelar:
        raise TransicaoInvalida("Este pedido não pode mais ser cancelado.")
    if pedido.status == StatusPedido.PAGO:
        for item in pedido.itens:
            item.produto.repor_estoque(item.quantidade)
        aprovado = pedido.pagamento_aprovado
        if aprovado:
            aprovado.status = StatusPagamento.ESTORNADO
    pedido.registrar_status(StatusPedido.CANCELADO, "Cancelado pelo cliente")
    db.session.commit()


def avancar_pedido(pedido):
    """US23 / RN10: a loja avança o pedido para a próxima etapa válida."""
    novo = pedido.avancar_status()
    db.session.commit()
    return novo


ORDEM_ADMIN = {
    StatusPedido.PAGO: 0, StatusPedido.EM_PREPARO: 1, StatusPedido.SAIU_PARA_ENTREGA: 2,
    StatusPedido.PRONTO_PARA_RETIRADA: 2, StatusPedido.AGUARDANDO_PAGAMENTO: 3, StatusPedido.ENTREGUE: 4,
    StatusPedido.CANCELADO: 5,
}


def pedidos_para_admin(status=None):
    """Lista para a loja: primeiro os que precisam de ação (pagos), depois os demais."""
    consulta = db.select(Pedido)
    if status:
        consulta = consulta.where(Pedido.status == status)
    pedidos = db.session.scalars(consulta.order_by(Pedido.criado_em.desc(), Pedido.id.desc())).all()
    return sorted(pedidos, key=lambda p: ORDEM_ADMIN[p.status])
