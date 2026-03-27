#!/usr/bin/env bash
# Earnings Analysis — zero dependencies, runs with system Python
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/earnings_report.py" "$@"
