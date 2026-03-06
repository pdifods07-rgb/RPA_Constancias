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
```
### 2) Crear entorno virtual
```bash
py -m venv .venv
```

### 3) Activar entorno virtual
CMD
```bash
.venv\Scripts\activate
```
###  4) Instalar dependencias
```bash
pip install -r requirements.txt
```

### Configuración (obligatoria)
### Variables/archivos sensibles (NO se suben a GitHub)

Este proyecto usa archivos/variables sensibles que deben existir localmente:

credenciales.json (Google Cloud Service Account)

validaciongeneracionconstancias.json (Google Cloud Service Account)

.env (opcional, para cadenas de conexión o tokens)

📌 Importante: estos archivos están en .gitignore y deben ser creados manualmente en tu máquina.


### Estructura sugerida para credenciales

Coloca tus archivos de credenciales en la raíz (o en una carpeta secrets/ si prefieres).

Ejemplo:
```bash
RPA_Constancias/
  credenciales.json
  validaciongeneracionconstancias.json
  .env
  ...
```


### Ejecución

Ejemplo genérico (ajusta según tu entrypoint real):
```bash
python main.py
```
