"""Cadastro e autenticação de usuários (RN01)."""
import re

from app.excecoes import ErroValidacao
from app.extensions import db
from app.models import Perfil, Usuario

REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def senha_forte(senha):
    """RN01: mínimo de 8 caracteres, com pelo menos uma letra e um número."""
    return (len(senha or "") >= 8 and re.search(r"[A-Za-zÀ-ÿ]", senha) is not None
            and re.search(r"\d", senha) is not None)


def normalizar_email(email):
    return (email or "").strip().lower()


def buscar_por_email(email):
    return db.session.scalar(db.select(Usuario).where(Usuario.email == normalizar_email(email)))


def cadastrar_cliente(nome, email, telefone, senha, confirmacao):
    erros = {}
    nome = (nome or "").strip()
    email = normalizar_email(email)
    telefone = (telefone or "").strip()
    if len(nome) < 3:
        erros["nome"] = "Informe seu nome completo."
    if not REGEX_EMAIL.match(email):
        erros["email"] = "Informe um e-mail válido."
    elif buscar_por_email(email):
        erros["email"] = "Este e-mail já possui conta. Faça login."
    if len(re.sub(r"\D", "", telefone)) < 10:
        erros["telefone"] = "Informe o telefone com DDD."
    if not senha_forte(senha):
        erros["senha"] = "A senha precisa ter pelo menos 8 caracteres, com letras e números."
    if senha != confirmacao:
        erros["confirmacao"] = "As senhas não conferem."
    if erros:
        raise ErroValidacao(erros)
    usuario = Usuario(nome=nome, email=email, telefone=telefone, perfil=Perfil.CLIENTE)
    usuario.definir_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def autenticar(email, senha):
    """Retorna o usuário se e-mail e senha conferem; senão None (sem dizer qual dos dois errou)."""
    usuario = buscar_por_email(email)
    if usuario and usuario.verificar_senha(senha or ""):
        return usuario
    return None
