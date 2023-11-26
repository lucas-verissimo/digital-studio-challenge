import random
import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import hashlib

# Configurações de conexão ao banco de dados PostgreSQL
db_host = 'db'
db_port = '5432'
db_user = 'adminestudiodigital'
db_password = 'passwordestudiodigital'
db_name = 'estudiodigital'

# URL de conexão para o SQLAlchemy
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Função para verificar se o PostgreSQL está pronto
def is_postgres_ready():
    try:
        # Tenta criar uma conexão com o banco de dados
        engine = create_engine(db_url)
        engine.connect()
        return True
    except OperationalError:
        return False

# Aguarda até que o PostgreSQL esteja pronto
max_retries = 30
retry_interval = 2  # segundos

for _ in range(max_retries):
    if is_postgres_ready():
        break
    else:
        print("Aguardando o PostgreSQL iniciar...")
        time.sleep(retry_interval)
else:
    # Se atingir o número máximo de tentativas, exibe uma mensagem de erro
    raise RuntimeError("Não foi possível conectar ao PostgreSQL após várias tentativas.")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adminestudiodigital:passwordestudiodigital@db:5432/estudiodigital'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class ClientList(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    clients = db.relationship('Client', backref='client_list', lazy=True)

class Client(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    celphone = db.Column(db.String(11), nullable=False)
    status = db.Column(db.Boolean, default=True)
    hash = db.Column(db.String(64), nullable=False)
    client_list_id = db.Column(db.String(32), db.ForeignKey('client_list.id'), nullable=False)

def create_new_list():
    new_list = ClientList(id=generate_list_id())
    db.session.add(new_list)
    db.session.commit()
    return new_list

def generate_list_id():
    timestamp = str(int(time.time()))
    random_part = str(random.randint(1000, 99999999))
    return timestamp + random_part

def get_or_create_current_list():
    current_list = ClientList.query.order_by(ClientList.id.desc()).first()

    if current_list is None or len(current_list.clients) >= 100:
        current_list = create_new_list()

    return current_list

@app.route('/client', methods=['POST'])
def create_client():
    data = request.get_json()

    client_id = data.get('id')
    name = data.get('name')
    email = data.get('email')
    celphone = data.get('celphone')
    status = data.get('status')
    hash_value = data.get('hash')

    if not client_id or not name or not email or not celphone or not status or not hash_value:
        return jsonify({'error': 'Missing required fields'}), 422

    hashed_value = hashlib.sha256(data['hash'].encode()).hexdigest()

    current_list = get_or_create_current_list()

    try:
        new_client = Client(id=data['id'], name=data['name'], email=data['email'],
                            celphone=data['celphone'], status=data['status'], hash=hashed_value,
                            client_list=current_list)
        db.session.add(new_client)
        db.session.commit()
        return jsonify({'list_id': current_list.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Duplicate entry'}), 422
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': 'Internal Server Error'}), 400

@app.route('/client/<list_id>', methods=['GET'])
def get_client_list(list_id):
    try:
        client_list = ClientList.query.get(list_id)
        if client_list:
            result = {'list': []}
            for client in client_list.clients:
                result['list'].append({
                    'id': client.id,
                    'name': client.name,
                    'email': client.email,
                    'celphone': client.celphone,
                    'status': client.status,
                    'hash': client.hash
                })
            return jsonify(result)
        else:
            return jsonify({'error': 'List not found'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
