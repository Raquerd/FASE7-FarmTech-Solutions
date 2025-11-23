import oracledb
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
DB_USER = "rm562274"
DB_PASS = "090402"
DB_DSN = "oracle.fiap.com.br:1521/ORCL" 

def get_db_connection():
    try:
        connection = oracledb.connect(user=DB_USER, password=DB_PASS, dsn=DB_DSN)
        return connection
    except oracledb.Error as e:
        print(f"Erro ao conectar no Oracle: {e}")
        return None

# --- ROTA PARA RECEBER DADOS DO ESP32 ---
@app.route('/api/dados', methods=['POST'])
def receber_dados():
    data = request.json
    
    if not data:
        return jsonify({"erro": "Nenhum dado recebido"}), 400
    
    print(f"Recebido: {data}") # Log no terminal
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = """
            INSERT INTO SENSORES (UMIDADE, TEMPERATURA, PH, FOSFORO, POTASSIO, BOMBA_LIGADA)
            VALUES (:1, :2, :3, :4, :5, :6)
        """
        try:
            # Mapeando os dados do JSON para o SQL
            # O ESP32 enviará true/false, convertemos para 1/0 aqui
            valores = (
                data.get('umidade'),
                data.get('temperatura'),
                data.get('ph'),
                1 if data.get('fosforo') else 0,
                1 if data.get('potassio') else 0,
                1 if data.get('bomba') else 0
            )
            
            cursor.execute(sql, valores)
            conn.commit()
            print("Dados salvos no Oracle com sucesso!")
            return jsonify({"status": "sucesso", "mensagem": "Dados gravados"}), 201
            
        except oracledb.Error as e:
            print(f"Erro ao inserir: {e}")
            return jsonify({"erro": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"erro": "Falha na conexão com o banco"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)