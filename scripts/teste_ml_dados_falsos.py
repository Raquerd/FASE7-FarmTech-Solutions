import pandas as pd, alertas
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
import joblib
import os

# --- CONFIGURAÇÃO ---
CAMINHO_MODELO = r'C:\Users\Davi\Documents\Projetos\FIAP\FASE 7\Capitulo 1\config\modelo_anomalia_sensores.pkl'

# --- ETAPA 3: TESTANDO COM DADOS FALSOS ---
print("\n--- ETAPA 3: HORA DA VERDADE (TESTE DE PREVISÃO) ---")

modelo_carregado = joblib.load(CAMINHO_MODELO)
colunas_ordem = ['UMIDADE', 'TEMPERATURA', 'PH']

# casos_teste = pd.DataFrame({
#     'UMIDADE':[50.5, 41.0, 10.0, 50.0, 50.0, 0.0],
#     'TEMPERATURA':[25.0, 21.0, 25.0, 80.0, 25.0, 0.0],
#     'PH':[7.0, 6.2, 7.0, 7.0, 2.0, 0.0]
# })

casos_teste = {
    'UMIDADE': np.random.uniform(90, 100, 1),     # Entre 40 e 60
    'TEMPERATURA': np.random.uniform(20, 30, 1), # Entre 20 e 30
    'PH': np.random.uniform(2.8, 3, 1)         # Entre 6.0 e 7.5
}


df = pd.DataFrame(casos_teste)
dados_teste = df[colunas_ordem]
print(dados_teste)

previsao = modelo_carregado.predict(dados_teste.values)
df['RESULTADO'] = previsao
df['RESULTADO'] = df['RESULTADO'].map({1:"✅ NORMAL", -1:"⚠️ ANOMALIA"})

print(casos_teste)

if previsao == -1:
    print(f"⚠️ ALERTA: Leitura estranha detectada! {df}")
    mensagem = f'''
    ⚠️ ALERTA FAZENDA:
    Anomalia detectada nos sensores!
    Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}
    '''
    # CORREÇÃO AQUI: Passando a variável mensagem
    alertas.enviar_alerta_sns(mensagem)
