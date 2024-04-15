from datetime import datetime, timedelta
import random
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
import numpy as np
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

    @staticmethod
    def generate_simulated_data(equipment_id_prefix, timestamp_start, timestamp_end, min_value=50.0, max_value=100.0, null_value_prob=0.2):
            equipment_id = f"{equipment_id_prefix}-{random.randint(10000, 99999)}"
            timestamp = SensorData.generate_random_timestamp(timestamp_start, timestamp_end)
            value = round(random.uniform(min_value, max_value), 2) if random.random() > null_value_prob else None

            return {
                "equipmentId": equipment_id,
                "timestamp": timestamp.isoformat(),
                "value": value
        }

    @staticmethod  
    def generate_random_timestamp(start_time, end_time):
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
        random_timestamp = start_time + (end_time - start_time) * random.random()
        return random_timestamp

    @staticmethod  
    def fill_database_with_simulated_data(num_records, equipment_id_prefix, timestamp_start, timestamp_end, min_value=50.0, max_value=100.0, null_value_prob=0.2):
        for _ in range(num_records):
            simulated_data = SensorData.generate_simulated_data(equipment_id_prefix, timestamp_start, timestamp_end, min_value, max_value, null_value_prob)
            SensorData.save_simulated_data_to_database(simulated_data)

        print(f"Simulação concluída. {num_records} registros foram adicionados ao banco de dados.")

    @staticmethod
    def save_simulated_data_to_database(data):
        try:
            equipmentId = data['equipmentId']
            timestamp = datetime.fromisoformat(data['timestamp'])
            value = data['value']

            new_sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
            db.session.add(new_sensor_data)
            db.session.commit()
        except Exception as e:
            print(f"Erro ao salvar dados simulados no banco de dados: {e}")


    #Realiza o cálculo da média dos valores do banco
    def calculate_average_values(chart_type):

        #Cria um dicionário para referenciar o período e a média
        average_values = {}

        #Encontra o intervalo de tempo baseado na escolha do usuário
        if chart_type == '24h':
            start_time = datetime.now() - timedelta(days=1)
        elif chart_type == '48h':
            start_time = datetime.now() - timedelta(days=2)
        elif chart_type == '1w':
            start_time = datetime.now() - timedelta(weeks=1)
        elif chart_type == '1m':
            start_time = datetime.now() - timedelta(weeks=4)
        else:
            raise ValueError("Tipo de gráfico inválido")
        
        print(start_time)

        # Consulta os registros no banco de dados para o período especificado
        query_result = SensorData.query.filter(SensorData.timestamp >= start_time).all()

        print(query_result)

        # Extrai os valores relevantes para cálculo da média (excluindo valores None)
        values = [record.value for record in query_result if record.value is not None]

        print(values)

        # Calcula a média dos valores
        if values:
            average_value = np.mean(values)
        else:
            average_value = 0

        average_values[chart_type] = average_value

        print(average_values)

        return average_values


