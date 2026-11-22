from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import dynaconf

# cria a aplicacao e o banco
app = Flask(__name__)
db = SQLAlchemy()

# carrega as configuracoes (banco, chave secreta e algoritmo do jwt)
settings = dynaconf.FlaskDynaconf(
    app,
    settings_files=["settings.toml", ".secrets.toml"],
)
db.init_app(app)

# importa os models (cria as tabelas) e depois as rotas
import models
import rotas
