# RPA_Constancias

Automatización para generación/validación de constancias (RPA) en Python.

## Requisitos
- Windows 10/11
- Python 3.10+ (recomendado 3.12)
- Git
- (Opcional) Playwright / navegador instalado (si aplica)
- Acceso a los servicios necesarios (DB / Google / etc.)

---

## Instalación (primer uso)

### 1) Clonar el repositorio
```bash
git clone https://github.com/pdifods07-rgb/RPA_Constancias.git
cd RPA_Constancias
2) Crear entorno virtual
py -m venv .venv
3) Activar entorno virtual

CMD

.venv\Scripts\activate

PowerShell

.venv\Scripts\Activate.ps1
4) Instalar dependencias
pip install -r requirements.txt

Si aún no existe requirements.txt, generarlo con:

pip freeze > requirements.txt
Configuración (obligatoria)
Variables/archivos sensibles (NO se suben a GitHub)

Este proyecto usa archivos/variables sensibles que deben existir localmente:

credenciales.json (Google Cloud Service Account)

validaciongeneracionconstancias.json (Google Cloud Service Account)

.env (opcional, para cadenas de conexión o tokens)

📌 Importante: estos archivos están en .gitignore y deben ser creados manualmente en tu máquina.

Estructura sugerida para credenciales

Coloca tus archivos de credenciales en la raíz (o en una carpeta secrets/ si prefieres).

Ejemplo:

RPA_Constancias/
  credenciales.json
  validaciongeneracionconstancias.json
  .env
  ...
Archivo .env (opcional)

Si usas variables de entorno, crea un archivo .env en la raíz con valores como:

DB_SERVER=MI_SERVIDOR
DB_NAME=MI_BASE
DB_TRUSTED_CONNECTION=yes

NO subir .env al repositorio.

Ejecución

Ejemplo genérico (ajusta según tu entrypoint real):

python main.py
Playwright (si tu proyecto usa automatización web)

Instalar navegadores:

playwright install
Buenas prácticas (GitHub / Seguridad)
✅ Qué se ignora (NO se sube)

Entornos virtuales: .venv/, venv/

Caché de Python: __pycache__/, *.pyc

Secrets: credenciales.json, validaciongeneracionconstancias.json, .env

✅ Qué SÍ se sube

Código fuente .py

requirements.txt

README.md

Plantillas de configuración (sin secretos), por ejemplo:

.env.example

credenciales.example.json (solo estructura, sin claves reales)

Troubleshooting
Error: push declined due to repository rule violations (secrets)

GitHub bloquea pushes con credenciales. Verifica que:

credenciales.json y validaciongeneracionconstancias.json NO estén trackeados

Estén listados en .gitignore

No existan en commits antiguos (si se subieron por error, hay que limpiar historial)

Licencia / Uso

Uso interno.


---

## ✅ `.gitignore` recomendado (para tu repo)
Crea o actualiza el archivo `.gitignore` (en la raíz):

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual env
venv/
.venv/
env/

# Environment variables
.env

# Secrets / credentials (Google service accounts)
credenciales.json
validaciongeneracionconstancias.json

# Logs
*.log

# OS / IDE
.DS_Store
.vscode/
.idea/
✅ Archivos “example” (muy recomendado)

Para que el proyecto sea fácil de clonar, sube plantillas sin secretos:

1) .env.example
DB_SERVER=
DB_NAME=
DB_TRUSTED_CONNECTION=yes
2) credenciales.example.json
{
  "type": "service_account",
  "project_id": "TU_PROJECT_ID",
  "private_key_id": "NO_COLOCAR",
  "private_key": "NO_COLOCAR",
  "client_email": "TU_CLIENT_EMAIL",
  "client_id": "TU_CLIENT_ID"
}

El README debe decir: “Renombra credenciales.example.json a credenciales.json y coloca tus datos reales”.

✅ Qué debes configurar para que funcione

Checklist rápido para cualquier persona que clone el repo:

✅ Instalar Python

✅ Crear/activar .venv

✅ pip install -r requirements.txt

✅ Crear/colocar:

credenciales.json

validaciongeneracionconstancias.json

.env (si aplica)

✅ Si usa Playwright:

playwright install

✅ Ejecutar python main.py (o tu entrypoint)
