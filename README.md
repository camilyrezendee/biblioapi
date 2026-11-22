# BiblioAPI

API de controle de livros e empréstimos de uma biblioteca, feita com Flask para a disciplina de Linguagem de Programação.

O bibliotecário faz cadastro e login, e com o token consegue cadastrar livros e leitores e registrar empréstimos e devoluções.

## Como rodar

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app run
```

## Rotas

Autenticação (não precisa de token):
- POST /auth/cadastro
- POST /auth/login

Livros:
- GET /livros
- POST /livros
- GET /livros/id
- PUT /livros/id
- DELETE /livros/id

Leitores:
- GET /leitores
- POST /leitores
- GET /leitores/id
- PUT /leitores/id
- DELETE /leitores/id

Empréstimos:
- GET /emprestimos
- POST /emprestimos
- PUT /emprestimos/id/devolucao

As rotas de livros, leitores e empréstimos precisam do token no header Authorization (Bearer token).

## Regras

- Ao emprestar, o livro perde 1 exemplar, e ao devolver ganha 1 de volta
- Não dá para emprestar livro sem exemplar
- Cada leitor pode ter no máximo 3 empréstimos ativos
- Não dá para excluir livro ou leitor com empréstimo em aberto

## Testes

Com a API rodando, em outro terminal:

```
python teste_api.py
```