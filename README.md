# Secure Notes API — Secure Vibe Coding con OWASP Top 10:2025

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)
![OWASP 2025](https://img.shields.io/badge/OWASP-Top%2010%3A2025-darkred)

Secure Notes API es una API REST de notas privadas construida con FastAPI, SQLAlchemy y SQLite bajo una filosofía de **Secure Vibe Coding**: la seguridad se diseña desde el primer prompt y se valida durante el desarrollo, en lugar de “parcharla” al final del ciclo.

En este proyecto, cada decisión técnica parte de controles OWASP Top 10:2025: autenticación JWT con expiración, validación estricta de entradas, control de ownership en acceso a notas, configuración segura por entorno y auditoría de dependencias para cadena de suministro.

## Por qué OWASP 2025 y no 2021

OWASP Top 10:2025 refleja mejor los riesgos actuales del desarrollo moderno y de pipelines automatizados. Esta API usa 2025 como baseline para incorporar controles que no estaban explícitamente priorizados en 2021.

| Tema | OWASP 2021 | OWASP 2025 | Impacto en este proyecto |
|---|---|---|---|
| Supply Chain Failures | No categoría explícita | **A03 (NUEVO 2025)** | `scripts/audit.sh` ejecuta `pip-audit` y bloquea CI/CD si hay vulnerabilidades |
| Mishandling of Exceptional Conditions | No categoría explícita | **A10 (NUEVO 2025)** | Manejo controlado de excepciones: logs internos + mensajes seguros al cliente |
| Security Misconfiguration | A05 | **A02** | Validación de settings en startup, CORS restringido y docs solo en desarrollo |
| Injection | A03 | **A05** | Validación Pydantic + consultas ORM parametrizadas (sin SQL dinámico inseguro) |

## Las 3 capas de seguridad

### Capa 1: Cursor Rules (`security.mdc`)
Reglas persistentes de seguridad aplican controles OWASP en tiempo de implementación:
- ownership obligatorio por usuario en consultas de notas
- secretos desde variables de entorno (sin hardcode)
- JWT con expiración y hashing bcrypt
- manejo explícito de excepciones con respuestas seguras

### Capa 2: Audit prompt (riesgos ANTES de codificar)
Antes de escribir código, se listan y analizan los riesgos críticos OWASP Top 10:2025 del caso de uso. Esto fuerza diseño seguro desde el inicio y reduce deuda de seguridad.

### Capa 3: `pip-audit` para Supply Chain (A03)
La seguridad de dependencias se verifica automáticamente con `pip-audit`:

```bash
bash scripts/audit.sh
```

El script:
- muestra CVEs/advisories detectados en un formato legible
- retorna `exit 1` si encuentra vulnerabilidades
- está diseñado para bloquear pipelines CI/CD inseguros

## Estructura base

```text
secure-notes-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── deps.py
│   └── routers/
│       ├── auth.py
│       └── notes.py
├── scripts/
│   └── audit.sh
└── SECURITY.md
```

## Verificación rápida de seguridad

```bash
bash scripts/audit.sh && python -m compileall app
```

## Licencia

Uso educativo y de referencia para prácticas de secure coding en APIs FastAPI.
