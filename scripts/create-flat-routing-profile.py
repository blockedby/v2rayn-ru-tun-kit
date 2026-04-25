#!/usr/bin/env python3
"""Create/activate a flat v2rayN routing profile for Russia + Steam direct.

This edits ~/.local/share/v2rayN/guiConfigs/guiNDB.db.
Backup first with scripts/backup-v2rayn-configs.sh.
"""
import json
import random
import sqlite3
from pathlib import Path

DB = Path.home() / ".local/share/v2rayN/guiConfigs/guiNDB.db"
REMARKS = "RUv2-flat-steam-direct-free-speech"

def rid() -> str:
    return str(random.randrange(10**18, 9 * 10**18))

rules = [
    {"Id": rid(), "OutboundTag": "direct", "Process": [
        "steam", "steamwebhelper", "steam-runtime-steam-remote", "dota2", "dota2_linux",
        "/home/kcnc/.steam/debian-installation/steamapps/common/dota 2 beta/game/bin/linuxsteamrt64/dota2",
        "/home/kcnc/.steam/root/steamapps/common/dota 2 beta/game/bin/linuxsteamrt64/dota2",
        "/home/kcnc/.steam/steam/steamapps/common/dota 2 beta/game/bin/linuxsteamrt64/dota2",
    ], "Enabled": True, "Remarks": "Steam/Dota/direct games by process"},
    {"Id": rid(), "OutboundTag": "direct", "Protocol": ["bittorrent"], "Enabled": True, "Remarks": "BitTorrent direct"},
    {"Id": rid(), "OutboundTag": "block", "Domain": ["geosite:category-ads-all"], "Enabled": True, "Remarks": "Ads block"},
    {"Id": rid(), "OutboundTag": "direct", "Ip": ["geoip:private"], "Enabled": True, "Remarks": "LAN/private IP direct"},
    {"Id": rid(), "OutboundTag": "direct", "Domain": ["geosite:private"], "Enabled": True, "Remarks": "LAN/private domains direct"},
    {"Id": rid(), "OutboundTag": "proxy", "Ip": ["geoip:ru-blocked"], "Enabled": True, "Remarks": "RU-blocked IP proxy"},
    {"Id": rid(), "OutboundTag": "proxy", "Domain": ["geosite:ru-blocked", "geosite:gfw", "geosite:greatfire"], "Enabled": True, "Remarks": "Blocked/free-speech domains proxy"},
    {"Id": rid(), "OutboundTag": "proxy", "Ip": ["geoip:telegram", "geoip:twitter", "geoip:facebook", "geoip:google"], "Enabled": True, "Remarks": "Social/Google IP proxy"},
    {"Id": rid(), "OutboundTag": "direct", "Ip": ["geoip:ru"], "Enabled": True, "Remarks": "Russian IP direct"},
    {"Id": rid(), "OutboundTag": "proxy", "Port": "0-65535", "Enabled": True, "Remarks": "Final proxy"},
]

con = sqlite3.connect(DB)
con.execute("update RoutingItem set IsActive=0")
con.execute("delete from RoutingItem where Remarks=?", (REMARKS,))
cols = ["Id", "Remarks", "Url", "RuleSet", "RuleNum", "Enabled", "Locked", "CustomIcon", "CustomRulesetPath4Singbox", "DomainStrategy", "DomainStrategy4Singbox", "Sort", "IsActive"]
vals = [rid(), REMARKS, None, json.dumps(rules, ensure_ascii=False), len(rules), 1, 0, None, None, "AsIs", "", 0, 1]
con.execute(f"insert into RoutingItem ({','.join(cols)}) values ({','.join(['?'] * len(cols))})", vals)
con.commit()
print(f"Created and activated routing profile: {REMARKS}")
print("Restart v2rayN/core to regenerate configs.")
