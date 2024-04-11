
#Estabelece a conexão com o banco de dados
from datetime import datetime
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

db = SQLAlchemy()


#Representa a estrutura do banco de dados
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    value = db.Column(db.Float(precision=2), nullable=True)
    
    #Função para receber o request JSON
    def receive_JSON():

        data = request.json
        equipmentId = data['equipmentId']
        timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
        value = round(float(data['value']), 2)

        #Adiciona o dado do sensor ao banco de dados
        new_sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
        db.session.add(new_sensor_data)
        db.session.commit()

        return jsonify({'message': 'Data received!'}), 201
    
    #Função para receber o request CSV
    def receive_CSV():
        try:
            # Verifica se um arquivo CSV foi enviado
            if 'file' not in request.files:
                return "No file sent", 400
            
            file = request.files['file']
            
            # Verifica se o nome do arquivo está vazio
            if file.filename == '':
                return "File name empty", 400
            
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






    


