import enum

from app.extensions import db
from app.models.base import agora, coluna_enum


class MetodoPagamento(enum.Enum):
    CREDITO = "CREDITO"
    DEBITO = "DEBITO"
    PIX = "PIX"

    @property
    def rotulo(self):
        return {"CREDITO": "Cartão de crédito", "DEBITO": "Cartão de débito", "PIX": "Pix"}[self.value]

    @property
    def usa_cartao(self):
        return self in (MetodoPagamento.CREDITO, MetodoPagamento.DEBITO)


class StatusPagamento(enum.Enum):
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"
    ESTORNADO = "ESTORNADO"


class Pagamento(db.Model):
    """Tentativa de pagamento de um pedido (simulado). Guarda só os 4 últimos dígitos do cartão (RNF09)."""

    __tablename__ = "pagamento"
    __table_args__ = (db.CheckConstraint("valor_centavos > 0", name="ck_pagamento_valor"),)

    id = db.Column(db.Integer, primary_key=True, comment="Identificador da tentativa de pagamento")
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False, index=True,
                          comment="Pedido pago (FK pedido.id)")
    metodo = db.Column(coluna_enum(MetodoPagamento, "ck_pagamento_metodo"), nullable=False,
                       comment="CREDITO, DEBITO ou PIX")
    status = db.Column(coluna_enum(StatusPagamento, "ck_pagamento_status"), nullable=False,
                       comment="APROVADO, RECUSADO ou ESTORNADO")
    valor_centavos = db.Column(db.Integer, nullable=False, comment="Valor cobrado, em centavos")
    cartao_final = db.Column(db.String(4), nullable=True, comment="4 últimos dígitos do cartão (vazio no Pix)")
    codigo_transacao = db.Column(db.String(40), nullable=True, comment="Código devolvido pelo serviço simulado")
    criado_em = db.Column(db.DateTime, nullable=False, default=agora, comment="Momento da tentativa")

    pedido = db.relationship("Pedido", back_populates="pagamentos")

    @property
    def descricao(self):
        if self.metodo.usa_cartao and self.cartao_final:
            return f"{self.metodo.rotulo} •••• {self.cartao_final}"
        return self.metodo.rotulo
