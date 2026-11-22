from app import app, db


# bibliotecario = quem usa o sistema (faz cadastro e login)
class Bibliotecario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

    def para_dict(self):
        # nao devolvo a senha na resposta
        return {'id': self.id, 'nome': self.nome, 'email': self.email}


# livro do acervo, exemplares = quantos ainda estao na estante
class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    exemplares = db.Column(db.Integer, nullable=False, default=0)

    def para_dict(self):
        return {'id': self.id, 'titulo': self.titulo,
                'autor': self.autor, 'exemplares': self.exemplares}


# leitor = quem pega o livro emprestado
class Leitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    def para_dict(self):
        return {'id': self.id, 'nome': self.nome, 'email': self.email}


# emprestimo liga um livro a um leitor
# status: "ativo" enquanto o livro nao volta, "devolvido" depois
class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, nullable=False)
    leitor_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ativo')
    data_emprestimo = db.Column(db.DateTime, nullable=False)
    data_devolucao = db.Column(db.DateTime, nullable=True)

    def para_dict(self):
        return {'id': self.id, 'livro_id': self.livro_id,
                'leitor_id': self.leitor_id, 'status': self.status,
                'data_emprestimo': str(self.data_emprestimo),
                'data_devolucao': str(self.data_devolucao) if self.data_devolucao else None}


# cria as tabelas no banco (depois de todas as models)
with app.app_context():
    db.create_all()
