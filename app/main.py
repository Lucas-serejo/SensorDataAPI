from models import db, SensorData
import pandas as pd
from flask import Flask, render_template, request, jsonify
from datetime import datetime


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:mysqlroot@localhost/SensorData'
db.init_app(app)

# Criar todas as tabelas no banco de dados
with app.app_context():
    db.create_all()

# Rota para renderizar o formulário HTML
@app.route('/')
def index():
    return render_template('upload.html')



#Função destinada a receber os payloads em JSON dos sensores
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    return SensorData.receive_JSON(data)



#Função destinada a receber arquivos csv com dados faltantes no banco
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Verifica se um arquivo CSV foi enviado
        if 'file' not in request.files:
            return "Nenhum arquivo enviado", 400
        
        file = request.files['file']
        
        # Verifica se o nome do arquivo está vazio
        if file.filename == '':
            return "Nome do arquivo vazio", 400
        
        # Verifica se o arquivo é um arquivo CSV
        if file and file.filename.endswith('.csv'):
            # Lê o arquivo CSV e processa os dados
            df = pd.read_csv(file)
            
            for _, row in df.iterrows():
                equipmentId = str(row['equipmentId'])
                timestamp = datetime.strptime(row['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
                value = round(float(row['value']), 2)
                
                # Cria um novo objeto SensorData e o adiciona ao banco de dados
                sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
                db.session.add(sensor_data)
            
            # Commit para salvar os dados no banco de dados
            db.session.commit()
            
            return "Arquivo CSV processado e dados adicionados ao banco de dados com sucesso!", 200
        
        else:
            return "Por favor, envie um arquivo CSV", 400
    
    except Exception as e:
        return f"Erro ao processar o arquivo CSV: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)