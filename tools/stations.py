#!/usr/bin/env python3
"""Türkiye halka açık şarj istasyonları (EPDK verisi) -> data/stations-tr.json (küçük biçim).

Kaynak: EPDK Şarj Serbest Erişim Platformu verisini her gece yayımlayan açık depo
(github.com/Bozkorde/TURKIYE-EPDK-CHARGE-STATIONS, stations.json). EPDK'ya doğrudan istek atılmaz.
Çıktı: {"at": unix, "s": [[lat, lon, marka, ad, acKw, dcKw, acAdet, dcAdet], ...]}
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

SRC = "https://raw.githubusercontent.com/Bozkorde/TURKIYE-EPDK-CHARGE-STATIONS/main/stations.json"
OUT = Path(__file__).resolve().parent.parent / "data" / "stations-tr.json"


def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else None
    if raw:
        data = json.load(open(raw, encoding="utf-8"))
    else:
        req = urllib.request.Request(SRC, headers={"User-Agent": "byd-smart-drive-data"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
    rows = []
    for s in data:
        lat, lon = s.get("lat"), s.get("lng")
        if lat is None or lon is None:
            continue
        dc = max(s.get("dcGuc") or 0, s.get("chademoGuc") or 0)
        rows.append([round(lat, 5), round(lon, 5), (s.get("marka") or "").strip(),
                     (s.get("officialName") or "").strip(), s.get("acGuc") or 0, dc,
                     s.get("acAdet") or 0, (s.get("dcAdet") or 0) + (s.get("chademoAdet") or 0)])
    if len(rows) < 5000:
        sys.exit("too few stations: %d" % len(rows))
    rows.sort()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"at": int(time.time()), "s": rows}, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print("stations:", len(rows))


if __name__ == "__main__":
    main()
