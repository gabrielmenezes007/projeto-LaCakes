"""Exceções das regras de negócio. Os controllers transformam essas exceções em mensagens na tela."""


class RegraDeNegocio(Exception):
    """Uma regra de negócio impediu a operação. A mensagem é mostrada ao usuário."""

    def __init__(self, mensagem):
        super().__init__(mensagem)
        self.mensagem = mensagem


class ErroValidacao(RegraDeNegocio):
    """Um ou mais campos de formulário estão inválidos. `erros` mapeia campo -> mensagem."""

    def __init__(self, erros, mensagem="Corrija os campos destacados para continuar."):
        super().__init__(mensagem)
        self.erros = erros


class EstoqueInsuficiente(RegraDeNegocio):
    """Não há estoque suficiente para a quantidade pedida (RN04/RN08)."""


class TransicaoInvalida(RegraDeNegocio):
    """O pedido não pode mudar para o status pedido (RN10/RN11)."""
