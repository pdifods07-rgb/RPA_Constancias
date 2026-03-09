from subp1.subproceso1 import ejecutar_subp1
from subp2.subproceso2 import ejecutar_subp2
from subp3.subproceso3 import ejecutar_subp3
from subp4.subproceso4 import ejecutar_subp4
from services.log_service import logger
from services.gmail_service import send_email
from db.queries import QUERY_OFERTA_GRUPO_PENDIENTES_VALIDACION
from services.bd_service import obtener_grupos_no_completados

def main():
    logger.info(f"Iniciando procesamiento ofertas")

    try:
        df_unicos = ejecutar_subp1()
        ejecutar_subp2(df_unicos)
        i = 0

        while True:
            i+=1

            if i == 1:
                ejecutar_subp3(df_unicos)
                ejecutar_subp4(df_unicos)
            else:
                ejecutar_subp4(df_unicos)

            pendientes = obtener_grupos_no_completados(QUERY_OFERTA_GRUPO_PENDIENTES_VALIDACION, df_unicos)
            if not pendientes:
                logger.info("Todos los grupos fueron completados")
                send_email()
                break

    except Exception as e:
        logger.error(f"Error: {e}")
    
    logger.info(f"Se terminó ejecución del día")

if __name__ == "__main__":
    main()