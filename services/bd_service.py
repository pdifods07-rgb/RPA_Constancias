from db.queries import QUERY_S2, QUERY_UPDATEOFERTAFORMATIVA, QUERY_INSERT_SUBP4_COMPLETADO
from db.connection import get_connection
import time
import gspread
from google.oauth2.service_account import Credentials
from config import settings

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


def ejecutar_query_simple(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    
def ejecutar_query_masiva(query, data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.fast_executemany = True
    cursor.executemany(query, data)
    conn.commit()
    cursor.close()
    conn.close()

def obtener_registros(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query)
    registros = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return registros

def insertar_subp4_completado(id_oferta, grupo, nro_constancias):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.fast_executemany = True
    cursor.execute(QUERY_INSERT_SUBP4_COMPLETADO, id_oferta, grupo, nro_constancias)

    conn.commit()
    cursor.close()
    conn.close()

def insertar_registros(query, id_oferta, grupo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query, id_oferta, grupo)

    conn.commit()
    cursor.close()
    conn.close()

def obtener_subp4_completados(query):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(query)

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return [(row.id_oferta, row.grupo) for row in resultados]

def obtener_cantidad_por_grupo_bd(query, registros):
    conn = get_connection()
    cursor = conn.cursor()

    # Construir (?, ?), (?, ?), ...
    placeholders = ",".join(["(?, ?)"] * len(registros))

    # Insertar dinámicamente los placeholders en la query
    nueva_query = query.format(valores=placeholders)

    # Aplanar lista de tuplas
    params = [item for tupla in registros for item in tupla]

    cursor.execute(nueva_query, params)
    resultados = cursor.fetchall()
    cursor.close()

    return {
        (row[0], row[1]): row[2]
        for row in resultados
    }

def obtener_grupos_no_completados(query, df_unicos):
    conn = get_connection()
    cursor = conn.cursor()
    
    pares = list(df_unicos[['ID_OFERTA_FORMATIVA','NOMBRE_GRUPO']].itertuples(index=False, name=None))

    if not pares:
        return []

    # construir (?, ?), (?, ?), ...
    placeholders = ",".join(["(?, ?)"] * len(pares))

    # insertar placeholders en la query
    nueva_query = query.format(valores=placeholders)

    # aplanar parametros
    params = [item for tupla in pares for item in tupla]

    cursor = conn.cursor()
    cursor.execute(nueva_query, params)

    rows = cursor.fetchall()
    cursor.close()

    return [(r[0], r[1]) for r in rows]