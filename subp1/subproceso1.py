import pandas as pd
from db import queries, connection
from config import settings
import os

def ejecutar_subp1():
    # =========================
    # EJECUTAR CONSULTA
    # =========================
    conn = connection.get_connection()
    df = pd.read_sql(queries.consulta, conn)
    conn.close()

    # Forzar columnas como texto (evita perder ceros iniciales)
    df["tipoDocumento"] = df["tipoDocumento"].astype(str)
    df["numeroDocumento"] = df["numeroDocumento"].astype(str)

    print("Consulta ejecutada correctamente")

    # =====================================
    # CREAR CARPETAS (SI ES QUE NO EXISTEN)
    # =====================================
    os.makedirs(settings.carpeta_entrada, exist_ok=True)
    os.makedirs(settings.carpeta_salida, exist_ok=True)

    # =========================
    # GENERAR EXCEL BASE
    # =========================
    archivo_generado = os.path.join(settings.carpeta_entrada, settings.excel_insumo)
    df.to_excel(archivo_generado, index=False)

    print("Excel base generado en carpeta 'input' del subp1")

    # =========================
    # PROCESO DE SEPARACIÓN
    # =========================
    for (id_oferta, nombre_grupo), grupo in df.groupby(["ID_OFERTA_FORMATIVA", "NOMBRE_GRUPO"]):
        df_filtrado = grupo[["tipoDocumento", "numeroDocumento"]]
        
        # Limpiar caracteres inválidos
        nombre_grupo_limpio = (
            str(nombre_grupo)
            .replace("/", "-")
            .replace("\\", "-")
            .replace(":", "-")
            .strip()
        )
        
        nombre_archivo = os.path.join(
            settings.carpeta_salida,
            f"{id_oferta}-{nombre_grupo_limpio}.xlsx"
        )
        
        df_filtrado.to_excel(nombre_archivo, index=False)

    print("Archivos separados generados correctamente en carpeta 'output' del subp1")
    print("Proceso finalizado")