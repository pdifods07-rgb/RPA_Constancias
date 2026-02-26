from services.bd_service import obtener_ofertas_desde_bd, ejecutar_updates
from services.google_sheets_service import obtener_ofertas_desde_google_sheet
from services.dict_service import comparar_ofertas

def ejecutar_subp2(modo_prueba=False):
    try:
        if modo_prueba:
            print("Ejecutando en modo prueba")

        # Paso 1: Ejecutar Query de Ofertas Formativas
        # Nombre Oferta, Horas Lectivas, Tipo Oferta Formativa, Periodo
        ofertas_bd = obtener_ofertas_desde_bd()
        print("✔ Paso 1 OK")

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
        if not modo_prueba:
            # Paso 4: Actualizar información en caso no coincida la información de la Oferta
            ejecutar_updates(cambios)
        else:
            print("Cambios detectados:", cambios)

    except Exception as e:
        print(f"Error durante la ejecución: {e}")