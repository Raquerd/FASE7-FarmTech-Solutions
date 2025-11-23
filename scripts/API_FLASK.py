import oracledb
import joblib
import alertas
import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_USER = "rm562274"
DB_PASS = "090402"
DB_DSN = "oracle.fiap.com.br:1521/ORCL" 

def get_db_connection():
    try:
        connection = oracledb.connect(user="rm562274", password="090402", dsn="oracle.fiap.com.br:1521/ORCL")
        return connection
    except oracledb.Error as e:
        print(f"Erro ao conectar no Oracle: {e}")
        return None

caminho_modelo = rf'C:\Users\Davi\Documents\Projetos\FIAP\FASE 7\Capitulo 1\documents\modelo_anomalia_sensores.pkl'

try:
    modelo_anomalia = joblib.load(caminho_modelo)
except FileNotFoundError:
    print(f"ERRO: Não encontrei o arquivo {caminho_modelo}")

    modelo_anomalia = None 

@app.route('/api/dados', methods=['POST'])
def receber_dados():
    if modelo_anomalia is None:
        return jsonify({"erro": "Modelo ML não carregado no servidor"}), 500

    data = request.json
    
    if not data:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
    
    print(f"Recebido: {data}") 
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            INSERT INTO SENSORES (UMIDADE, TEMPERATURA, PH, FOSFORO, POTASSIO, BOMBA)
            VALUES (:1, :2, :3, :4, :5, :6)
        """
        try:
            valores = (
                data.get('umidade'),
                data.get('temperatura'),
                data.get('ph'),
                1 if data.get('fosforo') else 0,
                1 if data.get('potassio') else 0,
                1 if data.get('bomba') else 0
            )
            
            # Validação para o modelo ML
            dados_sensores = [[
                data.get('umidade', 0), 
                data.get('temperatura', 0),
                data.get('ph', 0)
            ]]
            
            resultado = modelo_anomalia.predict(dados_sensores)[0]

            if resultado == -1:
                print(f"⚠️ ALERTA: Leitura estranha detectada! {dados_sensores}")
                mensagem = f'''
                ⚠️ ALERTA FAZENDA:
                Anomalia detectada nos sensores!
                Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                Dados: Umidade: {dados_sensores[0][0]}, Temp: {dados_sensores[0][1]}, PH: {dados_sensores[0][2]}
                '''
                # CORREÇÃO AQUI: Passando a variável mensagem
                alertas.enviar_alerta_sns(mensagem)

            cursor.execute(sql, valores)
            conn.commit()
            print("Dados salvos no Oracle com sucesso!")
            return jsonify({"status": "sucesso", "mensagem": "Dados gravados"}), 201
            
        except oracledb.Error as e:
            print(f"Erro ao inserir: {e}")
            return jsonify({"erro": str(e)}), 500
        except Exception as e:
            print(f"Erro genérico: {e}")
            return jsonify({"erro": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"erro": "Falha na conexão com o banco"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)