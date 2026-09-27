from pydantic import BaseModel


class WeaponUsageSchema(BaseModel):
    """ Define como um novo uso de arma a ser inserido deve ser representado.

        Associa uma arma do catálogo (weapon_id) a uma partida (match_id) com as
        estatísticas daquele uso.
    """
    match_id: int = 1
    weapon_id: int = 1
    shots_fired: int = 80
    accuracy: float = 0.62
    reloads: int = 4


class WeaponUsageViewSchema(BaseModel):
    """ Define como um uso de arma associado a uma partida será retornado.
    """
    weapon_id: int = 1
    name: str = "Pulse Rifle"
    shots_fired: int = 80
    accuracy: float = 0.62
    reloads: int = 4
