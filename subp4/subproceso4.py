from services.bd_service import obtener_cantidad_por_grupo_bd
from services.google_sheets_service import obtener_cantidad_por_grupo_googlesheet_2
from services.email_service import enviar_correo_validados, enviar_correo_pendientes
from services.dict_service import separar_resultados
from services.log_service import logger
from db.queries import QUERY_POR_GRUPO_VISTA, QUERY_POR_GRUPO_TABLA
from datetime import datetime

def ejecutar_subp4():
    logger.info("=== INICIO DEL SUBPROCESO 4: VALIDACIÓN DE GENERACIÓN DE CONSTANCIAS ===")
    try:
        # Paso 1: Obtener número de filas por grupo de la vista
        view_dict = obtener_cantidad_por_grupo_bd(QUERY_POR_GRUPO_VISTA)
        logger.info("Se obtuvo información de la vista")
        estado_validacion = {}

        # logger.info("Inicio de bucle de validación")
        # Paso 2: Obtener número de filas por grupo de la tabla
        #table_dict = obtener_cantidad_por_grupo_bd(QUERY_POR_GRUPO_TABLA)
        # Paso 2: Obtener número de filas por grupo del google sheet
        table_dict = obtener_cantidad_por_grupo_googlesheet_2()
        logger.info("Se obtuvo información del googlesheet")

        for clave, cantidad_view in view_dict.items():
            cantidad_bd = table_dict.get(clave, 0)

            if clave not in estado_validacion:
                estado_validacion[clave] = {
                    "cantidad_excel": cantidad_view,
                    "cantidad_bd": cantidad_bd,
                    "estado": "PENDIENTE",
                    "ultimo_check": datetime.now()
                }
            else:
                estado_validacion[clave]["cantidad_bd"] = cantidad_bd
                estado_validacion[clave]["ultimo_check"] = datetime.now()

        # Paso 3: Validación de ambas cantidades
            logger.info(f"Validación de oferta y grupo: {clave}")
            # Validación solo de los pendientes
            if clave in estado_validacion and estado_validacion[clave]["estado"] == "PENDIENTE":
                if cantidad_bd == cantidad_view:
                    estado_validacion[clave]["estado"] = "VALIDADO"
                    logger.info(f"Validación correcta de oferta y grupo: {clave}")
                else:
                    estado_validacion[clave]["estado"] = "PENDIENTE"
                    logger.info(f"Validación aún pendiente de oferta y grupo: {clave}")
        
        # while True:
        #     #Paso 2: Obtener número de filas por grupo de la BD
        #     bd_dict = obtener_cantidad_por_grupo_bd(QUERY_POR_GRUPO_TABLA)

        #     for clave, cantidad_view in view_dict.items():
        #         cantidad_bd = bd_dict.get(clave, 0)

        #         if clave not in estado_validacion:
        #             estado_validacion[clave] = {
        #                 "cantidad_excel": cantidad_view,
        #                 "cantidad_bd": cantidad_bd,
        #                 "estado": "PENDIENTE",
        #                 "ultimo_check": datetime.now()
        #             }
        #         else:
        #             estado_validacion[clave]["cantidad_bd"] = cantidad_bd
        #             estado_validacion[clave]["ultimo_check"] = datetime.now()

        #         # Validación
        #         if cantidad_bd == cantidad_view:
        #             estado_validacion[clave]["estado"] = "VALIDADO"
        #         else:
        #             estado_validacion[clave]["estado"] = "PENDIENTE"

        #     # Condición de salida
        #     if all(v["estado"] == "VALIDADO" for v in estado_validacion.values()):
        #         break

        logger.info("Terminó validación del día")
        validados, pendientes = separar_resultados(estado_validacion)
        # Paso 4: Enviar correo de éxito o de pendientes
        if validados:
            enviar_correo_validados(validados)
            logger.info("Se envió correos de ofertas validades correctamente")

        if pendientes:
            enviar_correo_pendientes(pendientes)
            logger.info("Se envió correos de ofertas pendientes de validar")
    except Exception as e:
        print(f"Error: {e}")
    logger.info("=== FIN DEL SUBPROCESO 4: VALIDACIÓN DE GENERACIÓN DE CONSTANCIAS ===")
