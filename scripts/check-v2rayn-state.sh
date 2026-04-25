#!/usr/bin/env bash
set -euo pipefail
echo '### processes'
ps aux | grep -i '[v]2rayN\|[s]ing-box\|[x]ray' || true
echo; echo '### sing-box validation'
for c in "$HOME/.local/share/v2rayN/binConfigs/config.json" "$HOME/.local/share/v2rayN/binConfigs/configPre.json"; do
  [ -e "$c" ] || continue
  echo "-- $c"
  "$HOME/.local/share/v2rayN/bin/sing_box/sing-box" check -c "$c" --disable-color || true
done
echo; echo '### route snippets'
python3 - <<'PY'
import json, os
for name in ['config.json','configPre.json']:
 p=os.path.expanduser('~/.local/share/v2rayN/binConfigs/'+name)
 if not os.path.exists(p): continue
 d=json.load(open(p)); print('\n--', name)
 for i,r in enumerate(d.get('route',{}).get('rules',[])):
  if 'steam' in r.get('process_name',[]) or r.get('process_path_regex') or (r.get('rule_set') and ('geosite-ru-blocked' in r.get('rule_set') or 'geoip-ru' in r.get('rule_set'))): print(i,r)
PY
