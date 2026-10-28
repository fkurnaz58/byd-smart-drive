#!/usr/bin/env python3
"""Türkiye benzinlikleri (OpenStreetMap, Overpass) -> data/fuel-tr.json (küçük biçim).

Araçtan Overpass'a doğrudan sorgu sık sık yanıtsız kaldığı için liste burada her gece hazırlanır.
Çıktı: {"at": unix, "s": [[lat, lon, ad], ...]}
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "fuel-tr.json"
Q = ('[out:json][timeout:600];area["ISO3166-1"="TR"][admin_level=2]->.a;'
     '(node["amenity"="fuel"](area.a);way["amenity"="fuel"](area.a););out center tags;')
SERVERS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
           "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]


def fetch():
    body = urllib.parse.urlencode({"data": Q}).encode()
    last = None
    for srv in SERVERS:
        for _ in range(2):
            try:
                req = urllib.request.Request(srv, data=body, headers={"User-Agent": "byd-smart-drive-data"})
                with urllib.request.urlopen(req, timeout=700) as r:
                    return json.load(r)
            except Exception as e:  # sıradaki sunucu
                last = e
                time.sleep(20)
    raise SystemExit("overpass failed: %s" % last)


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else fetch()
    rows = []
    for e in data.get("elements", []):
        t = e.get("tags") or {}
        lat = e.get("lat", (e.get("center") or {}).get("lat"))
        lon = e.get("lon", (e.get("center") or {}).get("lon"))
        if lat is None or lon is None:
            continue
        name = (t.get("name") or t.get("brand") or t.get("operator") or "").strip()
        rows.append([round(lat, 5), round(lon, 5), name])
    if len(rows) < 3000:
        sys.exit("too few fuel stations: %d" % len(rows))
    rows.sort()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"at": int(time.time()), "s": rows}, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print("fuel:", len(rows))


if __name__ == "__main__":
    main()
