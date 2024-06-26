from datetime import datetime, timedelta
import random
from flask import jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pandas as pd

#Instância do  SQLAlchemy para manipulação do banco de dados.
db = SQLAlchemy()

#Representa a estrutura do banco de dados.
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float(precision=2), nullable=True)
    
    #Função para receber o request JSON.
    def receive_JSON():

        #Identifica a requisição do payload em formato JSON.
        data = request.json
        equipmentId = data['equipmentId']
        timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
        
        #Verifica se o campo value está presente.
        if 'value' in data:
            try:
                value = round(float(data['value']), 2)
            #Captura os eventuais erros de escrita ou valor e atrui o valor nulo.
            except (TypeError, ValueError):
                value = None
        #Caso não esteja presente, atribui o valor nulo.
        else:
            value = None

        #Adiciona o dado do sensor ao banco de dados.
        new_sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
        db.session.add(new_sensor_data)
        db.session.commit()

        return jsonify({'message': 'Data received!'}), 201
    
    #Função para buscar valores do campo 'value' nulos.
    def search_values_byId():
        # Consulta os registros no banco de dados com 'value' nulo
        null_value_records = SensorData.query.filter(SensorData.value.is_(None)).all()
        
        # Cria um dicionário de tuplas (equipmentId) para os registros com 'value' nulo
        return {(record.equipmentId): record for record in null_value_records}
    
    #Função para buscar todos os objetos (registros) com campo 'value' nulo.
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
                        # Atualiza o 'value' do registro correspondente com o valor do arquivo CSV.
                       record = map_values[(equipmentId)]
                       record.value = value
                       print(f"Registro atualizado: equipmentId={equipmentId}, timestamp={timestamp}, value={value}")
                    else:
                        #Caso não haja valores correspondentes, cria um novo registro na tabela.
                        sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
                        db.session.add(sensor_data)
                    
                # Commit para salvar as alterações no banco de dados.
                db.session.commit()
                
                #Retorno o template da página de informação sobre a inserção do CSV.
                return render_template('message.html', mensagem = "CSV file was processed and database was Updated") 
            
            else:
                return render_template('message.html', mensagem = "Please, insert a CVS file") 
        
        except Exception as e:
            return f"Error processing CSV file: {str(e)}", 500

    #Função para gerar os valores aleatórios no formato JSON utilizado no projeto.
    def generate_simulated_data(equipment_id_prefix, timestamp_start, timestamp_end, min_value, max_value, null_value_prob):
            equipment_id = f"{equipment_id_prefix}-{random.randint(10000, 99999)}"
            timestamp = SensorData.generate_random_timestamp(timestamp_start, timestamp_end)
            value = round(random.uniform(min_value, max_value), 2) if random.random() > null_value_prob else None

            return {
                "equipmentId": equipment_id,
                "timestamp": timestamp.isoformat(),
                "value": value
        }

    #Função para gerar um timestamp aleatório dentro do intervalo de tempo especificado.
    def generate_random_timestamp(start_time, end_time):
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%f%z")
        random_timestamp = start_time + (end_time - start_time) * random.random()
        return random_timestamp

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

        #Consulta os registros no banco de dados para o período especificado
        query_result = SensorData.query.filter(SensorData.timestamp >= start_time).all()

        #Extrai os valores relevantes para cálculo da média (excluindo valores None)
        values = [record.value for record in query_result if record.value is not None]

        # Calcula a média dos valores.
        if values:
            average_value = np.mean(values)
        else:
            average_value = 0

        #Atribui o chart selecionado pelo usuário à média.
        average_values[chart_type] = average_value

        return average_values


