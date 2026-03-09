from services.error_service import map_exception
from services.log_service import logger
from services.bd_service import ejecutar_query_masiva
import pandas as pd
from config import settings
import os
from db import queries, connection


def ejecutar_subp1():
    try:
        # =========================
        # EJECUTAR CONSULTA
        # =========================
        conn = connection.get_connection()
        df = pd.read_sql(queries.consulta, conn)
        conn.close()

        # -------------------------------------------------------------------------
        # OBTENER OFERTAS Y GRUPOS UNICOS E INSERTARLOS EN TABLA, ANTES DEL PASO 1
        # -------------------------------------------------------------------------
        df_unicos = df[["ID_OFERTA_FORMATIVA", "NOMBRE_GRUPO"]].drop_duplicates()

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 1,1)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(queries.QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)

        # Forzar columnas como texto (evita perder ceros iniciales)
        df["tipoDocumento"] = df["tipoDocumento"].astype(str)
        df["numeroDocumento"] = df["numeroDocumento"].astype(str)

        print("Consulta ejecutada correctamente")

        # -------------------------------------------------------
        # LUEGO DEL PASO 1
        # -------------------------------------------------------
        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 1,2)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(queries.QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)

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

        # -------------------------------------------------------
        # LUEGO DEL PASO N
        # -------------------------------------------------------
        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 1,3)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(queries.QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)
        return df_unicos
    except Exception as e:
        error_info = map_exception(e)

        logger.info(str(e))

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 1, 4, error_info["id"])
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(queries.QUERY_INSERTAR_ERROR, registros)

        raise