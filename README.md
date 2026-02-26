RPA_Constancias

Automatización para generación y validación de constancias mediante RPA en Python.

📌 Requisitos

Windows 10/11

Python 3.10+ (recomendado 3.12)

Git

Playwright (si aplica)

Acceso a base de datos SQL Server

Credenciales Google Cloud (Service Account)

🚀 Instalación (primer uso)
1️⃣ Clonar el repositorio
git clone https://github.com/pdifods07-rgb/RPA_Constancias.git
cd RPA_Constancias
2️⃣ Crear entorno virtual
py -m venv .venv
3️⃣ Activar entorno virtual
CMD
.venv\Scripts\activate
PowerShell
.venv\Scripts\Activate.ps1
4️⃣ Instalar dependencias
pip install -r requirements.txt

Si aún no existe requirements.txt, generarlo con:

pip freeze > requirements.txt

Si el proyecto usa Playwright:

playwright install
⚙️ Configuración Obligatoria
🔐 Archivos sensibles (NO se suben a GitHub)

Este proyecto requiere los siguientes archivos locales:

credenciales.json

validaciongeneracionconstancias.json

.env (opcional)

⚠️ Estos archivos están en .gitignore y deben crearse manualmente.

🗄️ Configuración Base de Datos

Ejemplo de conexión SQL Server:

conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=MI_SERVIDOR;"
    "DATABASE=MI_BASE;"
    "Trusted_Connection=yes;"
)

Si usas .env:

DB_SERVER=MI_SERVIDOR
DB_NAME=MI_BASE
DB_TRUSTED_CONNECTION=yes
▶️ Ejecución

Ejecutar el archivo principal:

python main.py

(Reemplazar main.py por el archivo real del proyecto si es distinto.)

📁 Estructura del Proyecto
RPA_Constancias/
│
├── config/
├── db/
├── services/
├── subp1/
├── subp2/
├── subp3/
├── subp4/
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
🔒 Archivos Ignorados
__pycache__/
*.pyc
venv/
.venv/
.env
credenciales.json
validaciongeneracionconstancias.json
