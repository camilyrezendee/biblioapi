import datetime
from flask import request, jsonify

from app import app, db
from models import Emprestimo, Livro, Leitor
from token_jwt import validar_token

# limite de emprestimos ativos por leitor
LIMITE_EMPRESTIMOS = 3


# lista os emprestimos, da pra filtrar por status (?status=ativo ou devolvido)
@app.route('/emprestimos', methods=['GET'])
def listar_emprestimos():
    payload, erro = validar_token()
    if erro:
        return erro

    filtros = {}
    if request.args.get('status'):
        filtros['status'] = request.args.get('status')

    emprestimos = Emprestimo.query.filter_by(**filtros).all()
    return jsonify([e.para_dict() for e in emprestimos]), 200


# faz um emprestimo novo: recebe livro_id e leitor_id
@app.route('/emprestimos', methods=['POST'])
def emprestar():
    payload, erro = validar_token()
    if erro:
        return erro

    dados = request.get_json() or {}
    livro_id = dados.get('livro_id')
    leitor_id = dados.get('leitor_id')

    # livro e leitor existem?
    livro = Livro.query.get(livro_id) if livro_id else None
    leitor = Leitor.query.get(leitor_id) if leitor_id else None
    if not livro or not leitor:
        return jsonify({'mensagem': 'Livro ou leitor nao encontrado'}), 404

    # tem exemplar sobrando?
    if livro.exemplares <= 0:
        return jsonify({'mensagem': 'Sem exemplares disponiveis'}), 409

    # leitor ainda nao chegou no limite?
    ativos = Emprestimo.query.filter_by(leitor_id=leitor_id, status='ativo').all()
    if len(ativos) >= LIMITE_EMPRESTIMOS:
        return jsonify({'mensagem': 'Leitor ja tem 3 emprestimos ativos'}), 409

    # registra o emprestimo e tira 1 exemplar da estante
    emprestimo = Emprestimo(livro_id=livro_id,
                            leitor_id=leitor_id,
                            status='ativo',
                            data_emprestimo=datetime.datetime.utcnow())
    livro.exemplares = livro.exemplares - 1
    db.session.add(emprestimo)
    db.session.commit()
    return jsonify(emprestimo.para_dict()), 201


# devolve um livro: o emprestimo precisa existir e estar ativo
@app.route('/emprestimos/<int:emprestimo_id>/devolucao', methods=['PUT'])
def devolver(emprestimo_id):
    payload, erro = validar_token()
    if erro:
        return erro

    emprestimo = Emprestimo.query.get(emprestimo_id)
    if not emprestimo or emprestimo.status != 'ativo':
        return jsonify({'mensagem': 'Emprestimo nao encontrado ou ja devolvido'}), 404

    # marca como devolvido e o exemplar volta pra estante
    emprestimo.status = 'devolvido'
    emprestimo.data_devolucao = datetime.datetime.utcnow()
    livro = Livro.query.get(emprestimo.livro_id)
    livro.exemplares = livro.exemplares + 1
    db.session.commit()
    return jsonify(emprestimo.para_dict()), 200
