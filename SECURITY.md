# SECURITY

This project follows OWASP Top 10:2025 controls for a private notes API.

## Covered OWASP 2025 vulnerabilities (5)

### A01 - Broken Access Control
- Risk in this API: user can access another user's note by ID.
- Mitigation: every note query filters by both `Note.id` and `Note.owner_id == current_user.id`.

### A02 - Security Misconfiguration
- Risk in this API: wildcard CORS in production, public docs exposure, hardcoded secrets.
- Mitigation: settings loaded from environment, startup validation, CORS restricted by explicit allowlist, docs enabled only in development.

### A03 - Supply Chain Failures (NEW in 2025)
- Risk in this API: vulnerable Python dependencies introduced through `requirements.txt`.
- Mitigation: automated dependency scanning with `pip-audit` and CI blocking on vulnerabilities via `scripts/audit.sh`.

### A05 - Injection
- Risk in this API: dynamic SQL strings or raw f-string queries with user input.
- Mitigation: SQLAlchemy ORM filters and strict Pydantic schema validation for request bodies.

### A10 - Mishandling of Exceptional Conditions (NEW in 2025)
- Risk in this API: returning stack trace/internal exception text to clients on errors.
- Mitigation: controlled `try/except` in endpoints, internal logging, and safe client messages (`Internal server error.`).

## OWASP 2021 vs 2025 quick comparison

- `A03 Supply Chain Failures` is a new explicit category in OWASP Top 10:2025.
- `A10 Mishandling of Exceptional Conditions` is a new explicit category in OWASP Top 10:2025.
- In OWASP 2021, these concerns existed but were not represented as these dedicated categories.

## How to run pip-audit

Install tool if needed:

```bash
pip install pip-audit
```

Run security dependency scan:

```bash
bash scripts/audit.sh
```

Behavior:
- Exit code `0`: no known vulnerabilities.
- Exit code `1`: vulnerabilities found (CI/CD must fail).
- Exit code `2`: audit execution problem (tool or environment issue).

## Command to verify the app security baseline

```bash
bash scripts/audit.sh && python -m compileall app
```

This validates supply-chain posture (A03) and confirms the app package compiles with current secure exception-handling patterns (A10 control implementation in routers).
