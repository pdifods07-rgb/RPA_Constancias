import win32com.client as win32
from config import settings
from datetime import datetime

def enviar_correo_outlook(asunto, cuerpo_html, destinatarios):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    mail.Subject = asunto
    mail.HTMLBody = cuerpo_html
    mail.To = ";".join(destinatarios)

    mail.Send()  # O usar .Display() si quieres verlo antes

def enviar_correo_validados(validados):

    lista_html = "".join(
        f"<li>Oferta {id_oferta} - {grupo}</li>"
        for id_oferta, grupo in validados
    )

    cuerpo = f"""
    <h3>Estimados,</h3>
    <p>Las siguientes ofertas y grupos fueron validadas correctamente:</p>
    <ul>
        {lista_html}
    </ul>
    """

    fecha_ejecucion = datetime.now().strftime("%d/%m/%Y")

    asunto = f"Ofertas Validadas Exitosamente - {fecha_ejecucion}"

    enviar_correo_outlook(
        asunto = asunto,
        cuerpo_html = cuerpo,
        destinatarios = settings.EMAIL_DESTINATARIOS
    )

def enviar_correo_pendientes(pendientes):

    lista_html = "".join(
        f"<li>Oferta {id_oferta} - {grupo}</li>"
        for id_oferta, grupo in pendientes
    )

    cuerpo = f"""
    <h3>Estimados,</h3>
    <p>Las siguientes ofertas y grupos aún están pendientes de validación:</p>
    <ul>
        {lista_html}
    </ul>
    """

    fecha_ejecucion = datetime.now().strftime("%d/%m/%Y")

    asunto = f"Ofertas Pendientes de Validación - {fecha_ejecucion}"

    enviar_correo_outlook(
        asunto = asunto,
        cuerpo_html = cuerpo,
        destinatarios = settings.EMAIL_DESTINATARIOS
    )
