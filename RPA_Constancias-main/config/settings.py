# ============================================================
# BASE DE DATOS
# ============================================================
# Autenticación de SQL Server (Usuario y Pass)
server = "PCPOPRDIFOD132"
database = "db_automatizacion"

# Autenticación de Windows (sin pass), 
# cambiar connection string a Trusted_Connection=yes

# ============================================================
# GOOGLE DRIVE
# ============================================================
# ID del Google Sheet
GOOGLE_SHEET_ID = "1WPLOmxJJ-VAEzMtAfTlkQBLapWq120ikF-H_tQEAtGk"
# Nombre de la hoja
GOOGLE_SHEET_NAME = "DATOS_CARD"
# Ruta al archivo de credenciales JSON
GOOGLE_CREDENTIALS_PATH = "credenciales.json"

# ============================================================
# CARPETAS Y ARCHIVOS
# ============================================================
carpeta_entrada = "subp1/input"
carpeta_salida = "subp1/output"
excel_insumo = "consulta_generada.xlsx"



# ============================================================
# OUTLOOK
# ============================================================
# Destinatarios
EMAIL_DESTINATARIOS = ["DIFODSTI015@minedu.gob.pe"]

# ============================================================
# GOOGLE DRIVE
# ============================================================
# ID del Google Sheet
GOOGLE_SHEET_ID_2 = "1o7UElkWd27693x_PeVNQUsbSl_gteEFjd3NYo6ATltk"
# Nombre de la hoja
GOOGLE_SHEET_NAME_2 = "Hoja 1"
# Ruta al archivo de credenciales JSON
GOOGLE_CREDENTIALS_PATH_2 = "validaciongeneracionconstancias.json"