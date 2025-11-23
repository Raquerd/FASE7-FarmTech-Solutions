import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Configurações ---
dias_para_simular = 60
intervalo = '10min'  # 10 minutos
data_final = datetime.now()
data_inicial = data_final - timedelta(days=dias_para_simular)

# 1. Gerar o Index de Datas (O "esqueleto" da tabela)
# freq='10min' cria automaticamente os intervalos: 00:00, 00:10, 00:20...
datas = pd.date_range(start=data_inicial, end=data_final, freq=intervalo)
n_registros = len(datas)

print(f"Gerando {n_registros} registros simulados...")

# --- 2. Vetorização (Cálculos em massa) ---

# Extrair a hora decimal de cada registro para o cálculo da curva (Ex: 14:30 = 14.5)
horas = datas.hour + (datas.minute / 60)

# A. TEMPERATURA (Curva Senoidal baseada no array de horas)
# Utiliza numpy para calcular todas as 8 mil temperaturas de uma vez
temp_base = 25 + (5 * -np.cos((horas - 4) * np.pi / 12))
temperatura = temp_base + np.random.normal(0, 0.5, n_registros)

# B. UMIDADE (Inversa à Temperatura)
umidade = 100 - ((temperatura - 15) * 3.5)
umidade += np.random.normal(0, 2, n_registros) # Ruído
umidade = np.clip(umidade, 30, 100) # Trava entre 30 e 100

# C. PH
ph = np.random.normal(6.0, 0.3, n_registros)
ph = np.clip(ph, 4.5, 8.0)

# D. NUTRIENTES (Lógica Condicional com Numpy)
# Cria uma "máscara" boleana: Onde o pH é bom?
ph_bom = (ph >= 5.5) & (ph <= 6.5)

# Define a probabilidade baseada na máscara (0.9 se bom, 0.3 se ruim)
probabilidades = np.where(ph_bom, 0.9, 0.3)

# Gera os binários (0 ou 1) comparando um número aleatório com a probabilidade
fosforo = (np.random.rand(n_registros) < probabilidades).astype(int)
potassio = (np.random.rand(n_registros) < probabilidades).astype(int)

# E. BOMBA
# Liga (1) onde a umidade for menor que 45
bomba = np.where(umidade < 45, 1, 0)

# --- 3. Montagem do DataFrame ---
df_simulado = pd.DataFrame({
    'ID': range(1, n_registros + 1),
    'DATA_LEITURA': datas,
    'TEMPERATURA': np.round(temperatura, 2),
    'UMIDADE': umidade.astype(int),
    'PH': np.round(ph, 2),
    'FOSFORO': fosforo,
    'POTASSIO': potassio,
    'BOMBA': bomba
})

df_simulado['DATA_LEITURA'] = df_simulado['DATA_LEITURA'].dt.strftime('%Y-%m-%d %H:%M:%S')
# Exibir resultados
print(f"Primeira leitura: {df_simulado['DATA_LEITURA'].iloc[0]}")
print(f"Última leitura:   {df_simulado['DATA_LEITURA'].iloc[-1]}")
print("\n--- Amostra dos dados (Head) ---")
print(df_simulado.head())

# Opcional: Salvar para CSV para conferência
# df_simulado.to_csv('dados_plantio_10min.csv', index=False)

nome_arquivo = r"C:\Users\Davi\Documents\Projetos\FIAP\FASE 7\Capitulo 1\config\dados_sensores_agricolas.csv"
df_simulado.to_csv(nome_arquivo, index=False, sep=',')

# print(f"\nArquivo '{nome_arquivo}' gerado com sucesso!")

# cursor = conn.cursor()
                    
# # Usa o método robusto (.to_numpy().tolist()) para o executemany
# dados_para_insercao = df[['DATA_LEITURA', 'UMIDADE', 'PH', 'FOSFORO', 'POTASSIO', 'BOMBA']].to_numpy().tolist()

# cursor.executemany('''
#     INSERT INTO SENSORES (DATA_LEITURA, UMIDADE, PH, FOSFORO, POTASSIO, BOMBA)
#     VALUES (?, ?, ?, ?, ?, ?)
# ''', dados_para_insercao) # Usando '?' para sqlite3 por segurança

# conn.commit()
# conn.close()

