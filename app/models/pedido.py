import enum

from app.excecoes import TransicaoInvalida
from app.extensions import db
from app.models.base import agora, coluna_enum


class StatusPedido(enum.Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGO = "PAGO"
    EM_PREPARO = "EM_PREPARO"
    SAIU_PARA_ENTREGA = "SAIU_PARA_ENTREGA"
    PRONTO_PARA_RETIRADA = "PRONTO_PARA_RETIRADA"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

    @property
    def rotulo(self):
        return {
            "AGUARDANDO_PAGAMENTO": "Aguardando pagamento", "PAGO": "Pago", "EM_PREPARO": "Em preparo",
            "SAIU_PARA_ENTREGA": "Saiu para entrega", "PRONTO_PARA_RETIRADA": "Pronto para retirada",
            "ENTREGUE": "Entregue", "CANCELADO": "Cancelado",
        }[self.value]

    @property
    def classe_css(self):
        return {
            "AGUARDANDO_PAGAMENTO": "s-ag", "PAGO": "s-pago", "EM_PREPARO": "s-prep", "SAIU_PARA_ENTREGA": "s-saiu",
            "PRONTO_PARA_RETIRADA": "s-saiu", "ENTREGUE": "s-ent", "CANCELADO": "s-canc",
        }[self.value]


class Modalidade(enum.Enum):
    ENTREGA = "ENTREGA"
    RETIRADA = "RETIRADA"

    @property
    def rotulo(self):
        return "Entrega" if self is Modalidade.ENTREGA else "Retirada na loja"


class Pedido(db.Model):
    """Pedido feito por um cliente. O endereço fica gravado no próprio pedido (foto do momento da compra)."""

    __tablename__ = "pedido"
    __table_args__ = (
        db.CheckConstraint("subtotal_centavos >= 0", name="ck_pedido_subtotal"),
        db.CheckConstraint("taxa_entrega_centavos >= 0", name="ck_pedido_taxa"),
        db.CheckConstraint("total_centavos = subtotal_centavos + taxa_entrega_centavos", name="ck_pedido_total"),
    )

    id = db.Column(db.Integer, primary_key=True, comment="Número do pedido")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False, index=True,
                           comment="Cliente dono do pedido (FK usuario.id)")
    status = db.Column(coluna_enum(StatusPedido, "ck_pedido_status"), nullable=False,
                       default=StatusPedido.AGUARDANDO_PAGAMENTO, index=True, comment="Situação atual (RN10)")
    modalidade = db.Column(coluna_enum(Modalidade, "ck_pedido_modalidade"), nullable=False,
                           comment="ENTREGA ou RETIRADA")
    cep = db.Column(db.String(8), nullable=True, comment="CEP de entrega, só dígitos (vazio na retirada)")
    logradouro = db.Column(db.String(120), nullable=True, comment="Rua/avenida de entrega")
    numero = db.Column(db.String(10), nullable=True, comment="Número do endereço")
    complemento = db.Column(db.String(60), nullable=True, comment="Complemento (opcional)")
    bairro = db.Column(db.String(60), nullable=True, comment="Bairro de entrega")
    subtotal_centavos = db.Column(db.Integer, nullable=False, comment="Soma dos itens, em centavos")
    taxa_entrega_centavos = db.Column(db.Integer, nullable=False, default=0, comment="Taxa de entrega (RN06)")
    total_centavos = db.Column(db.Integer, nullable=False, comment="Subtotal + taxa de entrega")
    criado_em = db.Column(db.DateTime, nullable=False, default=agora, comment="Data e hora do pedido")
    atualizado_em = db.Column(db.DateTime, nullable=False, default=agora, onupdate=agora,
                              comment="Última alteração")

    usuario = db.relationship("Usuario", back_populates="pedidos")
    itens = db.relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan",
                            order_by="ItemPedido.id")
    pagamentos = db.relationship("Pagamento", back_populates="pedido", cascade="all, delete-orphan",
                                 order_by="Pagamento.id")
    historico = db.relationship("HistoricoStatus", back_populates="pedido", cascade="all, delete-orphan",
                                order_by="HistoricoStatus.id")

    # ----------------------------------------------------------------- regras
    def calcular_totais(self, taxa_entrega):
        self.subtotal_centavos = sum(i.subtotal_centavos for i in self.itens)
        self.taxa_entrega_centavos = taxa_entrega
        self.total_centavos = self.subtotal_centavos + taxa_entrega

    def registrar_status(self, novo_status, observacao=None):
        self.status = novo_status
        self.historico.append(HistoricoStatus(status=novo_status, observacao=observacao))

    def proximo_status(self):
        """RN10: próxima etapa válida, ou None se o pedido não pode avançar pela loja."""
        if self.status == StatusPedido.PAGO:
            return StatusPedido.EM_PREPARO
        if self.status == StatusPedido.EM_PREPARO:
            return (StatusPedido.SAIU_PARA_ENTREGA if self.modalidade == Modalidade.ENTREGA
                    else StatusPedido.PRONTO_PARA_RETIRADA)
        if self.status in (StatusPedido.SAIU_PARA_ENTREGA, StatusPedido.PRONTO_PARA_RETIRADA):
            return StatusPedido.ENTREGUE
        return None

    def avancar_status(self):
        novo = self.proximo_status()
        if novo is None:
            if self.status == StatusPedido.AGUARDANDO_PAGAMENTO:
                raise TransicaoInvalida("Este pedido ainda não foi pago.")
            raise TransicaoInvalida("Este pedido já foi finalizado.")
        self.registrar_status(novo)
        return novo

    @property
    def pode_cancelar(self):
        """RN11: cancelamento pelo cliente só antes de entrar em preparo."""
        return self.status in (StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.PAGO)

    @property
    def etapas(self):
        """Etapas da linha do tempo, de acordo com a modalidade."""
        final = (StatusPedido.SAIU_PARA_ENTREGA if self.modalidade == Modalidade.ENTREGA
                 else StatusPedido.PRONTO_PARA_RETIRADA)
        return [StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.PAGO, StatusPedido.EM_PREPARO, final,
                StatusPedido.ENTREGUE]

    def momento_do_status(self, status):
        for h in self.historico:
            if h.status == status:
                return h.criado_em
        return None

    @property
    def pagamento_aprovado(self):
        from app.models.pagamento import StatusPagamento
        for p in self.pagamentos:
            if p.status in (StatusPagamento.APROVADO, StatusPagamento.ESTORNADO):
                return p
        return None

    @property
    def quantidade_itens(self):
        return sum(i.quantidade for i in self.itens)

    def __repr__(self):
        return f"<Pedido {self.id} {self.status.value}>"


