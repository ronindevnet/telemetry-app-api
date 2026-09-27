from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base, WeaponUsage


class Match(Base):
    __tablename__ = 'matches'

    id = Column("pk_match", Integer, primary_key=True)
    player = Column(String(140))
    duration = Column(Integer)      # duração total em segundos
    money_spent = Column(Integer)   # valor gasto em reais inteiros
    insertion_date = Column(DateTime, default=datetime.now)

    # Definição do relacionamento entre a partida e os usos de arma.
    # Essa relação é implicita, não está salva na tabela 'matches',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    usages = relationship("WeaponUsage")

    def __init__(self, player:str, duration:int, money_spent:int,
                 insertion_date:Union[DateTime, None] = None):
        """
        Cria uma Partida (Match / sessão de jogo)

        Arguments:
            player: nome do jogador que realizou a partida.
            duration: duração da partida em segundos (inteiro).
            money_spent: valor gasto pelo jogador durante a partida, em reais inteiros.
            insertion_date: data de quando a partida foi inserida à base
        """
        self.player = player
        self.duration = duration
        self.money_spent = money_spent

        # se não for informada, será o data exata da inserção no banco
        if insertion_date:
            self.insertion_date = insertion_date

    def add_usage(self, usage:WeaponUsage):
        """ Adiciona um novo uso de arma à Partida
        """
        self.usages.append(usage)
