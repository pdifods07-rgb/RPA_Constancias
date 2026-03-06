from playwright.sync_api import sync_playwright, TimeoutError as ErrorTimeout
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
from pathlib import Path

import pandas as pd

import pyodbc

# 🔹 Cadena de conexión con Windows Authentication
conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=PCPOPRDIFOD132;"          # Cambia por tu servidor
    "DATABASE=db_automatizacion;"     # Cambia por tu base
    "Trusted_Connection=yes;"
)

query_constancias_pendientes = """
SELECT 
TIPO_REGISTRO
,ID_OFERTA_FORMATIVA
,ID_PARTICIPANTE
,ID_CONSTANCIA
,ID_TIPO_DOCUMENTO
,USUARIO_DOCUMENTO
,NOMBRE_GRUPO
,F_DESARROLLO_FIN
,NOMBRE_OFERTA
,CODIGO
,HORAS_LECTIVAS
,NOMBRE_TIPO_OFERTA
,NOMBRE_PERIODO
FROM [dbo].[tb_pendientes_constancia_2026]
"""

query_memorandum = """
SELECT 
ID
,MEMORANDUM
,FECHA_INICIO
,FECHA_FIN
FROM [dbo].[memorando_constancia-prueba]
"""

query_parametros = """
SELECT 
	CAST(A.ID_OFERTA_FORMATIVA AS VARCHAR(50))  AS ID_OFERTA_FORMATIVA,
	CAST(A.ID_GRUPO AS VARCHAR(50)) AS ID_GRUPO_PARAMETRO,
	A.CODIGO_OFERTA_FORMATIVA
FROM (
	SELECT DISTINCT 
		p.ID_OFERTA_FORMATIVA,
		g.ID_GRUPO,
		p.CODIGO AS CODIGO_OFERTA_FORMATIVA
	FROM [dbo].[tb_pendientes_constancia_2026] p
	CROSS JOIN (
		VALUES (163), (164)
) AS g(ID_GRUPO)
) A 
left join [dbo].[parametros] p 
on p.ID_PADRE is not  null and P.CODIgo = a.ID_OFERTA_FORMATIVA AND P.ID_GRUPO=A.ID_GRUPO
WHERE P.ID IS NULL
"""

DOMAIN = "https://sifods-cap.minedu.gob.pe/"

URL_LOGIN = f"{DOMAIN}/login"

URL_ADM_PARAMETROS = f"{DOMAIN}/admin/acciones-formativas-opciones"



df_constancias_pendientes = pd.read_sql(query_constancias_pendientes, conexion,
    dtype={
        "ID_OFERTA_FORMATIVA": str,
        "CODIGO": str,
        "USUARIO_DOCUMENTO": str
    })

df_memorandum = pd.read_sql(query_memorandum, conexion)

df_parametro = pd.read_sql(query_parametros, conexion,dtype=str)

#Extrayendo insumos requeridos.
df_constancias_pendientes["OF_GRUPO"] = (
    df_constancias_pendientes["ID_OFERTA_FORMATIVA"].astype(str) + "-" +
    df_constancias_pendientes["NOMBRE_GRUPO"].astype(str)
)

df_constancias = df_constancias_pendientes[
    ["TIPO_REGISTRO","ID_OFERTA_FORMATIVA", "NOMBRE_GRUPO", "OF_GRUPO", "CODIGO"]
].drop_duplicates()


#print(df_constancias_pendientes)
print(df_constancias)


#Extraer memorandum
df_memorandum["FECHA_INICIO"] = pd.to_datetime(df_memorandum["FECHA_INICIO"])
df_memorandum["FECHA_FIN"] = pd.to_datetime(df_memorandum["FECHA_FIN"])

hoy = pd.Timestamp.today().normalize()

df_memorandum_vigente = df_memorandum[
    (df_memorandum["FECHA_INICIO"] <= hoy) &
    (df_memorandum["FECHA_FIN"] >= hoy)
]
memorandum = df_memorandum.iloc[0]["MEMORANDUM"]

print(df_memorandum.head())
print(df_memorandum_vigente)
print(memorandum)



#Extraer parámetros pendientes

print(df_parametro)

conexion.close()



# ⚠️ AJUSTAR SELECTORES SEGÚN EL HTML REAL
SELECTORES = {
    "usuario": 'input[name="documentoIdentidad"]',
    "contrasena": 'input[name="password"]',
    #"captcha": 'input[name="captcha"]',
    "boton_login": 'button[type="submit"]'
}


