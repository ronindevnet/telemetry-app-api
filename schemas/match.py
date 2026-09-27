from pydantic import BaseModel
from typing import List, Optional
from model.match import Match

from schemas.weapon_usage import WeaponUsageViewSchema


class MatchSchema(BaseModel):
    """ Define como uma nova partida a ser inserida deve ser representada.
        duration em segundos (inteiro); money_spent em reais inteiros.
    """
    player: str = "john doe"
    duration: int = 1110
    money_spent: int = 13


class MatchSearchSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. Que será
        feita apenas com base no id da partida.
    """
    id: int = 1


class MatchListItemSchema(BaseModel):
    """ Define como cada partida aparece na listagem de partidas.
    """
    id: int = 1
    player: str = "john doe"
    duration: int = 1110
    money_spent: int = 13
    total_weapons: int = 1
    insertion_date: Optional[str] = "2026-09-27T14:03:12"


class MatchListSchema(BaseModel):
    """ Define como uma listagem de partidas será retornada.
    """
    matches:List[MatchListItemSchema]


def format_date(date):
    """ Converte a data de inserção para texto ISO 8601 (sem microssegundos),
        formato que o front-end consegue ler e exibir no fuso local.
    """
    if not date:
        return None
    return date.replace(microsecond=0).isoformat()


def present_matches(matches: List[Match]):
    """ Retorna uma representação da listagem de partidas seguindo o schema
        definido em MatchListSchema.
    """
    result = []
    for match in matches:
        result.append({
            "id": match.id,
            "player": match.player,
            "duration": match.duration,
            "money_spent": match.money_spent,
            "total_weapons": len(match.usages),
            "insertion_date": format_date(match.insertion_date),
        })

    return {"matches": result}


class MatchViewSchema(BaseModel):
    """ Define como uma partida será retornada: partida + armas utilizadas.
    """
    id: int = 1
    player: str = "john doe"
    duration: int = 1110
    money_spent: int = 13
    total_weapons: int = 1
    insertion_date: Optional[str] = "2026-09-27T14:03:12"
    weapons:List[WeaponUsageViewSchema]


class MatchDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    message: str
    id: int


def present_match(match: Match):
    """ Retorna uma representação da partida seguindo o schema definido em
        MatchViewSchema.
    """
    return {
        "id": match.id,
        "player": match.player,
        "duration": match.duration,
        "money_spent": match.money_spent,
        "total_weapons": len(match.usages),
        "insertion_date": format_date(match.insertion_date),
        "weapons": [{
            "weapon_id": u.weapon_id,
            "name": u.weapon.name,
            "shots_fired": u.shots_fired,
            "accuracy": u.accuracy,
            "reloads": u.reloads,
        } for u in match.usages]
    }
