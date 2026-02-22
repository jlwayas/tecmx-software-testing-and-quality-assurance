# Actividad 6.2 – Reservation System (Python)

Sistema de reservaciones con persistencia en archivos JSON y pruebas unitarias.
Incluye CRUD de **Hoteles** y **Clientes**, así como **crear/cancelar reservaciones**.

---

## Objetivos de la actividad
- Implementar un sistema con clases **Hotel**, **Customer** y **Reservation**.
- Persistir operaciones en archivos (JSON).
- Validar funcionamiento mediante **pruebas unitarias** con `unittest`.
- Cumplir estándar **PEP-8**, sin hallazgos en **flake8** y sin observaciones en **pylint**.
- Manejar **datos inválidos** en archivos sin detener la ejecución (se imprime error y se continúa).

---

## Estructura del proyecto
- `src/reservation_system/`: código fuente (paquete Python)
  - `models.py`: modelos de dominio (Hotel, Customer, Reservation)
  - `storage.py`: persistencia JSON con tolerancia a errores
  - `services.py`: lógica de negocio (CRUD, reservar/cancelar)
- `tests/`: pruebas unitarias (`unittest`)
- `data/`: archivos JSON de ejemplo (opcional, para ejecución manual)

> Importante: se usa `PYTHONPATH=src` para que Python encuentre el paquete.

---

## Requisitos
- Python 3.x
- Paquetes: `flake8`, `pylint`, `coverage`

## Instalación:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar el programa
```bash
PYTHONPATH=src python -m reservation_system.main
```

## Ejecución de unit tests y lints

> Ejecuta los siguientes comandos desde la raíz del proyecto (donde está `src/` y `tests/`).

### 1) Pylint
```bash
PYTHONPATH=src pylint src/reservation_system
PYTHONPATH=src pylint tests
```

### 2) flake8
```bash
PYTHONPATH=src flake8 src tests
```

### 3) Coverage and report
```bash
PYTHONPATH=src coverage run -m unittest discover -s tests -p "test_*.py"
PYTHONPATH=src coverage report -m
```
