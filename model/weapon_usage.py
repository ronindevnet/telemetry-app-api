from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base


class WeaponUsage(Base):
    """ Uso de uma arma em uma partida.

    Tabela de junção entre 'matches' e 'weapons': cada linha representa como uma
    determinada arma (do catálogo) foi usada em uma determinada partida. A chave
    primária é composta por (match_id, weapon_id), então uma arma aparece no
    máximo uma vez por partida.
    """
    __tablename__ = 'weapon_usages'

    match_id = Column(Integer, ForeignKey("matches.pk_match"), primary_key=True)
    weapon_id = Column(Integer, ForeignKey("weapons.pk_weapon"), primary_key=True)
    shots_fired = Column(Integer)
    accuracy = Column(Float)
    reloads = Column(Integer)
    insertion_date = Column(DateTime, default=datetime.now)

    # relacionamento com o catálogo, usado pra recuperar o nome da arma
    weapon = relationship("Weapon")

    def __init__(self, weapon_id:int, shots_fired:int, accuracy:float,
                 reloads:int, insertion_date:Union[DateTime, None] = None):
        """
        Cria um registro de uso de arma em uma partida

        Arguments:
            weapon_id: id da arma (do catálogo) utilizada.
            shots_fired: quantidade de tiros disparados com a arma.
            accuracy: precisão (taxa de acerto entre 0 e 1) com a arma.
            reloads: quantidade de recargas realizadas com a arma.
            insertion_date: data de quando o registro foi inserido à base
        """
        self.weapon_id = weapon_id
        self.shots_fired = shots_fired
        self.accuracy = accuracy
        self.reloads = reloads
        if insertion_date:
            self.insertion_date = insertion_date
