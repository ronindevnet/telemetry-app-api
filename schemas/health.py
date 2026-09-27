from pydantic import BaseModel


class HealthSchema(BaseModel):
    """ Resposta simples usada para verificar se a API está no ar.
    """
    status: str = "ok"
