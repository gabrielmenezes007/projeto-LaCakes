import enum

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager
from app.models.base import agora, coluna_enum


class Perfil(enum.Enum):
    CLIENTE = "CLIENTE"
    ADMIN = "ADMIN"


class Usuario(UserMixin, db.Model):
    """Pessoa cadastrada: cliente ou administrador da loja."""

    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True, comment="Identificador do usuário")
    nome = db.Column(db.String(80), nullable=False, comment="Nome completo do usuário")
    email = db.Column(db.String(120), nullable=False, unique=True, index=True,
                      comment="E-mail de login, único por conta (RN01)")
    senha_hash = db.Column(db.String(255), nullable=False, comment="Hash da senha; a senha nunca é gravada (RNF02)")
    telefone = db.Column(db.String(20), nullable=False, comment="Telefone/WhatsApp para contato sobre o pedido")
    perfil = db.Column(coluna_enum(Perfil, "ck_usuario_perfil"), nullable=False, default=Perfil.CLIENTE,
                       comment="CLIENTE ou ADMIN (RN13)")
    criado_em = db.Column(db.DateTime, nullable=False, default=agora, comment="Data e hora do cadastro")

    pedidos = db.relationship("Pedido", back_populates="usuario", order_by="Pedido.criado_em.desc()")

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def eh_admin(self):
        return self.perfil == Perfil.ADMIN

    @property
    def iniciais(self):
        partes = self.nome.split()
        if not partes:
            return "?"
        letras = partes[0][0] + (partes[-1][0] if len(partes) > 1 else "")
        return letras.upper()

    @property
    def primeiro_nome(self):
        return self.nome.split()[0] if self.nome else ""

    def __repr__(self):
        return f"<Usuario {self.email}>"


@login_manager.user_loader
def carregar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))
