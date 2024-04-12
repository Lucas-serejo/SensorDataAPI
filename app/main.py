from models import db, SensorData
from flask import Flask, render_template

#Cria uma instância do framework flask
app = Flask(__name__)

#Estabelece a conexão com o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mysqlroot@localhost/SensorData'
db.init_app(app)

#Criar todas as tabelas no banco de dados
with app.app_context():
    db.create_all()

#Definindo a rota para renderizar o formulário HTML
@app.route('/')
def index():
    return render_template('upload.html')

#Definindo a rota para receber o arquivo JSON
@app.route('/data', methods=['POST'])
def receive_data():
    return SensorData.receive_JSON()

#Definindo a rota para receber o arquivo CSV
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    return SensorData.receive_CSV()

if __name__ == '__main__':
    app.run(debug=True)