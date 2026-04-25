#!/usr/bin/env python3
import json
from pathlib import Path

base = Path.home() / '.local/share/v2rayN'
gui = base / 'guiConfigs/guiNConfig.json'
srs = base / 'bin/srss'
configs = [base / 'binConfigs/configPre.json', base / 'binConfigs/config.json']

wanted = [
    'geosite-ru-blocked','geoip-ru-blocked','geosite-gfw','geosite-greatfire',
    'geoip-telegram','geoip-twitter','geoip-facebook','geoip-google',
]
for cand in ['geosite-twitch', 'geoip-twitch']:
    if (srs / f'{cand}.srs').exists():
        wanted.append(cand)

if gui.exists():
    g = json.load(open(gui))
    t = g.setdefault('TunModeItem', {})
    t.update({'EnableTun': True, 'AutoRoute': True, 'StrictRoute': True, 'Mtu': 1500, 'EnableIPv6Address': False})
    g.setdefault('SystemProxyItem', {})['SysProxyType'] = 0
    sd = g.setdefault('SimpleDNSItem', {})
    sd.update({'FakeIP': True, 'GlobalFakeIp': True, 'RemoteDNS': 'tls://1.1.1.1,tls://8.8.8.8', 'DirectDNS': '1.1.1.1', 'BootstrapDNS': '1.1.1.1'})
    for item in g.get('CoreTypeItem', []):
        if item.get('ConfigType') == 5:  # VLESS
            item['CoreType'] = 24       # sing_box
    json.dump(g, open(gui, 'w'), indent=2, ensure_ascii=False)

steam_name_rule = {'outbound': 'direct', 'process_name': ['steam','steamwebhelper','steam-runtime-steam-remote','dota2','dota2_linux']}
steam_path_rule = {'outbound': 'direct', 'process_path_regex': [r'^/home/kcnc/\.steam/(root|steam|debian-installation)/steamapps/common/.+']}

def patch(path: Path):
    if not path.exists():
        return False
    data = json.load(open(path))
    # TUN MTU
    for inbound in data.get('inbounds', []):
        if inbound.get('type') == 'tun':
            inbound.update({'mtu': 1500, 'auto_route': True, 'strict_route': True})
    # DNS only if sing-box style dict servers
    if isinstance(data.get('dns'), dict) and isinstance(data['dns'].get('servers'), list):
        servers = [x for x in data['dns']['servers'] if isinstance(x, dict)]
        hosts = [x for x in servers if x.get('type') == 'hosts']
        fake = [x for x in servers if x.get('type') == 'fakeip']
        data['dns']['servers'] = [
            {'server':'1.1.1.1','type':'udp','tag':'local_local'},
            {'server':'1.1.1.1','server_port':853,'type':'tls','tag':'remote_dns','detour':'proxy'},
            {'server':'8.8.8.8','server_port':853,'type':'tls','tag':'remote_dns_google','detour':'proxy'},
            {'server':'1.1.1.1','type':'udp','tag':'direct_dns'},
        ] + hosts + fake
        data['dns']['final'] = 'remote_dns'
    route = data.setdefault('route', data.get('route', {}))
    if not route:
        json.dump(data, open(path,'w'), indent=2, ensure_ascii=False); return True
    rs = route.setdefault('rule_set', [])
    existing = {r.get('tag') for r in rs if isinstance(r, dict)}
    present=[]; missing=[]
    for tag in wanted:
        f = srs / f'{tag}.srs'
        if f.exists():
            present.append(tag)
            if tag not in existing:
                rs.append({'tag':tag,'type':'local','format':'binary','path':str(f)})
        else:
            missing.append(tag)
    rules = route.setdefault('rules', [])
    # remove our prior steam and aggregate rules
    rules = [r for r in rules if not (r.get('outbound') == 'direct' and (('steam' in r.get('process_name', [])) or any('steamapps/common' in x for x in r.get('process_path_regex', []))))]
    rules = [r for r in rules if not (r.get('outbound') == 'proxy' and set(r.get('rule_set', [])) == set(present))]
    # insert steam after sniff if exists, else after core-direct rules
    insert_at = 0
    for i,r in enumerate(rules):
        if r.get('action') == 'sniff':
            insert_at = i + 1; break
    rules.insert(insert_at, steam_path_rule)
    rules.insert(insert_at, steam_name_rule)
    # insert blocked proxy before geoip-ru direct, else before catch-all/final
    proxy_rule = {'outbound':'proxy','rule_set':present}
    idx = None
    for i,r in enumerate(rules):
        if r.get('outbound') == 'direct' and 'geoip-ru' in r.get('rule_set', []): idx=i; break
    if idx is None:
        for i,r in enumerate(rules):
            if r.get('outbound') == 'proxy' and (r.get('port_range') or r.get('port')): idx=i; break
    if idx is None: rules.append(proxy_rule)
    else: rules.insert(idx, proxy_rule)
    route['rules'] = rules
    route['final'] = 'proxy'
    json.dump(data, open(path,'w'), indent=2, ensure_ascii=False)
    print(f'Applied to {path}')
    print('Proxied:', ', '.join(present))
    if missing: print('Missing:', ', '.join(missing))
    return True

for c in configs:
    patch(c)
