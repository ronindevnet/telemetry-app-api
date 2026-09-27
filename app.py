from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from model import Session, Match, Weapon, WeaponUsage
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="API de Telemetria", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)


@app.teardown_appcontext
def remove_session(exception=None):
    """Libera a sessão do banco ao final de cada requisição (evita vazamento de conexões)."""
    Session.remove()

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
match_tag = Tag(name="Match", description="Adição, visualização e remoção de partidas à base")
weapon_tag = Tag(name="Weapon", description="Leitura e limpeza do catálogo de armas (as armas são cadastradas pelo POST /session)")
usage_tag = Tag(name="Usage", description="Adição de um uso de arma à uma partida cadastrada na base")
session_tag = Tag(name="Session", description="Registro de uma sessão completa (partida + armas) em uma única requisição JSON — usado pelo cliente Unity")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.get('/health', tags=[home_tag], responses={"200": HealthSchema})
def health():
    """Verifica se a API está disponível.

    Usado pelo front-end para detectar o estado 'servidor offline'.
    """
    return {"status": "ok"}


@app.post('/match', tags=[match_tag],
          responses={"200": MatchViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_match(form: MatchSchema):
    """Adiciona uma nova Partida à base de dados

    Retorna uma representação das partidas e armas associadas.
    """
    match = Match(
        player=form.player,
        duration=form.duration,
        money_spent=form.money_spent)
    logger.debug(f"Adicionando partida do jogador: '{match.player}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando partida
        session.add(match)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionada partida do jogador: '{match.player}'")
        return present_match(match), 200

    except IntegrityError as e:
        # como problema de integridade referencial é a provável razão do IntegrityError
        error_msg = "Partida com dados inconsistentes :/"
        logger.warning(f"Erro ao adicionar partida do jogador '{match.player}', {error_msg}")
        return {"message": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar nova partida :/"
        logger.warning(f"Erro ao adicionar partida do jogador '{match.player}', {error_msg}")
        return {"message": error_msg}, 400


@app.get('/matches', tags=[match_tag],
         responses={"200": MatchListSchema})
def get_matches():
    """Faz a busca por todas as Partidas cadastradas

    Retorna uma representação da listagem de partidas (lista vazia se não houver nenhuma).
    """
    logger.debug(f"Coletando partidas ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    matches = session.query(Match).all()

    if not matches:
        # se não há partidas cadastradas
        return {"matches": []}, 200
    else:
        logger.debug(f"%d partidas encontradas" % len(matches))
        # retorna a representação de partida
        return present_matches(matches), 200


@app.get('/match', tags=[match_tag],
         responses={"200": MatchViewSchema, "404": ErrorSchema})
def get_match(query: MatchSearchSchema):
    """Faz a busca por uma Partida a partir do id da partida

    Retorna uma representação das partidas e armas associadas.
    """
    match_id = query.id
    logger.debug(f"Coletando dados sobre partida #{match_id}")
    # criando conexao com a base
    session = Session()
    # fazendo a busca
    match = session.query(Match).filter(Match.id == match_id).first()

    if not match:
        # se a partida não foi encontrada
        error_msg = "Partida não encontrada na base :/"
        logger.warning(f"Erro ao buscar partida '{match_id}', {error_msg}")
        return {"message": error_msg}, 404
    else:
        logger.debug(f"Partida encontrada: '{match.id}'")
        # retorna a representação de partida
        return present_match(match), 200


@app.delete('/match', tags=[match_tag],
            responses={"200": MatchDelSchema, "404": ErrorSchema})
def del_match(query: MatchSearchSchema):
    """Deleta uma Partida a partir do id de partida informado

    Retorna uma mensagem de confirmação da remoção.
    """
    match_id = query.id
    logger.debug(f"Deletando dados sobre partida #{match_id}")
    # criando conexão com a base
    session = Session()
    # removendo os usos de arma associados à partida
    session.query(WeaponUsage).filter(WeaponUsage.match_id == match_id).delete()
    # fazendo a remoção
    count = session.query(Match).filter(Match.id == match_id).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletada partida #{match_id}")
        return {"message": "Partida removida", "id": match_id}
    else:
        # se a partida não foi encontrada
        error_msg = "Partida não encontrada na base :/"
        logger.warning(f"Erro ao deletar partida #'{match_id}', {error_msg}")
        return {"message": error_msg}, 404


@app.delete('/matches', tags=[match_tag],
            responses={"200": ClearMatchesSchema})
def clear_matches():
    """Remove todas as partidas (e todos os usos de arma associados a elas)

    Retorna a quantidade de partidas e de usos de arma removidos.
    """
    logger.debug("Removendo todas as partidas")
    # criando conexão com a base
    session = Session()
    # remove primeiro os usos de arma (dependem das partidas)
    deleted_usages = session.query(WeaponUsage).delete()
    deleted_matches = session.query(Match).delete()
    session.commit()
    logger.debug(f"Removidas {deleted_matches} partidas e {deleted_usages} usos de arma")
    return {
        "message": "Partidas removidas",
        "deleted_matches": deleted_matches,
        "deleted_usages": deleted_usages,
    }


@app.get('/weapons', tags=[weapon_tag],
         responses={"200": WeaponListSchema})
def get_weapons():
    """Faz a busca por todas as armas do catálogo

    Retorna uma representação da listagem do catálogo de armas.
    """
    logger.debug(f"Coletando catálogo de armas ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    weapons = session.query(Weapon).order_by(Weapon.id).all()
    logger.debug(f"%d armas encontradas" % len(weapons))
    # retorna a representação do catálogo de armas
    return present_weapons(weapons), 200


@app.delete('/weapons', tags=[weapon_tag],
            responses={"200": ClearWeaponsSchema})
def clear_weapons():
    """Limpa o catálogo de armas e remove todos os usos de arma das partidas

    As partidas são mantidas, mas ficam sem armas registradas.
    Retorna a quantidade de armas e de usos de arma removidos.
    """
    logger.debug("Limpando catálogo de armas e usos de arma")
    # criando conexão com a base
    session = Session()
    # remove primeiro os usos de arma (dependem do catalogo)
    deleted_usages = session.query(WeaponUsage).delete()
    deleted_weapons = session.query(Weapon).delete()
    session.commit()
    logger.debug(f"Removidas {deleted_weapons} armas e {deleted_usages} usos de arma")
    return {
        "message": "Catálogo de armas e usos de arma removidos",
        "deleted_weapons": deleted_weapons,
        "deleted_usages": deleted_usages,
    }


@app.post('/usage', tags=[usage_tag],
          responses={"200": MatchViewSchema, "404": ErrorSchema, "409": ErrorSchema})
def add_usage(form: WeaponUsageSchema):
    """Adiciona um novo uso de arma à uma partida cadastrada na base

    Associa uma arma do catálogo à partida com as estatísticas daquele uso.
    Retorna uma representação das partidas e armas associadas.
    """
    match_id = form.match_id
    weapon_id = form.weapon_id
    logger.debug(f"Adicionando uso de arma #{weapon_id} à partida #{match_id}")
    # criando conexão com a base
    session = Session()

    # fazendo a busca pela partida
    match = session.query(Match).filter(Match.id == match_id).first()
    if not match:
        # se partida não encontrada
        error_msg = "Partida não encontrada na base :/"
        logger.warning(f"Erro ao adicionar uso de arma à partida '{match_id}', {error_msg}")
        return {"message": error_msg}, 404

    # fazendo a busca pela arma no catálogo
    weapon = session.query(Weapon).filter(Weapon.id == weapon_id).first()
    if not weapon:
        # se arma não encontrada no catálogo
        error_msg = "Arma não encontrada no catálogo :/"
        logger.warning(f"Erro ao adicionar uso de arma '{weapon_id}', {error_msg}")
        return {"message": error_msg}, 404

    # verifica se essa arma já foi registrada nesta partida
    ja_registrada = session.query(WeaponUsage).filter(
        WeaponUsage.match_id == match_id,
        WeaponUsage.weapon_id == weapon_id).first()
    if ja_registrada:
        error_msg = "Esta arma já foi adicionada a esta partida :/"
        logger.warning(f"Erro ao adicionar uso de arma '{weapon_id}' à partida '{match_id}', {error_msg}")
        return {"message": error_msg}, 409

    # criando o uso de arma
    usage = WeaponUsage(
        weapon_id=weapon_id,
        shots_fired=form.shots_fired,
        accuracy=form.accuracy,
        reloads=form.reloads)

    # adicionando o uso de arma à partida
    match.add_usage(usage)
    try:
        session.commit()
    except IntegrityError as e:
        # a arma já foi registrada nesta partida (chave primária composta duplicada)
        session.rollback()
        error_msg = "Esta arma já foi adicionada a esta partida :/"
        logger.warning(f"Erro ao adicionar uso de arma '{weapon_id}' à partida '{match_id}', {error_msg}")
        return {"message": error_msg}, 409

    logger.debug(f"Adicionado uso de arma #{weapon_id} à partida #{match_id}")

    # retorna a representação de partida
    return present_match(match), 200


@app.post('/session', tags=[session_tag],
          responses={"201": MatchViewSchema, "422": ErrorSchema, "400": ErrorSchema})
def add_session(body: SessionSchema):
    """Registra uma sessão de jogo completa em uma única requisição (JSON)

    Voltado ao cliente Unity: cria a partida e todos os usos de arma de forma
    atômica (tudo ou nada). Armas que ainda não existem no catálogo são
    adicionadas automaticamente (add weapon by demand). As armas são
    identificadas pelo nome. Retorna a representação da partida criada.
    """
    logger.debug(f"Registrando sessão do jogador '{body.player}' com {len(body.weapons)} arma(s)")
    # criando conexão com a base
    session = Session()
    try:
        # cria a partida
        match = Match(
            player=body.player,
            duration=body.duration,
            money_spent=body.money_spent)
        session.add(match)

        # cria os usos de arma, resolvendo (ou criando) cada arma no catálogo
        for item in body.weapons:
            weapon = session.query(Weapon).filter(
                func.lower(Weapon.name) == item.weapon.lower()).first()
            if not weapon:
                # add weapon by demand: arma inexistente é cadastrada no catálogo
                weapon = Weapon(name=item.weapon)
                session.add(weapon)
                session.flush()  # garante o id da arma recém-criada
                logger.debug(f"Arma '{item.weapon}' adicionada ao catálogo sob demanda")
            usage = WeaponUsage(
                weapon_id=weapon.id,
                shots_fired=item.shots_fired,
                accuracy=item.accuracy,
                reloads=item.reloads)
            match.add_usage(usage)

        session.commit()

    except IntegrityError as e:
        # qualquer violação de integridade desfaz a sessão inteira
        session.rollback()
        error_msg = "Não foi possível salvar a sessão :/"
        logger.warning(f"Erro ao registrar sessão do jogador '{body.player}', {error_msg}")
        return {"message": error_msg}, 400

    logger.debug(f"Sessão registrada para o jogador '{body.player}' (partida #{match.id})")
    # retorna a representação da partida criada
    return present_match(match), 201


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
