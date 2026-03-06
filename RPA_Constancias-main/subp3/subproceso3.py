# -*- coding: utf-8 -*-
"""
RPA robusto (Playwright + SQL Server + pandas)
- Validaciones antes de interactuar con la UI
- Reintentos por paso
- Evidencia de error (screenshot + HTML)
- Log a consola + archivo
- Resumen final de errores (sin tumbar todo el proceso)
"""

from playwright.sync_api import sync_playwright, TimeoutError as ErrorTimeout
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import time
import logging
import traceback

import pandas as pd
import pyodbc


import re

# =============================================================================
# 1) CONEXIÓN + QUERIES
# =============================================================================

# 🔹 Cadena de conexión con Windows Authentication
conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=PCPOPRDIFOD132;"
    "DATABASE=db_automatizacion;"
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


# =============================================================================
# 2) URLS + SELECTORES
# =============================================================================

DOMAIN = "https://sifods-cap.minedu.gob.pe"
URL_LOGIN = f"{DOMAIN}/login"
URL_ADM_PARAMETROS = f"{DOMAIN}/admin/acciones-formativas-opciones"

# ⚠️ AJUSTAR SELECTORES SEGÚN EL HTML REAL
SELECTORES = {
    "usuario": 'input[name="documentoIdentidad"]',
    "contrasena": 'input[name="password"]',
    "boton_login": 'button[type="submit"]'
}


# =============================================================================
# 3) CARGA DE INSUMOS
# =============================================================================

df_constancias_pendientes = pd.read_sql(
    query_constancias_pendientes,
    conexion,
    dtype={
        "ID_OFERTA_FORMATIVA": str,
        "CODIGO": str,
        "USUARIO_DOCUMENTO": str
    }
)

df_memorandum = pd.read_sql(query_memorandum, conexion)
df_parametro = pd.read_sql(query_parametros, conexion, dtype=str)

# Extrayendo insumos requeridos.
df_constancias_pendientes["OF_GRUPO"] = (
    df_constancias_pendientes["ID_OFERTA_FORMATIVA"].astype(str) + "-" +
    df_constancias_pendientes["NOMBRE_GRUPO"].astype(str)
)

df_constancias = df_constancias_pendientes[
    ["TIPO_REGISTRO", "ID_OFERTA_FORMATIVA", "NOMBRE_GRUPO", "OF_GRUPO", "CODIGO"]
].drop_duplicates()

print(df_constancias)

# Extraer memorandum vigente
df_memorandum["FECHA_INICIO"] = pd.to_datetime(df_memorandum["FECHA_INICIO"])
df_memorandum["FECHA_FIN"] = pd.to_datetime(df_memorandum["FECHA_FIN"])

hoy = pd.Timestamp.today().normalize()

df_memorandum_vigente = df_memorandum[
    (df_memorandum["FECHA_INICIO"] <= hoy) &
    (df_memorandum["FECHA_FIN"] >= hoy)
]

# ⚠️ OJO: en tu código original tomabas el primero siempre.
# Aquí uso el vigente si existe; si no, uso el primero como fallback.
if not df_memorandum_vigente.empty:
    memorandum = str(df_memorandum_vigente.iloc[0]["MEMORANDUM"])
else:
    memorandum = str(df_memorandum.iloc[0]["MEMORANDUM"]) if not df_memorandum.empty else ""

print(df_memorandum.head())
print(df_memorandum_vigente)
print("MEMORANDUM USADO:", memorandum)

print(df_parametro)

conexion.close()


# =============================================================================
# 4) HELPERS ROBUSTOS (LOG + RETRY + EVIDENCIAS)
# =============================================================================

@dataclass
class StepError:
    step: str
    message: str
    url: str
    screenshot: str | None
    html: str | None
    traceback: str


