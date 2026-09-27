from pydantic import BaseModel
from typing import List
from model.weapon import Weapon


class WeaponViewSchema(BaseModel):
    """ Define como uma arma do catálogo será retornada.
    """
    id: int = 1
    name: str = "Pulse Rifle"


class WeaponListSchema(BaseModel):
    """ Define como uma listagem do catálogo de armas será retornada.
    """
    weapons:List[WeaponViewSchema]


def present_weapons(weapons: List[Weapon]):
    """ Retorna uma representação do catálogo de armas seguindo o schema
        definido em WeaponListSchema.
    """
    return {"weapons": [{"id": w.id, "name": w.name} for w in weapons]}