class ItemPedido(db.Model):
    """Cupcake dentro de um pedido. O preço é congelado no momento da compra (RN15)."""

    __tablename__ = "item_pedido"
    __table_args__ = (
        db.CheckConstraint("quantidade BETWEEN 1 AND 24", name="ck_item_quantidade"),
        db.CheckConstraint("preco_unitario_centavos > 0", name="ck_item_preco"),
        db.UniqueConstraint("pedido_id", "produto_id", name="uq_item_pedido_produto"),
    )

    id = db.Column(db.Integer, primary_key=True, comment="Identificador do item")
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False, index=True,
                          comment="Pedido ao qual o item pertence (FK pedido.id)")
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False, index=True,
                           comment="Cupcake comprado (FK produto.id)")
    quantidade = db.Column(db.Integer, nullable=False, comment="Quantidade, de 1 a 24 (RN04)")
    preco_unitario_centavos = db.Column(db.Integer, nullable=False,
                                        comment="Preço unitário congelado na compra (RN15)")

    pedido = db.relationship("Pedido", back_populates="itens")
    produto = db.relationship("Produto")

    @property
    def subtotal_centavos(self):
        return self.quantidade * self.preco_unitario_centavos


class HistoricoStatus(db.Model):
    """Registro de cada mudança de status do pedido (linha do tempo do acompanhamento)."""

    __tablename__ = "historico_status"

    id = db.Column(db.Integer, primary_key=True, comment="Identificador do registro")
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False, index=True,
                          comment="Pedido (FK pedido.id)")
    status = db.Column(coluna_enum(StatusPedido, "ck_historico_status"), nullable=False,
                       comment="Status que o pedido assumiu")
    observacao = db.Column(db.String(200), nullable=True, comment="Observação da mudança")
    criado_em = db.Column(db.DateTime, nullable=False, default=agora, comment="Momento da mudança")

    pedido = db.relationship("Pedido", back_populates="historico")
