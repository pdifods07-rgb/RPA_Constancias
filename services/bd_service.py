from db.queries import QUERY_S2, QUERY_UPDATEOFERTAFORMATIVA
from db.connection import get_connection
import time

def obtener_ofertas_desde_bd():
    #NEW
    inicio = time.perf_counter()
    #new

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(QUERY_S2)

    columnas = [column[0] for column in cursor.description]

    resultados = []

    for row in cursor.fetchall():
        fila_dict = dict(zip(columnas, row))
        resultados.append(fila_dict)

    cursor.close()
    conn.close()

    fin = time.perf_counter()

    print(f"⏳ Tiempo de ejecución QUERY_S2: {fin - inicio:.2f} segundos")
    print(f"📊 Total registros obtenidos: {len(resultados)}")

    if resultados:
        print("🔎 Primer registro:")
        print(resultados[0])

    return resultados

def ejecutar_updates(cambios):

    if not cambios:
        print("No hay diferencias. No se ejecutan updates.")
        return

    conn = get_connection()
    cursor = conn.cursor()

    for row in cambios:
        cursor.execute(
            QUERY_UPDATEOFERTAFORMATIVA,
            str(row["NombreOferta"]).strip(),
            int(row["Horas"]),
            str(row["TipoOferta"]).strip(),
            str(row["Periodo"]).strip(),
            int(row["IdOferta"])
        )

    conn.commit()
    cursor.close()

    print(f"{len(cambios)} ofertas actualizadas correctamente.")


def obtener_cantidad_por_grupo_bd(QUERY):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(QUERY)

    resultado = {}

    for row in cursor.fetchall():
        resultado[(int(row.id_oferta), str(row.grupo))] = int(row.numero_constancias or 0)

    cursor.close()

    return resultado