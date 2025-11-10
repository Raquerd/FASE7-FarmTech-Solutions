import pandas as pd, json, os, requests, oracledb, time, streamlit as st
from datetime import datetime

# Conexão banco de dados Oracle
conn = oracledb.connect(user='rm562274', password='090402', dsn='oracle.fiap.com.br:1521/ORCL') 
cursor = conn.cursor()

# Conexões API (Open Weather Map)
API_KEY = '7621dd8760f87d562a4e5a21bffbdc36'
cidade = 'Sao Paulo'

url = f'https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br'

#  Previsão do tempo API
def previsao_tempo(url):
    resposta = requests.get(url).json()

    chuva = resposta.get("rain", {}).get("1h", 0)
    clima = resposta.get("weather")[0]["description"]
    print("Previsão de chuva (1h):", chuva)

    if chuva > 0:
        print("Chuva prevista: bomba OFF")
    else:
        print("Sem chuva: bomba ON (se necessário)")
    return clima

# Inserção de dados manual
def inserir_dado_manual(umidade, ph, fosforo, potassio, bomba):
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO sensores (time, umidade, ph, fosforo, potassio, bomba)
    VALUES (:1, :2, :3, :4, :5, :6)
    ''', (time, umidade, ph, fosforo, potassio, bomba))
    conn.commit()

# Consulta
def listar_dados(min: str | None = ..., date_options: bool = False):
    if date_options == True:
        dataframe = pd.read_sql(f"SELECT * FROM sensores where time like '{min}%'", conn)
    else:
        dataframe = pd.read_sql('SELECT * FROM sensores', conn)
    return dataframe

# Atualizar dado
def atualizar_dado_manual(id, campo, valor):
    cursor.execute(f'''
    UPDATE sensores SET {campo} = {valor} WHERE id = {id}
    ''')
    conn.commit()

# Remover dado
def deletar_dado(id):
    cursor.execute('DELETE FROM sensores WHERE id = :1', (id,))
    conn.commit()

st.set_page_config(layout="wide", page_title="Controle de Sensores Agrícolas")
st.sidebar.title("Menu de opções")
menu = {
    "1": "Inserir dados",
    "2": "Consultar dados cadastrados",
    "3": "Atualizar dados cadastrados",
    "4": "Excluir dados cadastrados",
    "5": "Sair"
}

menu_option_action = st.sidebar.radio(
    "SELECIONE UMA AÇÃO",
    list(menu.values()),
    key="main_menu_radio"
)

st.title(f"Página: {menu_option_action}")

if menu_option_action == menu["1"]:
    st.subheader("Upload de Arquivo em lote (CSV)")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])

    if uploaded_file is not None:
            try:
                # O Streamlit lida com o arquivo em memória, não precisa de path
                df_dados_importados = pd.read_csv(uploaded_file, sep=',')
                st.dataframe(df_dados_importados) # Opcional: mostrar o DataFrame

                # O botão executa a inserção
                if st.button("Executar Inserção em Lote"):

                    cursor = conn.cursor()
                    
                    # Usa o método robusto (.to_numpy().tolist()) para o executemany
                    dados_para_insercao = df_dados_importados[['TIME', 'UMIDADE', 'PH', 'FOSFORO', 'POTASSIO', 'BOMBA']].to_numpy().tolist()

                    cursor.executemany('''
                        INSERT INTO SENSORES (TIME, UMIDADE, PH, FOSFORO, POTASSIO, BOMBA)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', dados_para_insercao) # Usando '?' para sqlite3 por segurança

                    conn.commit()
                    conn.close()
                    st.success(f"✅ {len(df_dados_importados)} registros inseridos com sucesso!")

            except Exception as e:
                st.error(f"❌ Erro ao processar o arquivo ou inserir dados: {e}")

elif menu_option_action == menu["2"]:
    col1, col2 = st.columns(2)
    with col1:
        dt_inicial = st.text_input('Digite a data inicial: ', key="dt_init")

    with col2:
        dt_final = st.text_input('Digite a data final: ', key="dt_fin")
    
    if dt_inicial != None or dt_final != None:

        df_extraido = pd.read_sql(f'''
            SELECT * FROM SENSORES
                WHERE TIME >= '{dt_inicial}' AND TIME <= '{dt_final}'
        ''', conn)
        st.subheader("Resultados da extração")
        st.dataframe(df_extraido)
        
        if not df_extraido.empty:
            st.download_button(
                label="Baixar dados em CSV",
                data=df_extraido.to_csv(index=False, sep=","),
                file_name=f"df_extraido_{dt_inicial}_a_{dt_final}.csv",
                mime="text/csv",
                key="Extrair"
            )

elif menu_option_action == menu["3"]:
    menu_att = {"1":"Atualização por lote (DATA)", "2":"Atualização por ID"}
    menu_att_action = st.radio("SELECIONE A AÇÃO DE ATUALIZAÇÃO NECESSÁRIA",
            list(menu_att.values()),
            key="menu_atualizacao")
    
    if menu_att_action == menu_att["1"]:
        col1, col2 = st.columns(2)
        with col1:
            dt_inicial = st.text_input("Digite a data inicial de edição: ", key="dt_init_att")
        with col2:
            dt_final = st.text_input("Digite a data inicial de edição: ", key="dt_fin_att")

        df_att = pd.read_sql(f"SELECT * FROM SENSORES WHERE TIME >= '{dt_inicial}' AND TIME <= '{dt_final}'", conn)
        

    if menu_att_action == menu_att["2"]:
        id_input_att = st.text_input("Digite o ID procurado: ", key="id_att")
        df_att = pd.read_sql(f"SELECT * FROM SENSORES WHERE ID = '{id_input_att}'", conn)

    st.dataframe(df_att)
         
    # st.text_input("Digite o ID que deseja alterar: ")
