import datetime
from flask import request, jsonify

from app import app, db
from models import Bibliotecario
from token_jwt import gerar_token


# cadastro do bibliotecario (nao precisa de token)
@app.route('/auth/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()

    # campos obrigatorios preenchidos?
    if not dados or not dados.get('nome') or not dados.get('email') or not dados.get('senha'):
        return jsonify({'mensagem': 'Preencha nome, email e senha'}), 400

    # e-mail ja cadastrado?
    existe = Bibliotecario.query.filter_by(email=dados['email']).first()
    if existe:
        return jsonify({'mensagem': 'E-mail ja esta em uso'}), 409

    novo = Bibliotecario(nome=dados['nome'],
                         email=dados['email'],
                         senha=dados['senha'])
    db.session.add(novo)
    db.session.commit()
    return jsonify(novo.para_dict()), 201


# login: se email e senha conferem, devolve o token
@app.route('/auth/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({'mensagem': 'E-mail ou senha invalidos'}), 401

    bibliotecario = Bibliotecario.query.filter_by(email=dados.get('email'),
                                                  senha=dados.get('senha')).first()
    if not bibliotecario:
        return jsonify({'mensagem': 'E-mail ou senha invalidos'}), 401

    # token vale 30 minutos
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        'iat': datetime.datetime.utcnow(),
        'sub': str(bibliotecario.id)
    }
    token = gerar_token(payload)
    return jsonify({'token': token, 'bibliotecario': bibliotecario.para_dict()}), 200
