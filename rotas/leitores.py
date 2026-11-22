from flask import request, jsonify

from app import app, db
from models import Leitor, Emprestimo
from token_jwt import validar_token


# confere os dados do leitor (usado no POST e no PUT)
def validar_leitor(dados):
    if not dados:
        return 'Envie os dados do leitor'
    if not dados.get('nome') or not dados.get('email'):
        return 'Nome e email sao obrigatorios'
    return None


# lista os leitores, da pra filtrar por nome (?nome=...)
@app.route('/leitores', methods=['GET'])
def listar_leitores():
    payload, erro = validar_token()
    if erro:
        return erro

    filtros = {}
    if request.args.get('nome'):
        filtros['nome'] = request.args.get('nome')

    leitores = Leitor.query.filter_by(**filtros).all()
    return jsonify([leitor.para_dict() for leitor in leitores]), 200


# cadastra um leitor novo
@app.route('/leitores', methods=['POST'])
def cadastrar_leitor():
    payload, erro = validar_token()
    if erro:
        return erro

    dados = request.get_json()
    mensagem = validar_leitor(dados)
    if mensagem:
        return jsonify({'mensagem': mensagem}), 400

    leitor = Leitor(nome=dados['nome'], email=dados['email'])
    db.session.add(leitor)
    db.session.commit()
    return jsonify(leitor.para_dict()), 201


# mostra um leitor pelo id
@app.route('/leitores/<int:leitor_id>', methods=['GET'])
def ver_leitor(leitor_id):
    payload, erro = validar_token()
    if erro:
        return erro

    leitor = Leitor.query.get(leitor_id)
    if not leitor:
        return jsonify({'mensagem': 'Leitor nao encontrado'}), 404

    return jsonify(leitor.para_dict()), 200


# atualiza um leitor (manda todos os campos)
@app.route('/leitores/<int:leitor_id>', methods=['PUT'])
def atualizar_leitor(leitor_id):
    payload, erro = validar_token()
    if erro:
        return erro

    leitor = Leitor.query.get(leitor_id)
    if not leitor:
        return jsonify({'mensagem': 'Leitor nao encontrado'}), 404

    dados = request.get_json()
    mensagem = validar_leitor(dados)
    if mensagem:
        return jsonify({'mensagem': mensagem}), 400

    leitor.nome = dados['nome']
    leitor.email = dados['email']
    db.session.commit()
    return jsonify(leitor.para_dict()), 200


# exclui um leitor, mas so se ele nao tiver emprestimo em aberto
@app.route('/leitores/<int:leitor_id>', methods=['DELETE'])
def excluir_leitor(leitor_id):
    payload, erro = validar_token()
    if erro:
        return erro

    leitor = Leitor.query.get(leitor_id)
    if not leitor:
        return jsonify({'mensagem': 'Leitor nao encontrado'}), 404

    ativos = Emprestimo.query.filter_by(leitor_id=leitor_id, status='ativo').all()
    if ativos:
        return jsonify({'mensagem': 'Nao pode excluir: leitor com emprestimo ativo'}), 409

    db.session.delete(leitor)
    db.session.commit()
    return jsonify({'mensagem': 'Leitor excluido com sucesso'}), 200
