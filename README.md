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


py -m venv .venv
.venv\Scripts\activate
.venv\Scripts\Activate.ps1


pip install -r requirements.txt
pip freeze > requirements.txt
