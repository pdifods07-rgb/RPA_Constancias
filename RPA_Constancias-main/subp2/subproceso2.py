from services.bd_service import *
from services.google_sheets_service import obtener_ofertas_desde_google_sheet
from services.dict_service import comparar_ofertas
from services.error_service import map_exception
from services.log_service import logger

def ejecutar_subp2(df_unicos, modo_prueba=False):
    try:
        # -------------------------------------------------------------------------
        # OBTENER OFERTAS Y GRUPOS UNICOS E INSERTARLOS EN TABLA, ANTES DEL PASO 1
        # -------------------------------------------------------------------------
        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 2, 1)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)

        if modo_prueba:
            print("Ejecutando en modo prueba")

        # Paso 1: Ejecutar Query de Ofertas Formativas
        # Nombre Oferta, Horas Lectivas, Tipo Oferta Formativa, Periodo
        ofertas_bd = obtener_ofertas_desde_bd()
        print("✔ Paso 1 OK")

        # -------------------------------------------------------
        # LUEGO DEL PASO 1
        # -------------------------------------------------------
        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 2, 2)
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_REGISTRO_TABLA_HISTORICA, registros)

        # Paso 2: Obtener información del Google Sheet con información de aulas virtuales
        # Nombre Oferta, Horas Lectivas, Tipo Oferta Formativa, Periodo
        ofertas_sheet = obtener_ofertas_desde_google_sheet()
        print("✔ Paso 2 OK")

        #validar actualizacion de datos
        print(f"Total registros BD: {len(ofertas_bd)}")
        print(f"Total registros Sheet: {len(ofertas_sheet)}")

        # Paso 3: Comparar información de la Oferta Formativa de BD y Google Sheet
        cambios = comparar_ofertas(ofertas_bd, ofertas_sheet)
        print("✔ Paso 3 OK")

        # -------------------------------------------------------
        # LUEGO DEL PASO N
        # -------------------------------------------------------
        registros_1 = [ # diccionario con la información de las ofertas y grupos
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO)
            for row in df_unicos.itertuples(index=False)
        ]

        for oferta, grupo in registros_1:
            valido = 0
            #valido = validar_regla(oferta) (BOOLEANO RESULTADO DE LA FUNCIÓN DE EVALUACIÓN DE LA OFERTA)
            if valido == 0: # solo valido
                insertar_registros(QUERY_INSERT_SUBP2_COMPLETADO, oferta, grupo)
            else:
                insertar_registros(QUERY_INSERT_SUBP2_ERROR, oferta, grupo)
        
        if not modo_prueba:
            # Paso 4: Actualizar información en caso no coincida la información de la Oferta
            ejecutar_updates(cambios)
        else:
            print("Cambios detectados:", cambios)

    except Exception as e:
        print(f"Error durante la ejecución: {e}")

        error_info = map_exception(e)

        registros = [
            (row.ID_OFERTA_FORMATIVA, row.NOMBRE_GRUPO, 2, 4, error_info["id"])
            for row in df_unicos.itertuples(index=False)
        ]

        ejecutar_query_masiva(QUERY_INSERTAR_ERROR, registros)
        logger.info(str(e))

        raise