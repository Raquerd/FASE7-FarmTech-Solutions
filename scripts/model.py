import pandas as pd, json, os, requests, oracledb, time
from datetime import datetime

conn = oracledb.connect(user='rm562274', password='090402', dsn='oracle.fiap.com.br:1521/ORCL') 
cursor = conn.cursor()

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

while True:
    os.system('cls')
    previsao_tempo(url)
    menu_option = int(input(f'''{'-'*15}
Seleciona a ação que deseja realizar

[1] Inserir dados
[2] Consultar dados cadastrados
[3] Atualizar dados cadastrados
[4] Excluir dados cadastrados
[5] Sair
{'-'*15}
R: '''))
    try:
        match menu_option:
            ## --------------------------------1------------------------------------------- ##
            case 1:
                os.system('cls')
                menu_1 = int(input('Qual seria a forma de inserção de dados?\n[1]-Em lote(csv)\n[2]-Manualmente'))
                if menu_1 == 1:
                    path = input('Digite o caminho onde o arquivo está salvo.')
                    df_dados_importados = pd.read_csv(rf'{path}', sep=',')
                    
                    cursor.executemany('''
                    INSERT 
                        INTO SENSORES (
                            TIME, UMIDADE, PH, FOSFORO, POTASSIO, BOMBA
                        )
                    VALUES (
                    :1, :2, :3, :4, :5, :6
                    )''', df_dados_importados.to_numpy().tolist())
                    conn.commit()
                    
                if menu_1 == 2:
                    while True:
                        try:
                            umidade = int(input('Umidade: '))
                            ph = int(input('PH: '))
                            fosforo = input('Fosforo: ')
                            potassio = int(input('Potassio: '))
                            bomba = input('RELÉ ON ou OFF?: ')
                            bomba = bomba.upper()
                            os.system('cls')

                            if bomba not in ['ON','OFF']:
                                raise ValueError('O Valor da bomba está errado, apenas os valores ON e OFF são compativeis.')
                            
                            inserir_dado_manual(umidade, ph, fosforo, potassio, bomba)
                        except Exception as e:
                            print(f'Erro:{e}')
                            
                        option_1 = int(input('Deseja inserir mais algum dado?:\n1-SIM\n2-NÃO\nR: '))
                        if option_1 == 1:
                            continue
                        elif option_1 == 2:
                            break
                        else:
                            os.system('cls')
                            input('OPÇÃO INVALIDA: Pressione enter para voltar ao MENU')
                else:
                    os.system('cls')
                    input('OPÇÃO INVALIDA: Pressione enter para voltar ao MENU')
            ## --------------------------------------------------------------------------- ##

            case 2:
                os.system('cls')
                try:
                    option_2 = int(input('Deseja fazer a consulta com um range de data?\n1-SIM\n2-NÃO\nR: '))
                    if  option_2 == 1:
                        date = input('Digite o ano-mês de extraçã: ')
                        df = listar_dados(date, True)
                    else:
                        df = listar_dados()
                    os.system('cls')
                    print(df)
                    option_2_extract = int(input('Deseja extrair os dados\n1-SIM\n2-NÃO\nR: '))
                    if option_2_extract == 1:
                        path = input('Digite o caminho onde deseja salvar o arquivo:')
                        df.to_excel(rf'{path}/extração_dados_sensores.xlsx', index=False)
                    elif 2:
                        input('Aperte enter para voltar ao MENU')
                    
                ## Armazena os dados de cadastro em formato de dicionário
                except Exception as e:
                    os.system('cls')
                    print(f'ERRO: {e}')
                    time.sleep(2)
            ## --------------------------------------------------------------------------- ##
            case 3:
                try:
                    id = input('Digite o ID que deseja atualizar: ')
                    campo = input('Digite qual campo deseja alterar: ')
                    valor = input('Digite o valor que deseja atribuir ao campo: ')
                    if campo.upper() in ['PH', 'FOSFORO', 'POTASSIO']:
                        valor = int(valor)
                    elif campo.upper() == 'UMIDADE':
                        valor = float(valor)
                         
                    atualizar_dado_manual(id, campo, valor)

                except Exception as e:
                    os.system('cls')
                    print(f'ERRO: {e}\nO preenchimento foi feito de forma inadequada\nVerifique os dados que estão sendo alterados e se os mesmo correspondem ao campo')
                    time.sleep(2)
            ## --------------------------------------------------------------------------- ##
            case 4:
                os.system('cls')
                try:

                ## Captura o ID que o usuário deseja limpar
                    id = int(input("Digite o ID que deseja eliminar do banco de dados: "))
                    deletar_dado(id)
                except:
                    print('Algo deu errado!')
                    time.sleep(3)
                    continue
                os.system('cls')
                input(f'O id {id} foi eliminado do banco de dados')
            ## --------------------------------------------------------------------------- ##
            case 5:
                conn.close()
                exit()

    except Exception as error:
        os.system('cls')
        print(f'ERRO: {error}')
            
            