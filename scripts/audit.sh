#!/usr/bin/env bash

set -uo pipefail

echo "==> OWASP A03 Supply Chain Failures check"
echo "==> Running pip-audit..."

TMP_REPORT="$(mktemp)"

if ! pip-audit --format json --progress-spinner off >"$TMP_REPORT" 2>/dev/null; then
  echo "ERROR: pip-audit execution failed. Ensure it is installed and dependencies are resolvable."
  rm -f "$TMP_REPORT"
  exit 2
fi

VULN_COUNT="$(python - <<'PY' "$TMP_REPORT"
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as fh:
    data = json.load(fh)

deps = data.get("dependencies", [])
vulns = []
for dep in deps:
    name = dep.get("name", "unknown")
    version = dep.get("version", "unknown")
    for vuln in dep.get("vulns", []):
        vid = vuln.get("id", "N/A")
        fix_versions = ", ".join(vuln.get("fix_versions", [])) or "no fix available"
        description = vuln.get("description", "").strip().replace("\n", " ")
        if len(description) > 120:
            description = description[:117] + "..."
        vulns.append((name, version, vid, fix_versions, description))

print(len(vulns))
if vulns:
    print("FOUND_VULNS")
    for item in vulns:
        pkg, ver, cve, fixes, desc = item
        print(f"- package={pkg} version={ver} advisory={cve} fixed_in={fixes}")
        if desc:
            print(f"  detail: {desc}")
PY
)"

COUNT_LINE="$(printf '%s\n' "$VULN_COUNT" | head -n 1)"
DETAIL_LINES="$(printf '%s\n' "$VULN_COUNT" | awk 'NR>1')"

if [ "$COUNT_LINE" -gt 0 ]; then
  echo "VULNERABILITIES FOUND: $COUNT_LINE"
  echo "$DETAIL_LINES"
  rm -f "$TMP_REPORT"
  exit 1
fi

echo "No known vulnerabilities found by pip-audit."
rm -f "$TMP_REPORT"
exit 0
