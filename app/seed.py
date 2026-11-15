"""Dados iniciais: categorias, cardápio de exemplo e contas de teste.

Uso:
    python -m app.seed             cria as tabelas e os dados, se o banco estiver vazio
    python -m app.seed --recriar   apaga tudo e cria de novo (volta ao estado inicial)

Contas de teste (ambiente de demonstração):
    Administradora: admin@lacakes.test   / Admin@2026
    Cliente:        cliente@lacakes.test / Cliente@2026
"""
import sys

from app.extensions import db
from app.models import Categoria, Perfil, Produto, Usuario

CONTAS = [
    {"nome": "Laysa", "email": "admin@lacakes.test", "senha": "Admin@2026", "telefone": "(14) 99999-0001",
     "perfil": Perfil.ADMIN},
    {"nome": "Ana Souza", "email": "cliente@lacakes.test", "senha": "Cliente@2026", "telefone": "(14) 99999-0002",
     "perfil": Perfil.CLIENTE},
]

CATEGORIAS = [
    ("Clássicos", "Os sabores tradicionais da casa."),
    ("Recheados", "Cupcakes com recheio cremoso."),
    ("Zero açúcar", "Opções sem adição de açúcar."),
    ("Datas especiais", "Sabores sazonais (Páscoa, festa junina, Natal)."),
]

# nome, categoria, preço (centavos), estoque, ativo, imagem, descrição, ingredientes, alergênicos
PRODUTOS = [
    ("Red Velvet Clássico", "Clássicos", 990, 18, True, "red-velvet",
     "Massa aveludada de cacau com cobertura de cream cheese e migalhas de red velvet.",
     "Farinha de trigo, açúcar, ovos, manteiga, leitelho, cacau, cream cheese, corante alimentício.",
     "Glúten, leite e ovos."),
    ("Ninho com Nutella", "Recheados", 1290, 24, True, "ninho-nutella",
     "Massa de baunilha recheada com Nutella e cobertura de creme de leite Ninho.",
     "Farinha de trigo, açúcar, ovos, manteiga, leite em pó, creme de avelã com cacau, creme de leite.",
     "Glúten, leite, ovos e avelã. Pode conter traços de soja."),
    ("Limão Siciliano", "Clássicos", 950, 4, True, "limao-siciliano",
     "Massa leve de limão siciliano com cobertura de merengue suíço maçaricado e raspas de limão.",
     "Farinha de trigo, açúcar, ovos, manteiga, leite, suco e raspas de limão siciliano, claras.",
     "Glúten, leite e ovos. Pode conter traços de castanhas."),
    ("Cenoura com Brigadeiro", "Recheados", 1150, 15, True, "cenoura-brigadeiro",
     "Massa fofinha de cenoura com recheio e cobertura de brigadeiro e granulado.",
     "Farinha de trigo, cenoura, açúcar, ovos, óleo, leite condensado, cacau, manteiga, granulado.",
     "Glúten, leite e ovos."),
    ("Chocolate 70% Zero Açúcar", "Zero açúcar", 1390, 12, True, "chocolate-70",
     "Massa de chocolate 70% adoçada com eritritol e ganache intensa.",
     "Farinha de trigo, chocolate 70% sem açúcar, eritritol, ovos, manteiga, creme de leite.",
     "Glúten, leite e ovos."),
    ("Morango com Chantilly", "Clássicos", 1090, 0, True, "morango-chantilly",
     "Massa de baunilha com chantilly fresco e morango inteiro.",
     "Farinha de trigo, açúcar, ovos, manteiga, leite, creme de leite fresco, morangos.",
     "Glúten, leite e ovos."),
    ("Pistache com Frutas Vermelhas", "Recheados", 1490, 10, True, "pistache-frutas-vermelhas",
     "Massa de pistache com recheio de geleia de frutas vermelhas.",
     "Farinha de trigo, pistache, açúcar, ovos, manteiga, frutas vermelhas.",
     "Glúten, leite, ovos e castanhas (pistache)."),
    ("Panetone Trufado", "Datas especiais", 1590, 0, False, "panetone-trufado",
     "Edição de Natal: massa de panetone com frutas cristalizadas e trufa de chocolate.",
     "Farinha de trigo, frutas cristalizadas, uvas-passas, chocolate, açúcar, ovos, manteiga.",
     "Glúten, leite e ovos."),
]


def popular(recriar=False):
    if recriar:
        db.drop_all()
    db.create_all()
    if db.session.scalar(db.select(db.func.count(Usuario.id))):
        return "O banco já tem dados; nada foi alterado. Use --recriar para voltar ao estado inicial."

    for dados in CONTAS:
        usuario = Usuario(nome=dados["nome"], email=dados["email"], telefone=dados["telefone"], perfil=dados["perfil"])
        usuario.definir_senha(dados["senha"])
        db.session.add(usuario)
    categorias = {}
    for nome, descricao in CATEGORIAS:
        categorias[nome] = Categoria(nome=nome, descricao=descricao)
        db.session.add(categorias[nome])
    for nome, cat, preco, estoque, ativo, img, descricao, ingredientes, alergenicos in PRODUTOS:
        db.session.add(Produto(nome=nome, categoria=categorias[cat], preco_centavos=preco, estoque=estoque, ativo=ativo,
                               imagem=f"img/cupcakes/{img}.svg", descricao=descricao, ingredientes=ingredientes,
                               alergenicos=alergenicos))
    db.session.commit()
    return (f"Banco criado com {len(CATEGORIAS)} categorias, {len(PRODUTOS)} cupcakes e {len(CONTAS)} contas de teste.")


if __name__ == "__main__":
    from app import create_app

    with create_app().app_context():
        print(popular(recriar="--recriar" in sys.argv))
