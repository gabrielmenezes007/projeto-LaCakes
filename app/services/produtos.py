"""Cadastro, edição e estoque de produtos pela área administrativa (RN14)."""
import pathlib
import uuid

from flask import current_app

from app.excecoes import ErroValidacao
from app.extensions import db
from app.models import Categoria, Produto
from app.models.produto import ESTOQUE_MAXIMO, PRECO_MAXIMO, PRECO_MINIMO
from app.utils import formatar_moeda, para_inteiro, reais_para_centavos

EXTENSOES_IMAGEM = {".png", ".jpg", ".jpeg", ".webp"}


def produtos_da_vitrine(categoria_id=None):
    consulta = db.select(Produto).where(Produto.ativo.is_(True))
    if categoria_id:
        consulta = consulta.where(Produto.categoria_id == categoria_id)
    # disponíveis primeiro, depois esgotados; dentro de cada grupo, por nome
    produtos = db.session.scalars(consulta.order_by(Produto.nome)).all()
    return sorted(produtos, key=lambda p: not p.disponivel)


def categorias():
    return db.session.scalars(db.select(Categoria).order_by(Categoria.id)).all()


def validar_estoque(texto):
    valor = para_inteiro(texto)
    if valor is None or not 0 <= valor <= ESTOQUE_MAXIMO:
        return None, f"O estoque deve ser um número de 0 a {ESTOQUE_MAXIMO}."
    return valor, None


def salvar_imagem(arquivo):
    """Grava a foto enviada em static/uploads e devolve o caminho relativo a /static."""
    if not arquivo or not arquivo.filename:
        return None
    extensao = pathlib.Path(arquivo.filename).suffix.lower()
    if extensao not in EXTENSOES_IMAGEM:
        raise ErroValidacao({"imagem": "Envie uma imagem JPG, PNG ou WEBP."})
    pasta = pathlib.Path(current_app.config["PASTA_UPLOADS"])
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"{uuid.uuid4().hex}{extensao}"
    arquivo.save(pasta / nome)
    return f"uploads/{nome}"


def salvar_produto(dados, arquivo_imagem=None, produto=None):
    """Valida os dados do formulário e cria ou atualiza o produto (US20/US21)."""
    erros = {}
    nome = (dados.get("nome") or "").strip()
    if len(nome) < 3:
        erros["nome"] = "Informe o nome do cupcake."
    else:
        existente = db.session.scalar(db.select(Produto).where(db.func.lower(Produto.nome) == nome.lower()))
        if existente and (produto is None or existente.id != produto.id):
            erros["nome"] = "Já existe um cupcake com este nome."
    categoria = db.session.get(Categoria, para_inteiro(dados.get("categoria_id"), 0))
    if categoria is None:
        erros["categoria_id"] = "Escolha uma categoria."
    preco = reais_para_centavos(dados.get("preco"))
    if preco is None or not PRECO_MINIMO <= preco <= PRECO_MAXIMO:
        erros["preco"] = (f"O preço deve ficar entre {formatar_moeda(PRECO_MINIMO)} "
                          f"e {formatar_moeda(PRECO_MAXIMO)}.")
    estoque, erro_estoque = validar_estoque(dados.get("estoque"))
    if erro_estoque:
        erros["estoque"] = erro_estoque
    if erros:
        raise ErroValidacao(erros)

    imagem = salvar_imagem(arquivo_imagem)
    novo = produto is None
    if novo:
        produto = Produto()
        db.session.add(produto)
    produto.nome = nome
    produto.categoria = categoria
    produto.descricao = (dados.get("descricao") or "").strip() or None
    produto.ingredientes = (dados.get("ingredientes") or "").strip() or None
    produto.alergenicos = (dados.get("alergenicos") or "").strip() or None
    produto.preco_centavos = preco
    produto.estoque = estoque
    produto.ativo = dados.get("ativo") in ("on", "1", "true", True)
    if imagem:
        produto.imagem = imagem
    db.session.commit()
    return produto


def atualizar_estoques(valores):
    """US22: recebe {produto_id: texto} e grava todos de uma vez. Se algum for inválido, não grava nenhum."""
    erros, novos = {}, {}
    for pid, texto in valores.items():
        produto = db.session.get(Produto, pid)
        if produto is None:
            continue
        valor, erro = validar_estoque(texto)
        if erro:
            erros[f"estoque_{pid}"] = f"{produto.nome}: {erro}"
        else:
            novos[produto] = valor
    if erros:
        raise ErroValidacao(erros, "Alguns estoques estão inválidos. Nada foi salvo.")
    for produto, valor in novos.items():
        produto.estoque = valor
    db.session.commit()
    return len(novos)
