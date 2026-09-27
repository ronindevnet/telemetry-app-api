from sqlalchemy import Column, String, Integer

from  model import Base


class Weapon(Base):
    """ Catálogo de armas.

    As armas são cadastradas sob demanda pelo POST /session: quando a Unity
    envia uma arma que ainda não existe, ela é adicionada aqui. Os nomes
    cadastrados são os mesmos utilizados pela Unity durante o jogo.
    """
    __tablename__ = 'weapons'

    id = Column("pk_weapon", Integer, primary_key=True)
    name = Column(String(140), unique=True)

    def __init__(self, name:str):
        """
        Cria uma Arma no catálogo

        Arguments:
            name: nome da arma (o mesmo utilizado pela Unity).
        """
        self.name = name
