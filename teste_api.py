# testa a API rodando (flask --app app run) e mostra no terminal se cada caso deu o codigo esperado
# rodar num SEGUNDO terminal: python teste_api.py
import json
import time
import urllib.request
import urllib.error

URL = 'http://127.0.0.1:5000'
token = None
certos = 0
errados = 0


def chamar(metodo, rota, dados=None, com_token=True):
    corpo = json.dumps(dados).encode() if dados is not None else None
    req = urllib.request.Request(URL + rota, data=corpo, method=metodo)
    req.add_header('Content-Type', 'application/json')
    if com_token and token:
        req.add_header('Authorization', 'Bearer ' + token)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read() or 'null')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or 'null')


def testar(descricao, esperado, metodo, rota, dados=None, com_token=True):
    global certos, errados
    codigo, resposta = chamar(metodo, rota, dados, com_token)
    if codigo == esperado:
        certos += 1
        print(f'  OK    {codigo}  {descricao}')
    else:
        errados += 1
        print(f'  ERRO  esperava {esperado}, veio {codigo}  {descricao} -> {resposta}')
    return resposta


# e-mail diferente a cada execucao pra nao dar 409 no cadastro
email = f'teste{int(time.time())}@email.com'

print('\nAUTENTICACAO')
testar('cadastro faltando campo', 400, 'POST', '/auth/cadastro', {'nome': 'Ana'})
testar('cadastro', 201, 'POST', '/auth/cadastro', {'nome': 'Ana', 'email': email, 'senha': '123'})
testar('cadastro com e-mail repetido', 409, 'POST', '/auth/cadastro', {'nome': 'Ana', 'email': email, 'senha': '123'})
testar('login com senha errada', 401, 'POST', '/auth/login', {'email': email, 'senha': 'errada'})
token = testar('login', 200, 'POST', '/auth/login', {'email': email, 'senha': '123'})['token']

print('\nTOKEN')
testar('listar livros sem token', 401, 'GET', '/livros', com_token=False)

print('\nLIVROS')
testar('livro com exemplares negativo', 400, 'POST', '/livros', {'titulo': 'X', 'autor': 'Y', 'exemplares': -1})
livro1 = testar('cadastrar livro (1 exemplar)', 201, 'POST', '/livros', {'titulo': 'Dom Casmurro', 'autor': 'Machado', 'exemplares': 1})['id']
livro2 = testar('cadastrar livro (5 exemplares)', 201, 'POST', '/livros', {'titulo': 'Iracema', 'autor': 'Alencar', 'exemplares': 5})['id']
testar('listar livros', 200, 'GET', '/livros')
testar('ver livro', 200, 'GET', f'/livros/{livro1}')
testar('ver livro que nao existe', 404, 'GET', '/livros/99999')
testar('atualizar livro', 200, 'PUT', f'/livros/{livro2}', {'titulo': 'Iracema', 'autor': 'José de Alencar', 'exemplares': 5})
testar('atualizar com dados invalidos', 400, 'PUT', f'/livros/{livro2}', {'titulo': 'Iracema'})

print('\nLEITORES')
testar('leitor sem e-mail', 400, 'POST', '/leitores', {'nome': 'João'})
leitor = testar('cadastrar leitor', 201, 'POST', '/leitores', {'nome': 'João', 'email': 'joao@email.com'})['id']
leitor2 = testar('cadastrar outro leitor', 201, 'POST', '/leitores', {'nome': 'Maria', 'email': 'maria@email.com'})['id']
testar('listar leitores', 200, 'GET', '/leitores')

print('\nEMPRESTIMOS')
testar('emprestar livro que nao existe', 404, 'POST', '/emprestimos', {'livro_id': 99999, 'leitor_id': leitor})
emp = testar('emprestar livro 1', 201, 'POST', '/emprestimos', {'livro_id': livro1, 'leitor_id': leitor})['id']
testar('emprestar livro 1 sem exemplar', 409, 'POST', '/emprestimos', {'livro_id': livro1, 'leitor_id': leitor2})
testar('emprestar livro 2 (2o ativo)', 201, 'POST', '/emprestimos', {'livro_id': livro2, 'leitor_id': leitor})
testar('emprestar livro 2 (3o ativo)', 201, 'POST', '/emprestimos', {'livro_id': livro2, 'leitor_id': leitor})
testar('4o emprestimo passa do limite', 409, 'POST', '/emprestimos', {'livro_id': livro2, 'leitor_id': leitor})
testar('excluir livro emprestado', 409, 'DELETE', f'/livros/{livro1}')
testar('excluir leitor com emprestimo', 409, 'DELETE', f'/leitores/{leitor}')
testar('listar emprestimos ativos', 200, 'GET', '/emprestimos?status=ativo')
testar('devolver', 200, 'PUT', f'/emprestimos/{emp}/devolucao')
testar('devolver de novo', 404, 'PUT', f'/emprestimos/{emp}/devolucao')
exemplares = chamar('GET', f'/livros/{livro1}')[1]['exemplares']
print(f'  ->    livro 1 voltou a ter {exemplares} exemplar(es) depois da devolucao')
testar('excluir leitor sem emprestimo', 200, 'DELETE', f'/leitores/{leitor2}')

print(f'\nResultado: {certos} certos, {errados} errados\n')