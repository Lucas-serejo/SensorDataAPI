import webbrowser
from models import db, SensorData
from flask import Flask, render_template, request

#Cria uma instância do framework flask
app = Flask(__name__)

#Estabelece a conexão com o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mysqlroot@localhost/SensorData'
db.init_app(app)

#Criar todas as tabelas no banco de dados
with app.app_context():
    db.create_all()

#Definindo a rota para renderizar o formulário HTML da página home
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/search_values')
def search_null():
    return render_template('search_values.html', records = SensorData.search_values_byObjct())

#Definindo a rota para receber o arquivo JSON
@app.route('/data', methods=['POST'])
def receive_data():
    return SensorData.receive_JSON()

#Definindo a rota para receber o arquivo CSV
@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        return SensorData.receive_CSV()
    return render_template('upload_csv.html')
#Suporte para abertura da página home ao rodar o script
def open_browser():
    base_url = 'http://127.0.0.1:5000/'
    try:
        # Tenta abrir o navegador apenas se a URL não estiver aberta
        webbrowser.get().open(base_url, new=2)
    except Exception as e:
        print(f"Erro ao abrir o navegador: {e}")

if __name__ == '__main__':
    open_browser()
    app.run(debug=True)