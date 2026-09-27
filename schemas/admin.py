from pydantic import BaseModel


class ClearMatchesSchema(BaseModel):
    """ Resultado da limpeza de todas as partidas.
    """
    message: str
    deleted_matches: int
    deleted_usages: int


class ClearWeaponsSchema(BaseModel):
    """ Resultado da limpeza do catálogo de armas e dos usos de arma.
    """
    message: str
    deleted_weapons: int
    deleted_usages: int
