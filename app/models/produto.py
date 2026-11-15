from app.excecoes import EstoqueInsuficiente
from app.extensions import db
from app.models.base import agora

PRECO_MINIMO = 100        # R$ 1,00 (RN14)
PRECO_MAXIMO = 20000      # R$ 200,00 (RN14)
ESTOQUE_MAXIMO = 500      # RN14
ULTIMAS_UNIDADES = 5      # aviso "Últimas unidades" (US04)
IMAGEM_PADRAO = "img/cupcakes/padrao.svg"


class Categoria(db.Model):
    """Agrupa os cupcakes na vitrine (Clássicos, Recheados...)."""

    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True, comment="Identificador da categoria")
    nome = db.Column(db.String(40), nullable=False, unique=True, comment="Nome exibido no filtro da vitrine")
    descricao = db.Column(db.String(200), nullable=True, comment="Descrição curta da categoria")

    produtos = db.relationship("Produto", back_populates="categoria", order_by="Produto.nome")

    def __repr__(self):
        return f"<Categoria {self.nome}>"


class Produto(db.Model):
    """Cupcake vendido na loja."""

    __tablename__ = "produto"
    __table_args__ = (
        db.CheckConstraint(f"preco_centavos BETWEEN {PRECO_MINIMO} AND {PRECO_MAXIMO}", name="ck_produto_preco"),
        db.CheckConstraint(f"estoque BETWEEN 0 AND {ESTOQUE_MAXIMO}", name="ck_produto_estoque"),
    )

    id = db.Column(db.Integer, primary_key=True, comment="Identificador do produto")
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False, index=True,
                             comment="Categoria do produto (FK categoria.id)")
    nome = db.Column(db.String(80), nullable=False, unique=True, comment="Nome do cupcake, único (RN14)")
    descricao = db.Column(db.Text, nullable=True, comment="Descrição exibida na página do produto")
    ingredientes = db.Column(db.Text, nullable=True, comment="Lista de ingredientes")
    alergenicos = db.Column(db.String(200), nullable=True, comment="Alergênicos (ex.: glúten, leite, ovos)")
    preco_centavos = db.Column(db.Integer, nullable=False,
                               comment="Preço em centavos, de 100 a 20000 (R$ 1,00 a R$ 200,00)")
    estoque = db.Column(db.Integer, nullable=False, default=0, comment="Unidades disponíveis hoje, de 0 a 500")
    imagem = db.Column(db.String(200), nullable=True,
                       comment="Caminho da imagem dentro de /static; vazio usa a imagem padrão")
    ativo = db.Column(db.Boolean, nullable=False, default=True, comment="Se falso, o produto não aparece na vitrine")
    criado_em = db.Column(db.DateTime, nullable=False, default=agora, comment="Data e hora do cadastro")

    categoria = db.relationship("Categoria", back_populates="produtos")

    @property
    def disponivel(self):
        """RN03: aparece como disponível se está ativo e tem estoque."""
        return self.ativo and self.estoque > 0

    @property
    def ultimas_unidades(self):
        return 0 < self.estoque <= ULTIMAS_UNIDADES

    @property
    def caminho_imagem(self):
        return self.imagem or IMAGEM_PADRAO

    def baixar_estoque(self, quantidade):
        if quantidade > self.estoque:
            raise EstoqueInsuficiente(f"Estoque insuficiente para: {self.nome}")
        self.estoque -= quantidade

    def repor_estoque(self, quantidade):
        self.estoque = min(self.estoque + quantidade, ESTOQUE_MAXIMO)

    def __repr__(self):
        return f"<Produto {self.nome}>"
