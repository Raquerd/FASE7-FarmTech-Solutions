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
    DATA_LEITURA = datetime.datetime.now().strfDATA_LEITURA('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO TBL_SENSORES (DATA_LEITURA, umidade, ph, fosforo, potassio, bomba)
    VALUES (:1, :2, :3, :4, :5, :6)
    ''', (DATA_LEITURA, umidade, ph, fosforo, potassio, bomba))
    conn.commit()

# Consulta
def listar_dados(min: str | None = ..., date_options: bool = False):
    if date_options == True:
        dataframe = pd.read_sql(f"SELECT * FROM TBL_SENSORES where TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') like '{min}%'", conn)
    else:
        dataframe = pd.read_sql('SELECT * FROM TBL_SENSORES', conn)
    return dataframe

# Atualizar dado
def atualizar_dado_manual(id, campo, valor):
    cursor.execute(f'''
    UPDATE TBL_SENSORES SET {campo} = {valor} WHERE id = {id}
    ''')
    conn.commit()

# Remover dado
def deletar_dado(id):
    cursor.execute('DELETE FROM TBL_SENSORES WHERE id = :1', (id,))
    conn.commit()

st.set_page_config(layout="wide", page_title="Controle de TBL_SENSORES Agrícolas")
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
                    dados_para_insercao = df_dados_importados[['DATA_LEITURA', 'TEMPERATURA', 'UMIDADE', 'PH', 'FOSFORO', 'POTASSIO', 'BOMBA']].to_numpy().tolist()

                    cursor.executemany('''
                        INSERT INTO TBL_SENSORES (DATA_LEITURA, TEMPERATURA, UMIDADE, PH, FOSFORO, POTASSIO, BOMBA)
                        VALUES (TO_DATE(:1, 'YYYY-MM-DD HH24:MI:SS'), :2, :3, :4, :5, :6, :7)
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
            SELECT * FROM TBL_SENSORES
                WHERE TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') >= '{dt_inicial}' AND TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') <= '{dt_final}'
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
    def todos_os_inputs_preenchidos(dicionario):
        return bool(dicionario) and all(v is not None and v != '' for v in dicionario.values())
    menu_att = {"1":"Atualização por lote (DATA)", "2":"Atualização por ID"}
    menu_att_action = st.radio("SELECIONE A AÇÃO DE ATUALIZAÇÃO NECESSÁRIA",
            list(menu_att.values()),
            key="menu_atualizacao")
    dt_inicial = None
    dt_final = None
    
    if menu_att_action == menu_att["1"]:
        col1, col2 = st.columns(2)
        with col1:
            dt_inicial = st.text_input("Digite a data inicial de edição: ", key="dt_init_att")
        with col2:
            dt_final = st.text_input("Digite a data inicial de edição: ", key="dt_fin_att")

        df_att = pd.read_sql(f"SELECT * FROM TBL_SENSORES WHERE TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') >= '{dt_inicial}' AND TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') <= '{dt_final}'", conn)        

    if menu_att_action == menu_att["2"]:
        id_input_att = st.text_input("Digite o ID procurado: ", key="id_att")
        df_att = pd.read_sql(f"SELECT * FROM TBL_SENSORES WHERE ID = '{id_input_att}'", conn)

    if df_att.shape[0] > 0:
        st.subheader(f"Registros encontrados para edição ({len(df_att)}):")
        # st.dataframe(df_att) # Exibe o DataFrame encontrado

        COLUNAS_ATUALIZAVEIS = ['TEMPERATURA', 'UMIDADE', 'PH', 'FOSFORO', 'POTASSIO', 'BOMBA']

        # 1. Seleção dos Campos para Atualizar
        campos_selecionados = st.multiselect(
            'Selecione os campos que deseja atualizar:',
            options=COLUNAS_ATUALIZAVEIS,
            key='campos_atualizacao'
        )
        
        # 2. Criação dos Inputs Dinâmicos (SÓ PARA RENDERIZAR E ARMAZENAR NO SESSION_STATE)
        if campos_selecionados:
            st.subheader("Novos Valores (aplicados a TODOS os registros acima)")
            
            for campo in campos_selecionados:
                widget_key = f'novo_{campo}'
                
                # ... (Lógica para renderizar st.number_input, st.radio, etc. para cada campo) ...
                if campo in ['POTASSIO', "FOSFORO"]:
                    val = st.radio(f"Novo valor para {campo}:", [1, 0], key=widget_key, index=0)
                    if campo == "POTASSIO":
                        df_att["POTASSIO"] = val
                    elif campo == "FOSFORO":
                        df_att["FOSFORO"] = val
                elif campo == "UMIDADE":
                    val = st.number_input(f"Novo valor para {campo}:", key=widget_key, min_value=10, value=30)
                    df_att["UMIDADE"] = val
                elif campo == "TEMPERATURA":
                    val = st.number_input(f"Novo valor para {campo}:", key=widget_key, min_value=0.0, max_value=40.0, value=25.0)
                    df_att["TEMPERATURA"] = val
                elif campo == 'PH':
                    val = st.number_input(f"Novo valor para {campo}:", key=widget_key, min_value=0.0, max_value=14.0, step=0.1, value=7.0)
                    df_att["PH"] = val
                elif campo == 'BOMBA':
                    val = st.radio(f"Novo valor para {campo}:", ['ON', 'OFF'], key=widget_key, index=0)
                    df_att["BOMBA"] = val

                    val = 1 if val == 'ON' else 0 
                    df_att["BOMBA"] = val
                # else: 
                #     val = st.text_input(f"Novo valor para {campo}:", key=widget_key)
        
            # --- 3. Execução da Atualização (Ação Principal) ---
            if st.button("Executar Atualização"):
                sql_update_correto = "UPDATE TBL_SENSORES SET TEMPERATURA = :1, UMIDADE = :2, PH = :3, FOSFORO = :4, POTASSIO = :5, BOMBA = :6 WHERE ID = :7"

                cursor.executemany(
                    sql_update_correto, 
                    df_att[['TEMPERATURA', 'UMIDADE', 'PH', 'FOSFORO', 'POTASSIO', 'BOMBA', 'ID']].to_numpy().tolist()
                )
                st.success(f"✅ Sucesso! {len(df_att)} registro(s) foram atualizados no banco de dados.")
                conn.commit()

        st.dataframe(df_att)
