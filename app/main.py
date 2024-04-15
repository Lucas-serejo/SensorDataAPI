from datetime import datetime, timezone
import os
import webbrowser
from models import db, SensorData
from flask import Flask, jsonify, render_template, request

#Cria uma instância do framework flask
app = Flask(__name__)

#Estabelece a conexão com o banco de dados.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://adm:admpassword@localhost/SensorData'
db.init_app(app)

#Criar todas as tabelas no banco de dados.
with app.app_context():
    db.create_all()

#Função simuladora de sensores para enviar à rota que trata os payloads.
def send_simulated_data_to_route():
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    #Estabelece os parâmetros de geração dos valores aleatórios dos payloads simulados.
    num_records = 2000
    equipment_id_prefix = "EQ"
    timestamp_start ="2024-02-10T00:30:00.000+00:00"
    timestamp_end = current_time
    min_value = 100
    max_value = 5000
    null_value_prob = 0.2


    for _ in range(num_records):
        simulated_data = SensorData.generate_simulated_data(equipment_id_prefix, timestamp_start, timestamp_end, min_value, max_value, null_value_prob)
        response = app.test_client().post('/data', json=simulated_data)



#Definindo a rota para renderizar o formulário HTML da página home.
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home.html')

#Definindo a rota para a geração da tabela com registros com valor nulo.
@app.route('/search_values')
def search_null():
    return render_template('search_values.html', records = SensorData.search_values_byObjct())

#Definindo a rota para receber o arquivo JSON.
@app.route('/data', methods=['POST'])
def receive_data():
    return SensorData.receive_JSON()

#Definindo a rota para receber o arquivo CSV.
@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        return SensorData.receive_CSV()
    return render_template('upload_csv.html')

#Definindo a rota para renderizar os gráficos.
@app.route('/graphics', methods = ['GET'])
def graphics():
    return render_template('graphics.html')

#Definindo a rota para receber o período de tempo do usuário.
@app.route('/get_chart', methods=['GET'])
def get_chart():
    #Recebe o tempo selecionado.
    chart_type = request.args.get('chartType')

    # Calcula os valores médios para o período de tempo específico (24h, 48h, 1w, 1m).
    average_values = SensorData.calculate_average_values(chart_type)

    # Retorna os valores médios como resposta JSON.
    return jsonify(average_values)


if __name__ == '__main__':
    send_simulated_data_to_route()
    #Para executar apenas uma vez
    if not os.environ.get("WERKZEUG_RUN_MAIN"): 
        webbrowser.open("http://127.0.0.1:5000/")
        
app.run(debug=False)