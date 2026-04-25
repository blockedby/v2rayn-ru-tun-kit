#!/usr/bin/env bash
set -euo pipefail
TS="$(date +%Y%m%d-%H%M%S)"
BD="$HOME/.local/share/v2rayN/backups/ru-tun-kit-$TS"
mkdir -p "$BD"
for f in \
  "$HOME/.local/share/v2rayN/guiConfigs/guiNConfig.json" \
  "$HOME/.local/share/v2rayN/guiConfigs/guiNDB.db" \
  "$HOME/.local/share/v2rayN/binConfigs/config.json" \
  "$HOME/.local/share/v2rayN/binConfigs/configPre.json"; do
  [ -e "$f" ] && cp -a "$f" "$BD/"
done
cat > "$BD/restore.sh" <<'RESTORE'
#!/usr/bin/env bash
set -euo pipefail
BD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -e "$BD/guiNConfig.json" ] && cp -a "$BD/guiNConfig.json" "$HOME/.local/share/v2rayN/guiConfigs/guiNConfig.json"
[ -e "$BD/guiNDB.db" ] && cp -a "$BD/guiNDB.db" "$HOME/.local/share/v2rayN/guiConfigs/guiNDB.db"
[ -e "$BD/config.json" ] && cp -a "$BD/config.json" "$HOME/.local/share/v2rayN/binConfigs/config.json"
[ -e "$BD/configPre.json" ] && cp -a "$BD/configPre.json" "$HOME/.local/share/v2rayN/binConfigs/configPre.json"
echo "Restored from $BD. Restart v2rayN/core."
RESTORE
chmod +x "$BD/restore.sh"
echo "$BD"
echo "Restore with: $BD/restore.sh"
