import oracledb, numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# 1. CRIAR DADOS FICTÍCIOS (MOCK)
dados = {
    'UMIDADE': np.random.uniform(30, 80, 100),     # Entre 40 e 60
    'TEMPERATURA': np.random.uniform(20, 30, 100), # Entre 20 e 30
    'PH': np.random.uniform(5.8, 7.2, 100)         # Entre 6.0 e 7.5
}

df = pd.DataFrame(dados)
print(f"Gerados {len(df)} dados fictícios para treinamento.")

# 2. TREINAMENTO
modelo_anomalia = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
modelo_anomalia.fit(df.values)

# 3. SALVAR
joblib.dump(modelo_anomalia, r'C:\Users\Davi\Documents\Projetos\FIAP\FASE 7\Capitulo 1\config\modelo_anomalia_sensores.pkl')
print("Modelo de anomalia salvo!")
