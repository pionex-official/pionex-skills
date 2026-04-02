#!/usr/bin/env bash
# DCF Valuation — no external dependencies
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/get_dcf.py" "$@"
