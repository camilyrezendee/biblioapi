from flask import request, jsonify

from app import app, db
from models import Livro, Emprestimo
from token_jwt import validar_token


# confere os dados do livro (usado no POST e no PUT)
# devolve a mensagem de erro, ou None se estiver tudo certo
def validar_livro(dados):
    if not dados:
        return 'Envie os dados do livro'
    if not dados.get('titulo') or not dados.get('autor'):
        return 'Titulo e autor sao obrigatorios'
    exemplares = dados.get('exemplares')
    if type(exemplares) != int or exemplares < 0:
        return 'Exemplares deve ser um numero inteiro maior ou igual a 0'
    return None


# lista os livros, da pra filtrar por titulo ou autor (?autor=...)
@app.route('/livros', methods=['GET'])
def listar_livros():
    payload, erro = validar_token()
    if erro:
        return erro

    filtros = {}
    if request.args.get('titulo'):
        filtros['titulo'] = request.args.get('titulo')
    if request.args.get('autor'):
        filtros['autor'] = request.args.get('autor')

    livros = Livro.query.filter_by(**filtros).all()
    return jsonify([livro.para_dict() for livro in livros]), 200


# cadastra um livro novo
@app.route('/livros', methods=['POST'])
def cadastrar_livro():
    payload, erro = validar_token()
    if erro:
        return erro

    dados = request.get_json()
    mensagem = validar_livro(dados)
    if mensagem:
        return jsonify({'mensagem': mensagem}), 400

    livro = Livro(titulo=dados['titulo'],
                  autor=dados['autor'],
                  exemplares=dados['exemplares'])
    db.session.add(livro)
    db.session.commit()
    return jsonify(livro.para_dict()), 201


# mostra um livro pelo id
@app.route('/livros/<int:livro_id>', methods=['GET'])
def ver_livro(livro_id):
    payload, erro = validar_token()
    if erro:
        return erro

    livro = Livro.query.get(livro_id)
    if not livro:
        return jsonify({'mensagem': 'Livro nao encontrado'}), 404

    return jsonify(livro.para_dict()), 200


# atualiza um livro (manda todos os campos)
@app.route('/livros/<int:livro_id>', methods=['PUT'])
def atualizar_livro(livro_id):
    payload, erro = validar_token()
    if erro:
        return erro

    livro = Livro.query.get(livro_id)
    if not livro:
        return jsonify({'mensagem': 'Livro nao encontrado'}), 404

    dados = request.get_json()
    mensagem = validar_livro(dados)
    if mensagem:
        return jsonify({'mensagem': mensagem}), 400

    livro.titulo = dados['titulo']
    livro.autor = dados['autor']
    livro.exemplares = dados['exemplares']
    db.session.commit()
    return jsonify(livro.para_dict()), 200


# exclui um livro, mas so se nao tiver emprestimo em aberto
@app.route('/livros/<int:livro_id>', methods=['DELETE'])
def excluir_livro(livro_id):
    payload, erro = validar_token()
    if erro:
        return erro

    livro = Livro.query.get(livro_id)
    if not livro:
        return jsonify({'mensagem': 'Livro nao encontrado'}), 404

    ativos = Emprestimo.query.filter_by(livro_id=livro_id, status='ativo').all()
    if ativos:
        return jsonify({'mensagem': 'Nao pode excluir: livro com emprestimo ativo'}), 409

    db.session.delete(livro)
    db.session.commit()
    return jsonify({'mensagem': 'Livro excluido com sucesso'}), 200
