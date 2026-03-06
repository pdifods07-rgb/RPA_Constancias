import pyodbc
from config import settings

def get_connection():
    try:
        conexion = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings.server};"
            f"DATABASE={settings.database};"
            "Trusted_Connection=yes;"
        )
        print("✅ Conexión exitosa a SQL Server")
        return conexion

    except Exception as e:
        print("❌ Error de conexión:", e)
        exit()