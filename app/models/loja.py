from app.extensions import db
from app.models.base import agora

# Índice de cada dia = date.weekday() do Python (0 = segunda ... 6 = domingo)
DIAS_DA_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def formatar_hora(hora):
    """time(9, 0) -> '9h'; time(9, 30) -> '9h30'."""
    return f"{hora.hour}h{hora.minute:02d}" if hora.minute else f"{hora.hour}h"


def descrever_dias(dias):
    """[0..5] -> 'Segunda a sábado'; [5, 6] -> 'Sábado e domingo'; [0, 2, 4] -> 'Segunda, quarta e sexta'."""
    if not dias:
        return "Nenhum dia"
    if len(dias) == 7:
        return "Todos os dias"
    nomes = [DIAS_DA_SEMANA[d] for d in dias]
    if len(dias) >= 3 and dias == list(range(dias[0], dias[-1] + 1)):
        return f"{nomes[0]} a {nomes[-1].lower()}"
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join([nomes[0]] + [n.lower() for n in nomes[1:-1]]) + " e " + nomes[-1].lower()


class Loja(db.Model):
    """Dados da loja cadastrados pela administradora (registro único): endereço, dias e horário de funcionamento."""

    __tablename__ = "loja"
    __table_args__ = (db.CheckConstraint("abre_as < fecha_as", name="ck_loja_horario"),)

    id = db.Column(db.Integer, primary_key=True, comment="Identificador (a loja tem um único registro)")
    endereco = db.Column(db.String(150), nullable=False, comment="Endereço da loja, usado na retirada")
    dias_funcionamento = db.Column(db.String(7), nullable=False,
                                   comment="Dias abertos: dígitos de 0 (segunda) a 6 (domingo), ex.: 012345")
    abre_as = db.Column(db.Time, nullable=False, comment="Horário de abertura")
    fecha_as = db.Column(db.Time, nullable=False, comment="Horário de fechamento (depois da abertura)")
    atualizado_em = db.Column(db.DateTime, nullable=False, default=agora, onupdate=agora, comment="Última alteração")

    @property
    def dias(self):
        return sorted({int(c) for c in self.dias_funcionamento or "" if c in "0123456"})

    @property
    def horario_texto(self):
        return f"{descrever_dias(self.dias)}, das {formatar_hora(self.abre_as)} às {formatar_hora(self.fecha_as)}"

    def __repr__(self):
        return f"<Loja {self.endereco}>"
