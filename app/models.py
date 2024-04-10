
#Estabelece a conexão com o banco de dados
from datetime import datetime
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#Representa a tabela do banco de dados
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipmentId = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    value = db.Column(db.Float(precision=2), nullable=True)

    def receive_JSON(data):
        equipmentId = data['equipmentId']
        timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S.%f%z")
        value = round(float(data['value']), 2)

        #Adiciona o dado do sensor ao banco de dados
        new_sensor_data = SensorData(equipmentId=equipmentId, timestamp=timestamp, value=value)
        db.session.add(new_sensor_data)
        db.session.commit()

        return jsonify({'message': 'Dados recebidos!'}), 201




    


