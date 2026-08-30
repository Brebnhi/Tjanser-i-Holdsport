#!/usr/bin/env python3
"""Bygger et test-feed i volleyball.dk's format ud fra tjanselisten, med
bevidst indbyggede afvigelser, så pipelinen kan afprøves."""
import csv, os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
DK = ZoneInfo("Europe/Copenhagen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# AFVIG=1 indbygger en flyttet kamp, en forsvundet kamp og en hjemmekamp uden tjans
AFVIG = os.environ.get("AFVIG", "0") == "1"

PULJE = {"Volleyligaen Kvinder": "VLK", "1. Division Herrer": "Vest",
         "1. Division Kvinder": "Vest", "2. Division Herrer": "Nord",
         "2. Division Kvinder": "Nord"}

# Afvigelser vi vil se pipelinen fange:
FLYTTET = {"148188": timedelta(days=7, hours=2)} if AFVIG else {}
FJERNET = {"148670"} if AFVIG else set()
EKSTRA = [("148999", "2. Division Herrer", "Nord", "Aalborg Volleyball.2",
           "Nyt Hold IF", "Aalborg Stadionhal 1",
           datetime(2027, 5, 8, 12, 0, tzinfo=DK))] if AFVIG else []

def ev(nr, raekke, pulje, hjemme, ude, sted, start, runde=9):
    end = start + timedelta(hours=1, minutes=30)
    f = "%Y%m%dT%H%M%SZ"
    from datetime import timezone
    desc = (f"{raekke} {pulje}\\nRunde {runde}\\nKampnr {nr}\\n\\n{hjemme} - {ude}\\n"
            f"{sted}\\nAnnebergvej  48\\n9000 Aalborg\\n{start.strftime('%d-%m-%Y %H:%M')}")
    return "\r\n".join([
        "BEGIN:VEVENT", "PRODID:-//DBU//DA", f"UID:item_{nr}",
        f"DTSTART:{start.astimezone(timezone.utc).strftime(f)}",
        f"DTEND:{end.astimezone(timezone.utc).strftime(f)}",
        f"SUMMARY:{hjemme} - {ude}", f"DESCRIPTION:{desc}", f"LOCATION:{sted}",
        "X-MICROSOFT-CDO-BUSYSTATUS:BUSY", "X-MICROSOFT-CDO-IMPORTANCE:1",
        "BEGIN:VALARM", "TRIGGER:-PT2H", "ACTION:DISPLAY",
        "DESCRIPTION:Reminder", "END:VALARM", "END:VEVENT"])

rows = [r for r in csv.DictReader(open(f"{ROOT}/data/tjanser.csv", encoding="utf-8"))
        if r["kampnr"]]
blocks = []
for r in rows:
    if r["kampnr"] in FJERNET:
        continue
    start = datetime.strptime(f"{r['dato']} {r['tid']}", "%d-%m-%y %H:%M").replace(tzinfo=DK)
    start += FLYTTET.get(r["kampnr"], timedelta())
    blocks.append(ev(r["kampnr"], r["raekke"], PULJE.get(r["raekke"], ""),
                     r["hjemmehold"], r["udehold"], r["spillested"], start))
for nr, raekke, pulje, hj, ud, sted, start in EKSTRA:
    blocks.append(ev(nr, raekke, pulje, hj, ud, sted, start))
# et par udekampe, som ikke må give tjanser
blocks.append(ev("148195", "1. Division Herrer", "Vest", "Kolding VK",
                 "Aalborg Volleyball", "Bakkeskolens hal",
                 datetime(2026, 10, 25, 16, 0, tzinfo=DK)))
blocks.append(ev("149261", "Volleyligaen Kvinder", "VLK", "Ikast KFUM", "Holte IF",
                 "Sportscenter Ikast Hal A", datetime(2026, 10, 9, 18, 30, tzinfo=DK)))

cal = "\r\n".join(["BEGIN:VCALENDAR", "VERSION:2.0", "METHOD:PUBLISH",
                   "CALSCALE:GREGORIAN", "PRODID:-//VD//VD Aalborg VolleyballKAMPE//DK",
                   "X-WR-CALNAME:VD Aalborg Volleyball kampe",
                   "X-WR-TIMEZONE:Europe/Copenhagen"] + blocks + ["END:VCALENDAR"]) + "\r\n"
os.makedirs(f"{ROOT}/test/fixtures", exist_ok=True)
open(f"{ROOT}/test/fixtures/alle.ics", "w", encoding="utf-8").write(cal)
print(f"testfeed: {cal.count('BEGIN:VEVENT')} events fra {len(rows)} kampe i arket"
      + (" (1 flyttet, 1 fjernet, 1 ekstra hjemmekamp)" if AFVIG else " (uden afvigelser)")
      + ", plus 2 udekampe")
