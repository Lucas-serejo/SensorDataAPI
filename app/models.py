
#Estabelece a conexão com o banco de dados
from datetime import datetime
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

db = SQLAlchemy()


#Representa a estrutura do banco de dados
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float(precision=2), nullable=True)
    
    #Função para receber o request JSON
    def receive_JSON():

        data = request.json
        equipmentId = data['equipmentId']
        timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
        
        #Verifica se o campo value está presente
        if 'value' in data:
            try:
                value = round(float(data['value']), 2)
            #Captura os eventuais erros de escrita ou valor e atrui o valor nulo
            except (TypeError, ValueError):
                value = None
        #Caso não esteja presente, atribui o valor nulo
        else:
            value = None

        #Adiciona o dado do sensor ao banco de dados
        new_sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
        db.session.add(new_sensor_data)
        db.session.commit()

        return jsonify({'message': 'Data received!'}), 201
    
    #Função para buscar valores do campo 'value' nulos e retornando um dicionário
    def search_values_byId():
        # Consulta os registros no banco de dados com 'value' nulo
        null_value_records = SensorData.query.filter(SensorData.value.is_(None)).all()
        
        # Cria um dicionário de tuplas (equipmentId) para os registros com 'value' nulo
        print("Registros com value nulo:", null_value_records)
        return {(record.equipmentId): record for record in null_value_records}
    
    def search_values_byObjct():
        return SensorData.query.filter(SensorData.value.is_(None)).all()

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
                map_values = SensorData.search_values_byId()


                #Itera pelas linhas do arquivo csv
                for _, row in df.iterrows():
                    equipmentId = str(row['equipmentId'])
                    timestamp = datetime.strptime(row['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    value = round(float(row['value']), 2)

                    if (equipmentId) in map_values:
                        # Atualiza o 'value' do registro correspondente com o valor do arquivo CSV
                       record = map_values[(equipmentId)]
                       record.value = value
                       print(f"Registro atualizado: equipmentId={equipmentId}, timestamp={timestamp}, value={value}")
                    else:
                        #Caso não haja valores correspondentes, cria um novo registro na tabela
                        sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
                        db.session.add(sensor_data)
                    
                # Commit para salvar as alterações no banco de dados
                db.session.commit()
                
                return "CSV file was processed and database was Updated", 200
            
            else:
                return "Please, insert a CVS file", 400
        
        except Exception as e:
            return f"Error processing CSV file: {str(e)}", 500






    


