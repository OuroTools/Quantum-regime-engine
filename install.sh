#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "========================================"
echo " Regime Detection Engine - Install"
echo "========================================"

python3 --version
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[all]"
python3 scripts/verify.py

echo ""
echo "Install complete!"
echo "  regime-engine      - CLI"
echo "  regime-dashboard   - Web UI"
