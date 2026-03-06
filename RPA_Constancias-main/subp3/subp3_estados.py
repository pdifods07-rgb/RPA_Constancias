from services.bd_service import *
from services.error_service import map_exception
from services.log_service import logger

def ejecutar(df_unicos):
    try:
        # -------------------------------------------------------------------------
        # OBTENER OFERTAS Y GRUPOS UNICOS E INSERTARLOS EN TABLA, ANTES DEL PASO 1
        # -------------------------------------------------------------------------
        # df_unicos (debe ser global para todo - ¿Paso 0?)

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 3,1)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)

        # -------------------------------------------------------
        # LUEGO DEL PASO 1
        # -------------------------------------------------------
        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 3,2)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)

        # -------------------------------------------------------
        # LUEGO DEL PASO N
        # -------------------------------------------------------
        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 3,3)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)
    except Exception as e:
        error_info = map_exception(e)

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 3, 4, error_info["id"])
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_ERROR, registros)

        logger.info(str(e))

        raise