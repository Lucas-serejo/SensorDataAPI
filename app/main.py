from datetime import datetime
import os
import webbrowser
from matplotlib import pyplot as plt
# from graphic_generator import *
from models import db, SensorData
from flask import Flask, jsonify, render_template, request, send_file

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

    # Preencher o banco de dados com dados simulados ao iniciar o aplicativo
    num_records = 2000
    equipment_id_prefix = "EQ"
    timestamp_start = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S")
    timestamp_end = "2024-02-01T00:00:00"
    min_value = 10
    max_value = 1000
    null_value_prob = 0.2

    SensorData.fill_database_with_simulated_data(num_records, equipment_id_prefix, timestamp_start, timestamp_end, min_value, max_value, null_value_prob)
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

@app.route('/graphics', methods = ['GET'])
def graphics():
    return render_template('graphics.html')

@app.route('/get_chart', methods=['GET'])
def get_chart():
    chart_type = request.args.get('chartType')

    # Calcula os valores médios para o período de tempo específico (24h, 48h, 1w, 1m)
    average_values = SensorData.calculate_average_values(chart_type)

    # Retorna os valores médios como resposta JSON
    return jsonify(average_values)


if __name__ == '__main__':
    #Para executar apenas uma vez
    if not os.environ.get("WERKZEUG_RUN_MAIN"): 
        webbrowser.open("http://127.0.0.1:5000/")
        
app.run(debug=True)