elif menu_option_action == menu["4"]:
    menu_del = {"1":"Deletar dados por lote (DATA)", "2":"Deletar dados por ID"}
    menu_del_action = st.radio("SELECIONE A AÇÃO NECESSÁRIA",
            list(menu_del.values()),
            key="menu_atualizacao")
    dt_inicial = None
    dt_final = None
    
    if menu_del_action == menu_del["1"]:
        col1, col2 = st.columns(2)
        with col1:
            dt_inicial = st.text_input("Digite a data inicial de edição: ", key="dt_init_del")
        with col2:
            dt_final = st.text_input("Digite a data inicial de edição: ", key="dt_fin_del")
        df_del = pd.read_sql(f"SELECT * FROM TBL_SENSORES WHERE TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') >= '{dt_inicial}' AND TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') <= '{dt_final}'", conn)

    if menu_del_action == menu_del["2"]:
        id_input_del = st.text_input("Digite o ID procurado: ", key="id_del")
        df_del = pd.read_sql(f"SELECT * FROM TBL_SENSORES WHERE ID = '{id_input_del}'", conn)
    
    alerta_placeholder = st.empty()
    st.error("⚠️ ATENÇÃO: Confirmação Necessária!")
    st.write("Tem certeza que deseja prosseguir com esta ação, os dados serão deletados do banco para sempre?")

    if st.button("Deletar Dados"):
        st.success("Ação confirmada! Processando...")
        col_sim, col_nao = st.columns([1, 4])
        if menu_del_action == menu_del["1"]:
            cursor.execute(f"DELETE FROM TBL_SENSORES WHERE TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') >= '{dt_inicial}' AND TO_CHAR(DATA_LEITURA, 'YYYY-MM-DD') <= '{dt_final}'") 
        
        if menu_del_action == menu_del["2"]:
            cursor.execute(f"DELETE FROM TBL_SENSORES WHERE ID = '{id_input_del}'")
        conn.commit()

        st.success("Exclusão realizada com sucesso!")
        alerta_placeholder.empty()

    st.dataframe(df_del)