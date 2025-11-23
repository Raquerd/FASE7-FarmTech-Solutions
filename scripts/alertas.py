import boto3, pandas as pd
import os
from botocore.exceptions import ClientError
# from dotenv import load_dotenv 

# load_dotenv()

# --- CONFIGURAÇÃO AWS ---
AWS_ACCESS_KEY = pd.read_csv(r"C:\Users\Davi\Documents\Projetos\FIAP\FASE 7\Capitulo 1\config\BotPythonFazenda_accessKeys.csv")['Access key ID'].values[0]
AWS_SECRET_KEY = pd.read_csv(r"C:\Users\Davi\Documents\Projetos\FIAP\FASE 7\Capitulo 1\config\BotPythonFazenda_accessKeys.csv")['Secret access key'].values[0]
AWS_REGION = "us-west-1" 
SNS_TOPIC_ARN = "arn:aws:sns:us-west-1:718905962872:AlertaFazenda"
def enviar_alerta_sns(mensagem, assunto="Alerta Fazenda"):
    """
    Envia a mensagem para o tópico SNS configurado.
    """
    client = boto3.client(
        "sns",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    try:
        response = client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensagem,
            Subject=assunto
        )
        return True, response['MessageId']
    except ClientError as e:
        print(f"Erro AWS: {e}") 
        return False, str(e)