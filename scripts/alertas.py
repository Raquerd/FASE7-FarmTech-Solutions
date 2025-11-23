import streamlit as st
import boto3
from botocore.exceptions import ClientError

# --- CONFIGURAÇÃO AWS ---
AWS_ACCESS_KEY = "AKIA2OYRCOF4KTZJ4PGC"
AWS_SECRET_KEY = "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"
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
        return False, str(e)

