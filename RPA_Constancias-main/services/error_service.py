from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound
import pyodbc
import socket

def map_exception(e):
    # -----------------------------
    # UI AUTOMATION (WEB)
    # -----------------------------
    if isinstance(e, PlaywrightTimeoutError):
        return build_error(
            "UI_AUTOMATION_ERROR",
            1
        )

    # -----------------------------
    # DATABASE (SQL SERVER)
    # -----------------------------
    elif isinstance(e, pyodbc.OperationalError):
        return build_error(
            "DATABASE_ERROR",
            2
        )

    elif isinstance(e, pyodbc.ProgrammingError):
        return build_error(
            "DATABASE_ERROR",
            2
        )

    # -----------------------------
    # NETWORK / INFRASTRUCTURE
    # -----------------------------
    elif isinstance(e, socket.gaierror):
        return build_error(
            "INFRASTRUCTURE_ERROR",
            3
        )

    elif isinstance(e, ConnectionError):
        return build_error(
            "INFRASTRUCTURE_ERROR",
            3
        )

    # -----------------------------
    # GOOGLE SHEETS / API
    # -----------------------------
    elif isinstance(e, PermissionError):
        return build_error(
            "GOOGLE_SHEET_ERROR",
            4
        )
    
    elif isinstance(e, SpreadsheetNotFound):
        return build_error(
            "GOOGLE_SHEET_ERROR",
            4
        )

    elif isinstance(e, WorksheetNotFound):
        return build_error(
            "GOOGLE_SHEET_ERROR",
            4
        )

    elif isinstance(e, APIError):
        return build_error(
            "GOOGLE_SHEET_ERROR",
            4
        )

    # -------------------------------------------------
    # ERRORES PROPIOS DE PYTHON (VARIABLES, FUNCIONES)
    # -------------------------------------------------
    elif isinstance(e, KeyError):
        return build_error(
            "DATA_STRUCTURE_ERROR",
            5
        )
    
    elif isinstance(e, AttributeError):
        return build_error(
            "APPLICATION_ERROR",
            7
        )
    
    elif isinstance(e, TypeError):
        return build_error(
            "APPLICATION_ERROR",
            7
        )
    
    elif isinstance(e, IndexError):
        return build_error(
            "DATA_STRUCTURE_ERROR",
            5
        )

    elif "BUSINESS_RULE_ERROR" in str(e):
        return build_error(
            "BUSINESS_RULE_ERROR",
            6
        )

    # -----------------------------
    # ERROR DESCONOCIDO
    # -----------------------------
    else:
        return build_error(
            "APPLICATION_ERROR",
            7
        )


def build_error(categoria, id_error):
    return {
        "categoria": categoria,
        "id": id_error,
    }