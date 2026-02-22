# Actividad 6.2 - Reservation System

## Estructura
- `src/reservation_system/`: código fuente (paquete Python)
- `tests/`: pruebas unitarias (unittest)
- `data/`: archivos de ejemplo (opcional para ejecución manual)

> Importante: usar `PYTHONPATH=src` para que Python encuentre el paquete.

## Ejecutar flake 8

```bash
PYTHONPATH=src flake8 src tests

## Ejecutar pylint

```bash
PYTHONPATH=src pylint src/reservation_system                            
PYTHONPATH=src pylint tests

## Ejecutar pruebas

```bash
PYTHONPATH=src python -m unittest discover -s tests -p "test_*.py"
