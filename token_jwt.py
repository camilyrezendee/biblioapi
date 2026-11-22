import jose
from flask import request, jsonify
from jose import jwt

from app import app


# gera o token com os dados do payload
def gerar_token(payload):
    token = jwt.encode(payload,
                       app.config['SECRET_KEY'],
                       algorithm=app.config['ALGORITHM'])
    return token


# confere se o token e valido, se nao for devolve None
def verificar_token(token):
    try:
        payload = jwt.decode(token,
                             app.config['SECRET_KEY'],
                             algorithms=[app.config['ALGORITHM']])
        return payload
    except jose.exceptions.JWTError as e:
        print(e)
        return None


# validacao do token num lugar so, todas as rotas fora do /auth chamam essa
# devolve (payload, None) se deu certo ou (None, resposta de erro) se nao
def validar_token():
    authorization = request.headers.get('Authorization')
    if not authorization or ' ' not in authorization:
        return None, (jsonify({'mensagem': 'Token ausente'}), 401)

    token = authorization.split(' ')[1]
    payload = verificar_token(token)
    if not payload:
        return None, (jsonify({'mensagem': 'Token invalido'}), 401)

    return payload, None
