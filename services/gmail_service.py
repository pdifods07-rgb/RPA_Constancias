import os.path
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from config import settings
from services.bd_service import obtener_subp4_completados
from db.queries import QUERY_OBTENER_SUBP4_COMPLETADOS

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "enviarcorreo.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    return service

def send_email():
    service = get_gmail_service()

    # Obtener información de las ofertas y grupos completados
    completados = obtener_subp4_completados(QUERY_OBTENER_SUBP4_COMPLETADOS)

    lineas = []

    for oferta, grupo in completados:
        lineas.append(f"Oferta {oferta} - Grupo {grupo}")

    texto = "\n".join(lineas)

    cuerpo = (
    "Se completó la generación y validación de constancias para las siguientes ofertas y grupos:\n\n"
    f"{texto}\n\n"
    )

    # Armar asunto
    fecha_ejecucion = datetime.now().strftime("%d/%m/%Y")
    asunto = f"Ofertas Validadas Exitosamente - {fecha_ejecucion}"

    message = MIMEText(cuerpo, "plain")

    message["to"] = ", ".join(settings.EMAIL_DESTINATARIOS)
    message["subject"] = asunto

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    message_body = {
        "raw": raw_message
    }

    service.users().messages().send(
        userId="me",
        body=message_body
    ).execute()

    print("Correo enviado")