def solicitar_captcha():
    """
    Muestra una ventana emergente para que el usuario
    ingrese el captcha recibido por correo.
    """
    ventana = tk.Tk()
    ventana.withdraw()

    captcha = simpledialog.askstring(
        "Ingreso de CAPTCHA",
        "Ingrese el CAPTCHA recibido por correo:"
    )

    ventana.destroy()
    return (captcha or "").strip()


def llenar_formulario_login(pagina, usuario, contrasena):
    """
    Llena los campos del formulario de login
    """
    pagina.wait_for_selector(SELECTORES["usuario"], timeout=30000)
    pagina.wait_for_selector(SELECTORES["contrasena"], timeout=30000)
    #pagina.wait_for_selector(SELECTORES["captcha"], timeout=30000)

    pagina.fill(SELECTORES["usuario"], usuario)
    pagina.fill(SELECTORES["contrasena"], contrasena)
    #pagina.fill(SELECTORES["captcha"], captcha)

    pagina.click(SELECTORES["boton_login"])



def ejecutar_subp3():

    usuario = "72119474"
    contrasena = "Minedu2026$"

    with sync_playwright() as p:

        navegador = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        contexto = navegador.new_context(no_viewport=True)
        pagina = contexto.new_page()

        pagina.goto(URL_LOGIN, timeout=60000)
        pagina.wait_for_load_state("networkidle")

        print("Página cargada correctamente")

        """ captcha = solicitar_captcha()

        if not captcha:
            messagebox.showwarning(
                "CAPTCHA",
                "No ingresó captcha. Cancelando proceso."
            )
            return """

        try:
            print("Llenando datos")
            llenar_formulario_login(
                pagina,
                usuario,
                contrasena
            )
            pagina.wait_for_load_state("networkidle")

        except ErrorTimeout:
            print("⏳ Timeout en login")
            pagina.reload()
            pagina.wait_for_load_state("networkidle")

        print("Proceso finalizado. Cerrando en 5 segundos...")
        pagina.wait_for_timeout(10000)

        print("Iniciando procesamiento de ofertas...")

        #VALIDAR SI SE TIENE QUE IR A PARÁMETROS

        for index, row in df_parametro.iterrows():
            
            idGrupoParametro = row["ID_GRUPO_PARAMETRO"]
            #IR A PARAMETROS
            pagina.goto(URL_ADM_PARAMETROS, timeout=60000)
            descripcion = f"{row["CODIGO_OFERTA_FORMATIVA"]} ({row["ID_OFERTA_FORMATIVA"]})"

            if idGrupoParametro == '163':
                #163
                
                pagina.query_selector("nb-select").click()
                pagina.wait_for_selector("nb-option")
                pagina.query_selector("nb-option:has-text('Configuracion de detalle de evaluacion final para generar constancia')").click()


                pagina.wait_for_selector("button:has-text('Nuevo')")
                pagina.query_selector("button:has-text('Nuevo')").click()

                input_valor = pagina.query_selector("input[formcontrolname='valor']")
                input_valor.fill("Por haber aprobado el:")

                input_descripcion = pagina.query_selector("input[formcontrolname='descripcion']")
                input_descripcion.fill(f"{descripcion}")

                input_cod_oferta = pagina.query_selector("input[formcontrolname='codigo']")
                input_cod_oferta.fill(f"{row["ID_OFERTA_FORMATIVA"]}")

                # Aceptar
                pagina.wait_for_selector("button:has-text('Aceptar')")
                pagina.query_selector("button:has-text('Aceptar')").click()
                pagina.wait_for_timeout(5000) 

                # Esperar que aparezca el modal
                pagina.wait_for_selector("nb-card")
                botones = pagina.query_selector_all("button:has-text('Aceptar')")
                botones[-1].click()

                pagina.wait_for_timeout(10000) 

            elif idGrupoParametro == '164':
                #164
                pagina.query_selector("nb-select").click()
                pagina.wait_for_selector("nb-option")
                pagina.query_selector("nb-option:has-text('Configuracion de fecha de desarrollo para generar constancia')").click()
                pagina.wait_for_timeout(5000)

                pagina.wait_for_selector("button:has-text('Nuevo')")
                pagina.query_selector("button:has-text('Nuevo')").click()

                input_valor = pagina.query_selector("input[formcontrolname='valor']")
                input_valor.fill("Desarrollado desde el {INI_DIA} de {INI_MES} hasta el {FIN_DIA} de {FIN_MES} del {FIN_ANIO}, con un total de {HORAS} horas.")

                input_descripcion = pagina.query_selector("input[formcontrolname='descripcion']")
                input_descripcion.fill(f"{descripcion}")

                input_cod_oferta = pagina.query_selector("input[formcontrolname='codigo']")
                input_cod_oferta.fill(f"{row["ID_OFERTA_FORMATIVA"]}")

                # Aceptar
                pagina.wait_for_selector("button:has-text('Aceptar')")
                pagina.query_selector("button:has-text('Aceptar')").click()
                pagina.wait_for_timeout(5000) 

                # Esperar que aparezca el modal
                pagina.wait_for_selector("nb-card")
                botones = pagina.query_selector_all("button:has-text('Aceptar')")
                botones[-1].click()

                pagina.wait_for_timeout(10000)

        for _, fila in df_constancias.iterrows():
            idOferta = int(fila["ID_OFERTA_FORMATIVA"])
            grupo = str(fila["NOMBRE_GRUPO"]).strip()
            fechaGeneracion = datetime.now().strftime("%d/%m/%Y")
             #str(fila_excel["TipoConstancia"])
            if fila["TIPO_REGISTRO"] == 'CURSO':
                tipoConstancia = "Curso"
            elif fila["TIPO_REGISTRO"] == 'PROGRAMA':
                tipoConstancia = f"{fila["CODIGO"]}-{fila["ID_OFERTA_FORMATIVA"]}" 

            

            URLOFERTA = f"{DOMAIN}/dash/mantenimiento/oferta-formativa/disenar/{idOferta}"

            pagina.goto(URLOFERTA, timeout=60000)
            pagina.wait_for_load_state("domcontentloaded")

            pagina.wait_for_selector(
                "app-disenar-oferta-formativa table",
                timeout=30000
            )

            """ tabla = pagina.query_selector(
                "app-disenar-oferta-formativa table"
            ) """

            tabla = (
                pagina
                .query_selector("nb-card-body")
                .query_selector_all(":scope > .row")[2]
                .query_selector_all(":scope > .col-sm-12")[1]
                .query_selector("table")
            )

            filas = tabla.query_selector_all(
                "tr.ng-star-inserted"
            )

            print("Oferta:", idOferta,
                  "| Grupo:", grupo,
                  "| Filas:", len(filas),
                  "| Fecha generación", fechaGeneracion,
                  "| Memorandum",memorandum,
                  "| Tipo de constancia", tipoConstancia
                  )

            encontrado = False

            for i, fila in enumerate(filas):

                primera_celda = fila.query_selector("td")

                if not primera_celda:
                    continue

                primera = primera_celda.inner_text().strip()

                if primera == grupo:

                    print("✅ Encontrado en posición:", i)
                    encontrado = True

                    fila.scroll_into_view_if_needed()
                    #pagina.wait_for_timeout(5000)

                    boton = fila.query_selector(
                        "button[nbtooltip='Generar constancia']"
                    )

                    if not boton:
                        tds = fila.query_selector_all("td")
                        if tds:
                            boton = tds[-1].query_selector("button")

                    if boton:
                        try:
                            
                            boton.click()
                            pagina.wait_for_timeout(5000)
                            print("🟢 Click en Generar constancia")
                            
                            #Subiendo archivo
                            input_file = pagina.query_selector("input[type='file'][formcontrolname='archivoDocente']")
                            nombre_archivo = f"{idOferta}-{grupo}.xlsx"
                            BASE_DIR = Path(__file__).resolve().parent
                            # Subimos un nivel (RobotPrueba)
                            RAIZ_PROYECTO = BASE_DIR.parent
                            ruta_archivo = RAIZ_PROYECTO / "subp1" / "output" / nombre_archivo

                            print(ruta_archivo)


                            #ruta_archivo = fr"D:\proyectos\RPA constancias\archivos\{nombre_archivo}"
                            input_file.set_input_files(ruta_archivo)

                            #Completando fecha de generación
                            input_fecha = pagina.query_selector("input[formcontrolname='fechaProceso']")
                            input_fecha.fill(fechaGeneracion)
                            # cierra el calendario/overlay
                            pagina.locator("text=Fecha de Generación:").click()
                            

                            #Completar Memorandum
                            input_memo = pagina.query_selector("input[formcontrolname='memorandum']")
                            input_memo.click()
                            input_memo.fill(memorandum)

                            #Completar tipo de constancia
                            pagina.click("nb-select[formcontrolname='tipoConstancia']")
                            pagina.wait_for_selector("nb-option")
                            pagina.click(f"nb-option:has-text('{tipoConstancia}')")

                            pagina.locator("text=Fecha de Generación:").click()

                            pagina.locator("text=Generar Constancias").click()
                            
                            pagina.wait_for_timeout(10000)



                        except Exception as e:
                            print(e)
                            boton.evaluate("el => el.click()")
                            print("🟢 Click forzado")
                    else:
                        print("❌ No se encontró botón")

                    break

                    

            if not encontrado:
                print("⚠️ No se encontró el grupo en esta oferta.")

        navegador.close()



