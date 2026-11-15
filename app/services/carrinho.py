"""Carrinho de compras guardado na sessão do navegador (não vai para o banco)."""
from dataclasses import dataclass

from app.excecoes import EstoqueInsuficiente, RegraDeNegocio
from app.extensions import db
from app.models import Produto

CHAVE_SESSAO = "carrinho"
MAXIMO_POR_ITEM = 24  # RN04


@dataclass
class ItemCarrinho:
    produto: Produto
    quantidade: int

    @property
    def subtotal_centavos(self):
        return self.produto.preco_centavos * self.quantidade


class Carrinho:
    def __init__(self, sessao):
        self.sessao = sessao

    # ------------------------------------------------------------ armazenamento
    def _dados(self):
        return dict(self.sessao.get(CHAVE_SESSAO, {}))

    def _salvar(self, dados):
        self.sessao[CHAVE_SESSAO] = dados
        self.sessao.modified = True

    def quantidade_de(self, produto_id):
        return self._dados().get(str(produto_id), 0)

    # ----------------------------------------------------------------- regras
    @staticmethod
    def _validar(produto, quantidade):
        if quantidade < 1:
            raise RegraDeNegocio("A quantidade precisa ser de pelo menos 1 unidade.")
        if not produto.ativo:
            raise RegraDeNegocio("Este cupcake não está mais disponível.")
        if produto.estoque <= 0:
            raise EstoqueInsuficiente("Este cupcake esgotou hoje.")
        if quantidade > MAXIMO_POR_ITEM:
            raise RegraDeNegocio(f"O limite é de {MAXIMO_POR_ITEM} unidades por sabor.")
        if quantidade > produto.estoque:
            unidade = "unidade" if produto.estoque == 1 else "unidades"
            raise EstoqueInsuficiente(f"Só temos {produto.estoque} {unidade} deste sabor hoje.")

    def adicionar(self, produto, quantidade):
        """Soma a quantidade à que já está no carrinho (US08)."""
        nova = self.quantidade_de(produto.id) + quantidade
        if quantidade < 1:
            nova = quantidade
        self._validar(produto, nova)
        dados = self._dados()
        dados[str(produto.id)] = nova
        self._salvar(dados)

    def atualizar(self, produto, quantidade):
        """Troca a quantidade de um item; zero remove o item (US09)."""
        if quantidade <= 0:
            self.remover(produto.id)
            return
        self._validar(produto, quantidade)
        dados = self._dados()
        dados[str(produto.id)] = quantidade
        self._salvar(dados)

    def remover(self, produto_id):
        dados = self._dados()
        dados.pop(str(produto_id), None)
        self._salvar(dados)

    def limpar(self):
        self._salvar({})

    # --------------------------------------------------------------- consultas
    def itens(self):
        """Itens com o produto carregado. Produtos apagados ou desativados saem do carrinho."""
        dados = self._dados()
        itens, mudou = [], False
        for pid, qtd in dados.items():
            produto = db.session.get(Produto, int(pid))
            if produto is None or not produto.ativo:
                mudou = True
                continue
            itens.append(ItemCarrinho(produto, qtd))
        if mudou:
            self._salvar({str(i.produto.id): i.quantidade for i in itens})
        return itens

    def subtotal_centavos(self):
        return sum(i.subtotal_centavos for i in self.itens())

    def total_itens(self):
        return sum(self._dados().values())

    def vazio(self):
        return not self._dados()
