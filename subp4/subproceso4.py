from services.log_service import logger
from services.bd_service import *
from db.queries import *
from services.error_service import map_exception
from services.google_sheets_service import obtener_cantidad_por_grupo_googlesheet_2

def ejecutar_subp4(df_unicos):

    try:
        logger.info("=== INICIO SUBPROCESO 4 ===")

        # 1️⃣ Crear subp4 pendientes desde subp3 completados
        ejecutar_query_simple(QUERY_CREAR_SUBP4_PENDIENTE)

        # 2️⃣ Obtener pendientes reales
        pendientes = obtener_registros(QUERY_OBTENER_SUBP4_PENDIENTES)

        if not pendientes:
            logger.info("No hay pendientes para validar")
            return
        
        # 3️⃣ Obtener datos externos
        view_dict = obtener_cantidad_por_grupo_bd(QUERY_POR_GRUPO_VISTA, pendientes)
        sheet_dict = obtener_cantidad_por_grupo_googlesheet_2(pendientes) 

        # 4️⃣  Pasarlos a EN_EJECUCION
        valores_insert = []

        for oferta, grupo in pendientes:
            nro = sheet_dict.get((oferta, grupo), 0)
            valores_insert.append((oferta, grupo, nro))

        if valores_insert:
            ejecutar_query_masiva(QUERY_CREAR_SUBP4_EN_EJECUCION, valores_insert)

        # 5️⃣ Obtener los que ahora están en ejecución
        en_ejecucion = obtener_registros(QUERY_OBTENER_SUBP4_EN_EJECUCION)

        # 6️⃣ Validar
        for oferta, grupo in en_ejecucion:
            cantidad_view = view_dict.get((oferta, grupo), 0)
            cantidad_sheet = sheet_dict.get((oferta, grupo), 0)

            if cantidad_view == cantidad_sheet:
                insertar_subp4_completado(oferta, grupo, cantidad_sheet)
                logger.info(f"Validado {oferta} - {grupo}")
            else:
                insertar_registros(QUERY_INSERTAR_PENDIENTE, oferta, grupo)
                logger.warning(
                f"Reintento {oferta} - {grupo} "
                f"(sheet = {cantidad_sheet}, view = {cantidad_view})"
                )

        logger.info("=== FIN SUBPROCESO 4 ===")
    except Exception as e:
        error_info = map_exception(e)

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 4, 4, error_info["id"])
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_ERROR, registros)

        logger.info(str(e))

        raise