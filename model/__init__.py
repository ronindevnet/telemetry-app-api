from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
import os

# importando os elementos definidos no modelo
from model.base import Base
from model.weapon import Weapon
from model.weapon_usage import WeaponUsage
from model.match import Match

db_path = "database/"
# Verifica se o diretorio não existe
if not os.path.exists(db_path):
   # então cria o diretorio
   os.makedirs(db_path)

# url de acesso ao banco (essa é uma url de acesso ao sqlite local)
db_url = 'sqlite:///%s/db.sqlite3' % db_path

# cria a engine de conexão com o banco
engine = create_engine(db_url, echo=False)

# Instancia um criador de seção com o banco.
# Usa scoped_session para que cada requisição tenha sua própria sessão, que é
# liberada de volta ao pool no fim da requisição (ver teardown em app.py). Isso
# evita o vazamento de conexões que ocorreria criando sessões sem fechá-las.
Session = scoped_session(sessionmaker(bind=engine))

# cria o banco se ele não existir
if not database_exists(engine.url):
    create_database(engine.url)

# cria as tabelas do banco, caso não existam
Base.metadata.create_all(engine)
