import gspread
from google.oauth2.service_account import Credentials
from config import settings

def obtener_ofertas_desde_google_sheet():
    
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH)
    credentials = credentials.with_scopes(SCOPES)

    client = gspread.authorize(credentials)

    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
    worksheet = sheet.worksheet(settings.GOOGLE_SHEET_NAME)
    registros = worksheet.get_all_records()

    # Validar que las columnas necesarias existan
    columnas_requeridas = ["IdOferta","NombreOferta", "Horas", "TipoOferta", "Periodo"]

    for col in columnas_requeridas:
        if col not in registros[0]:
            raise Exception(f"La columna '{col}' no existe en el Google Sheet")

    # Normalizar formato (mismo esquema que BD)
    resultados = []

    for row in registros:
        fila = {
            "IdOferta": str(row["IdOferta"]).strip(),
            "NombreOferta": str(row["NombreOferta"]).strip(),
            "Horas": int(row["Horas"]),
            "TipoOferta": str(row["TipoOferta"]).strip(),
            "Periodo": str(row["Periodo"]).strip()
        }

        resultados.append(fila)

    return resultados

def obtener_cantidad_por_grupo_googlesheet_2():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH_2)
    credentials = credentials.with_scopes(SCOPES)
    client = gspread.authorize(credentials)

    sheet = client.open_by_key(settings.GOOGLE_SHEET_ID_2)
    worksheet = sheet.worksheet(settings.GOOGLE_SHEET_NAME_2)
    registros = worksheet.get_all_records()

    if not registros:
        return {}

    # Validar que las columnas necesarias existan
    columnas_requeridas = ["OFERTA","GRUPO", "NRO_CONSTANCIAS"]

    for col in columnas_requeridas:
        if col not in registros[0]:
            raise Exception(f"La columna '{col}' no existe en el Google Sheet")

    # Normalizar formato (mismo esquema que BD)
    resultados = {}

    for row in registros:
        oferta = int(row["OFERTA"])
        grupo = str(row["GRUPO"]).strip()
        nro = int(row["NRO_CONSTANCIAS"])

        clave = (oferta, grupo)

        if clave not in resultados:
            resultados[clave] = nro
        else:
            resultados[clave] += nro

    return resultados