def setup_logger():
    
    logs_dir = Path(__file__).parent.parent / "logs"
    print(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"rpa_subp3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    print(log_file)
    logger = logging.getLogger("rpa")
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # evita duplicar handlers si corres el script más de una vez en mismo proceso
    if not logger.handlers:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger, log_file


def _safe_dump_evidence(page, step_name: str):
    evid_dir = Path(__file__).resolve().parent / "evidencias"
    evid_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = str(evid_dir / f"{ts}_{step_name}.png")
    html_path = str(evid_dir / f"{ts}_{step_name}.html")

    try:
        page.screenshot(path=screenshot_path, full_page=True)
    except Exception:
        screenshot_path = None

    try:
        html = page.content()
        Path(html_path).write_text(html, encoding="utf-8")
    except Exception:
        html_path = None

    return screenshot_path, html_path


def retry(action, *, tries=3, base_sleep=0.6, step_name="step", logger=None):
    last = None
    for i in range(1, tries + 1):
        try:
            return action()
        except Exception as e:
            last = e
            if logger:
                logger.warning(f"[{step_name}] intento {i}/{tries} falló: {e}")
            time.sleep(base_sleep * i)
    raise last


def wait_visible(page, selector: str, *, timeout=15000):
    page.locator(selector).wait_for(state="visible", timeout=timeout)


def safe_click(page, selector: str, *, timeout=15000, tries=3, logger=None, force=False):
    def _do():
        loc = page.locator(selector)
        loc.wait_for(state="visible", timeout=timeout)
        loc.scroll_into_view_if_needed()
        loc.click(timeout=timeout, force=force)
    return retry(_do, tries=tries, step_name=f"click:{selector}", logger=logger)


def safe_fill(page, selector: str, value: str, *, timeout=15000, tries=3, logger=None):
    def _do():
        loc = page.locator(selector)
        loc.wait_for(state="visible", timeout=timeout)
        loc.scroll_into_view_if_needed()
        loc.fill(value, timeout=timeout)
    return retry(_do, tries=tries, step_name=f"fill:{selector}", logger=logger)


""" def safe_select_nb_option(page, nb_select_selector: str, option_text: str, *, logger=None):
    # abre nb-select y elige opción por texto
    safe_click(page, nb_select_selector, logger=logger)
    page.locator("nb-option").first.wait_for(state="visible", timeout=15000)
    safe_click(page, f"nb-option:has-text('{option_text}')", logger=logger)
 """


def safe_select_nb_option(page, nb_select_selector: str, option_text: str, *, logger=None, timeout=15000):
    # 1) Abrir el nb-select
    safe_click(page, nb_select_selector, logger=logger, timeout=timeout)

    # 2) Esperar que aparezcan las opciones
    page.locator("nb-option").first.wait_for(state="visible", timeout=timeout)

    # 3) Seleccionar texto EXACTO (no "contiene")
    pattern = re.compile(rf"^\s*{re.escape(option_text)}\s*$", re.IGNORECASE)

    opt = page.locator("nb-option", has_text=pattern).first
    opt.wait_for(state="visible", timeout=timeout)
    opt.scroll_into_view_if_needed()
    opt.click(timeout=timeout)

def guard_step(errors: list[StepError], page, step_name: str, logger, fn):
    try:
        return fn()
    except Exception as e:
        tb = traceback.format_exc()
        screenshot_path, html_path = _safe_dump_evidence(page, step_name)
        err = StepError(
            step=step_name,
            message=str(e),
            url=page.url if page else "",
            screenshot=screenshot_path,
            html=html_path,
            traceback=tb
        )
        errors.append(err)
        logger.error(f"[ERROR] {step_name} | {e}")
        logger.error(tb)
        # NO revienta el proceso; continúa
        return None


# =============================================================================
# 5) CAPTCHA (SI LO NECESITAS)
# =============================================================================

def solicitar_captcha():
    ventana = tk.Tk()
    ventana.withdraw()

    captcha = simpledialog.askstring(
        "Ingreso de CAPTCHA",
        "Ingrese el CAPTCHA recibido por correo:"
    )

    ventana.destroy()
    return (captcha or "").strip()


def llenar_formulario_login(pagina, usuario, contrasena):
    wait_visible(pagina, SELECTORES["usuario"], timeout=30000)
    wait_visible(pagina, SELECTORES["contrasena"], timeout=30000)

    safe_fill(pagina, SELECTORES["usuario"], usuario)
    safe_fill(pagina, SELECTORES["contrasena"], contrasena)
    safe_click(pagina, SELECTORES["boton_login"])


# =============================================================================
# 6) EJECUCIÓN PRINCIPAL
# =============================================================================

def ejecutar_subp3():
    logger, log_file = setup_logger()
    errors: list[StepError] = []

    usuario = "72119474"
    contrasena = "Minedu2026$"

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False, args=["--start-maximized"])
        contexto = navegador.new_context(no_viewport=True)
        pagina = contexto.new_page()

        guard_step(errors, pagina, "goto_login", logger, lambda: pagina.goto(URL_LOGIN, timeout=60000))
        guard_step(errors, pagina, "wait_dom_login", logger, lambda: pagina.wait_for_load_state("domcontentloaded"))

        def _login():
            llenar_formulario_login(pagina, usuario, contrasena)
            # Mejor esperar por un elemento post-login real (ajusta si tienes uno)
            pagina.wait_for_timeout(1500)

        # Reintento de login (por si se renderiza tarde)
        guard_step(errors, pagina, "login", logger, lambda: retry(_login, tries=2, step_name="login", logger=logger))

        logger.info("Iniciando procesamiento de parámetros...")

        # ---------------------------------------------------------------------
        # A) PARÁMETROS PENDIENTES
        # ---------------------------------------------------------------------
        for index, row in df_parametro.iterrows():
            idGrupoParametro = str(row["ID_GRUPO_PARAMETRO"])
            id_oferta = str(row["ID_OFERTA_FORMATIVA"])
            descripcion = f"{row['CODIGO_OFERTA_FORMATIVA']} ({id_oferta})"

            def _ir_parametros():
                pagina.goto(URL_ADM_PARAMETROS, timeout=60000)
                pagina.wait_for_load_state("domcontentloaded")
                wait_visible(pagina, "nb-select", timeout=30000)

            guard_step(errors, pagina, f"param_goto_{idGrupoParametro}_{id_oferta}", logger, _ir_parametros)

            if idGrupoParametro == "163":
                def _crear_163():
                    safe_select_nb_option(
                        pagina,
                        "nb-select",
                        "Configuracion de detalle de evaluacion final para generar constancia",
                        logger=logger
                    )

                    safe_click(pagina, "button:has-text('Nuevo')", logger=logger)
                    safe_fill(pagina, "input[formcontrolname='valor']", "Por haber aprobado el:", logger=logger)
                    safe_fill(pagina, "input[formcontrolname='descripcion']", descripcion, logger=logger)
                    safe_fill(pagina, "input[formcontrolname='codigo']", id_oferta, logger=logger)

                    safe_click(pagina, "button:has-text('Aceptar')", logger=logger)

                    # Modal confirm (último Aceptar)
                    pagina.locator("nb-card").first.wait_for(state="visible", timeout=20000)
                    botones = pagina.locator("button:has-text('Aceptar')")
                    botones.nth(botones.count() - 1).click()

                    pagina.wait_for_timeout(800)

                guard_step(errors, pagina, f"param_163_create_{id_oferta}", logger, _crear_163)

            elif idGrupoParametro == "164":
                def _crear_164():
                    safe_select_nb_option(
                        pagina,
                        "nb-select",
                        "Configuracion de fecha de desarrollo para generar constancia",
                        logger=logger
                    )

                    safe_click(pagina, "button:has-text('Nuevo')", logger=logger)
                    safe_fill(
                        pagina,
                        "input[formcontrolname='valor']",
                        "Desarrollado desde el {INI_DIA} de {INI_MES} hasta el {FIN_DIA} de {FIN_MES} del {FIN_ANIO}, con un total de {HORAS} horas.",
                        logger=logger
                    )
                    safe_fill(pagina, "input[formcontrolname='descripcion']", descripcion, logger=logger)
                    safe_fill(pagina, "input[formcontrolname='codigo']", id_oferta, logger=logger)

                    safe_click(pagina, "button:has-text('Aceptar')", logger=logger)

                    pagina.locator("nb-card").first.wait_for(state="visible", timeout=20000)
                    botones = pagina.locator("button:has-text('Aceptar')")
                    botones.nth(botones.count() - 1).click()

                    pagina.wait_for_timeout(800)

                guard_step(errors, pagina, f"param_164_create_{id_oferta}", logger, _crear_164)

        logger.info("Iniciando procesamiento de constancias...")

        # ---------------------------------------------------------------------
        # B) GENERAR CONSTANCIAS
        # ---------------------------------------------------------------------
        for _, fila in df_constancias.iterrows():
            idOferta = int(fila["ID_OFERTA_FORMATIVA"])
            grupo = str(fila["NOMBRE_GRUPO"]).strip()
            fechaGeneracion = datetime.now().strftime("%d/%m/%Y")

            if fila["TIPO_REGISTRO"] == "CURSO":
                tipoConstancia = "Curso"
            else:
                tipoConstancia = f"{fila['CODIGO']}-{fila['ID_OFERTA_FORMATIVA']}"

            URLOFERTA = f"{DOMAIN}/dash/mantenimiento/oferta-formativa/disenar/{idOferta}"

            def _abrir_oferta():
                pagina.goto(URLOFERTA, timeout=60000)
                pagina.wait_for_load_state("domcontentloaded")
                wait_visible(pagina, "app-disenar-oferta-formativa table", timeout=30000)

            guard_step(errors, pagina, f"oferta_goto_{idOferta}", logger, _abrir_oferta)

            def _generar():
                # Localiza la fila por texto del grupo
                row_loc = pagina.locator(
                    "app-disenar-oferta-formativa table tr.ng-star-inserted",
                    has_text=grupo
                ).first

                row_loc.wait_for(state="visible", timeout=20000)
                row_loc.scroll_into_view_if_needed()

                # Botón generar constancia
                btn = row_loc.locator("button[nbtooltip='Generar constancia']").first
                if btn.count() == 0:
                    btn = row_loc.locator("td").last.locator("button").first

                btn.wait_for(state="visible", timeout=15000)
                btn.click()

                # Form de generación
                wait_visible(pagina, "input[type='file'][formcontrolname='archivoDocente']", timeout=30000)

                # Archivo (ajusta aquí tu ruta real)
                nombre_archivo = f"{idOferta}-{grupo}.xlsx"
                BASE_DIR = Path(__file__).resolve().parent
                RAIZ_PROYECTO = BASE_DIR.parent
                ruta_archivo = RAIZ_PROYECTO / "subp1" / "output" / nombre_archivo

                if not ruta_archivo.exists():
                    raise FileNotFoundError(f"No existe el archivo: {ruta_archivo}")

                pagina.set_input_files(
                    "input[type='file'][formcontrolname='archivoDocente']",
                    str(ruta_archivo)
                )

                # Fecha de generación
                safe_fill(pagina, "input[formcontrolname='fechaProceso']", fechaGeneracion, logger=logger)
                pagina.locator("text=Fecha de Generación:").click()

                # Memorandum
                safe_fill(pagina, "input[formcontrolname='memorandum']", str(memorandum), logger=logger)

                opciones = pagina.locator("nb-option").all_inner_texts()
                print("OPCIONES DISPONIBLES:", opciones)

                # Tipo constancia
                safe_select_nb_option(
                    pagina,
                    "nb-select[formcontrolname='tipoConstancia']",
                    tipoConstancia,
                    logger=logger
                )

                pagina.locator("text=Fecha de Generación:").click()

                # Botón final
                safe_click(pagina, "text=Generar Constancias", logger=logger)

                pagina.wait_for_timeout(5000)

            # Reintento por constancia (por si el render falló)
            guard_step(
                errors,
                pagina,
                f"generar_constancia_{idOferta}_{grupo}",
                logger,
                lambda: retry(_generar, tries=2, step_name="generar", logger=logger)
            )

        navegador.close()

    # -------------------------------------------------------------------------
    # C) RESUMEN FINAL (IMPRIME ERRORES + EVIDENCIAS)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("RESUMEN FINAL")
    print(f"Log: {log_file}")
    print(f"Total errores: {len(errors)}")
    for i, e in enumerate(errors, 1):
        print("-" * 90)
        print(f"{i}. Step: {e.step}")
        print(f"   URL: {e.url}")
        print(f"   Error: {e.message}")
        print(f"   Screenshot: {e.screenshot}")
        print(f"   HTML: {e.html}")
        print("   Traceback:")
        print(e.traceback)
    print("=" * 90)


# =============================================================================
# 7) MAIN
# =============================================================================

""" if __name__ == "__main__":
    #setup_logger()
    ejecutar_subp3()  """