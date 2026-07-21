#!/usr/bin/env python3
"""Correlate awakening or mouth-opening markers with synchronized PAP evidence windows."""
from __future__ import annotations
import argparse, csv, json, statistics
from datetime import datetime

def t(v): return datetime.fromisoformat(v.replace("Z","+00:00")).timestamp()
def read_csv(path):
    with open(path,newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def read_events(path):
    with open(path,encoding="utf-8") as f:return [json.loads(x) for x in f if x.strip()]
def num(row,key):
    try:return float(row[key])
    except:return None
def summarize(rows):
    out={}
    for key in ["spo2","pulse_bpm","mask_pressure_cmh2o","mask_humidity_pct","room_humidity_pct","respiration_rpm","jaw_open"]:
        vals=[num(r,key) for r in rows]; vals=[v for v in vals if v is not None]
        out[key]={"count":len(vals),"minimum":min(vals) if vals else None,"maximum":max(vals) if vals else None,"mean":statistics.fmean(vals) if vals else None}
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument("pap_csv"); p.add_argument("events_jsonl"); p.add_argument("output_jsonl"); p.add_argument("--before",type=float,default=300); p.add_argument("--after",type=float,default=300); a=p.parse_args()
    rows=read_csv(a.pap_csv); events=read_events(a.events_jsonl); reports=[]
    for e in events:
        center=t(e["start_time_utc"]); win=[r for r in rows if center-a.before<=t(r["time_utc"])<=center+a.after]
        reports.append({"schema_version":"pom.pap-event-correlation.v1","event_id":e.get("event_id"),"event_type":e.get("event_type"),"event_time_utc":e["start_time_utc"],"window_before_seconds":a.before,"window_after_seconds":a.after,"sample_count":len(win),"summary":summarize(win)})
    with open(a.output_jsonl,"w",encoding="utf-8") as f:
        for r in reports:f.write(json.dumps(r,separators=(",", ":"))+"\n")
    print(json.dumps({"events":len(reports),"output":a.output_jsonl}))
if __name__=="__main__":main()
