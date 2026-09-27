from pydantic import BaseModel, Field, field_validator
from typing import List


class SessionWeaponSchema(BaseModel):
    """ Uso de uma arma dentro do payload de sessão enviado pela Unity.

        A arma é identificada pelo nome (o mesmo usado no jogo). Se não existir
        no catálogo, é adicionada automaticamente.
    """
    weapon: str = Field("Rifle", min_length=1)
    shots_fired: int = Field(80, ge=0)
    accuracy: float = Field(0.62, ge=0, le=1)
    reloads: int = Field(4, ge=0)

    @field_validator("weapon")
    @classmethod
    def strip_weapon(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("o nome da arma não pode ser vazio")
        return value


class SessionSchema(BaseModel):
    """ Payload completo de uma sessão de jogo (partida + armas utilizadas),
        enviado pela Unity em uma única requisição ao final da gameplay.
    """
    player: str = Field("ana", min_length=1)
    duration: int = Field(1110, ge=0)      # duração total em segundos
    money_spent: int = Field(13, ge=0)     # valor gasto em reais inteiros
    weapons: List[SessionWeaponSchema] = []

    @field_validator("player")
    @classmethod
    def strip_player(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("o nome do jogador não pode ser vazio")
        return value

    @field_validator("weapons")
    @classmethod
    def no_duplicate_weapons(cls, weapons: List[SessionWeaponSchema]) -> List[SessionWeaponSchema]:
        seen = set()
        for weapon in weapons:
            key = weapon.weapon.lower()
            if key in seen:
                raise ValueError("cada arma pode aparecer apenas uma vez na sessão")
            seen.add(key)
        return weapons
