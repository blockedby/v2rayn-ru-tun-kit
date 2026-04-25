# v2rayN RU TUN Kit

Reusable helper scripts for v2rayN on Linux/Kubuntu with sing-box TUN mode, aimed at Russia censorship-resistance while keeping Russian/local/Steam traffic direct.

## What it does

The main script patches v2rayN generated sing-box configs:

- `~/.local/share/v2rayN/binConfigs/config.json`
- `~/.local/share/v2rayN/binConfigs/configPre.json`

It applies:

- TUN MTU `1500`
- TUN `auto_route=true`, `strict_route=true`
- system proxy disabled in GUI config
- FakeIP enabled in GUI config
- VLESS default core type set to `sing_box` in GUI config
- DNS-over-TLS through proxy:
  - Cloudflare `1.1.1.1:853`
  - Google `8.8.8.8:853`
- Proxy these local SRS rule sets when present:
  - `geosite-ru-blocked`
  - `geoip-ru-blocked`
  - `geosite-gfw`
  - `geosite-greatfire`
  - `geoip-telegram`
  - `geoip-twitter`
  - `geoip-facebook`
  - `geoip-google`
  - `geosite-twitch` / `geoip-twitch` if available
- Keep `geoip-ru` direct after blocked/free-speech proxy rules
- Keep bittorrent direct if v2rayN generated that builtin rule
- Steam/Dota/all Steam library games direct by process/path:
  - `steam`
  - `steamwebhelper`
  - `steam-runtime-steam-remote`
  - `dota2`, `dota2_linux`
  - `~/.steam/{root,steam,debian-installation}/steamapps/common/...`

## Install

```bash
cd ~/code/tools/v2rayn-ru-tun-kit
./scripts/install.sh
```

This installs:

```bash
~/.local/share/v2rayN/binConfigs/pi-apply-ru-tun-rules.py
```

## Backup first

```bash
~/code/tools/v2rayn-ru-tun-kit/scripts/backup-v2rayn-configs.sh
```

It prints a backup directory and creates a `restore.sh` inside it.


## Create flat v2rayN routing profile

To avoid ambiguous combined rules, create an active flat GUI routing profile:

```bash
~/code/tools/v2rayn-ru-tun-kit/scripts/backup-v2rayn-configs.sh
~/code/tools/v2rayn-ru-tun-kit/scripts/create-flat-routing-profile.py
```

Then restart v2rayN/core. The created profile is named:

```text
RUv2-flat-steam-direct-free-speech
```

It uses separate rules so fields do not accidentally combine with AND semantics.

## Apply after v2rayN restart/regeneration

v2rayN often regenerates `config.json` / `configPre.json`. After switching node, changing routing, restarting core, or updating subscription, run:

```bash
~/.local/share/v2rayN/binConfigs/pi-apply-ru-tun-rules.py
```

Then restart the v2rayN core from GUI if needed.

## Check state

```bash
~/code/tools/v2rayn-ru-tun-kit/scripts/check-v2rayn-state.sh
```

Also useful:

```bash
curl https://ifconfig.me
curl https://cloudflare.com/cdn-cgi/trace
ps aux | grep -i '[x]ray\|[s]ing-box\|[v]2rayN'
```

Expected for native sing-box VLESS backend:

```text
sing-box run -c .../binConfigs/config.json
```

If you see `xray run -c config.json`, your selected node/default core is still Xray.


### Current Steam/Dota bypass strings

Use these as flat direct process rules in v2rayN:

```text
steam
steamwebhelper
steam-runtime-steam-remote
dota2
dota2_linux
```

And as a separate direct process rule for Steam library folders / Dota exact paths:

```text
/home/kcnc/.steam/debian-installation/steamapps/common/
/home/kcnc/.steam/root/steamapps/common/
/home/kcnc/.steam/steam/steamapps/common/
/home/kcnc/.steam/debian-installation/steamapps/common/dota 2 beta/game/bin/linuxsteamrt64/dota2
/home/kcnc/.steam/root/steamapps/common/dota 2 beta/game/bin/linuxsteamrt64/dota2
/home/kcnc/.steam/steam/steamapps/common/dota 2 beta/game/bin/linuxsteamrt64/dota2
```

Keep these above final/catch-all proxy rules.

## Rule precedence

sing-box uses first-match-wins routing. Intended order:

1. v2rayN/sing-box/Xray anti-loop builtin rules
2. Steam/Dota/Steam games direct
3. DNS hijack/sniff builtin rules
4. bittorrent direct
5. ads block
6. LAN/private direct
7. ru-blocked/gfw/greatfire/social/google proxy
8. `geoip-ru` direct
9. final proxy

## Notes

This is a generated-config hot-patch kit. v2rayN can overwrite generated configs, so rerun the apply script after v2rayN config changes.

For a durable GUI-only setup, recreate equivalent rules in v2rayN routing profiles/templates.
