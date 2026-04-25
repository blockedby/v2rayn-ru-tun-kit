#!/usr/bin/env bash
set -euo pipefail
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HOME/.local/share/v2rayN/binConfigs/pi-apply-ru-tun-rules.py"
mkdir -p "$(dirname "$TARGET")"
install -m 755 "$SRC_DIR/apply-ru-tun-rules.py" "$TARGET"
echo "Installed: $TARGET"
echo "Run it after v2rayN regenerates/restarts configs:"
echo "  $TARGET"
