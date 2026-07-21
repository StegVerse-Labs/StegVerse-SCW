#!/usr/bin/env python3
"""Detect sustained personal-baseline hemodynamic change events from transparent features."""
from __future__ import annotations
import argparse, csv, json, uuid
from datetime import datetime

def load(path):
    with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
def f(row,key):
    try:return float(row[key])
    except:return None
def detect(rows, threshold=2.5, min_seconds=5.0):
    events=[]; active=None
    for r in rows:
        score=f(r,"relative_change_index"); t=datetime.fromisoformat(r["time_utc"].replace("Z","+00:00"))
        crossed=score is not None and score>=threshold
        if crossed and active is None: active={"start":t,"start_row":r,"peak":score}
        elif crossed and active: active["peak"]=max(active["peak"],score)
        elif not crossed and active:
            dur=(t-active["start"]).total_seconds()
            if dur>=min_seconds:
                events.append({"schema_version":"pom.event.v1","event_id":str(uuid.uuid4()),"event_type":"hemodynamic-collapse-candidate","start_time_utc":active["start"].isoformat(),"end_time_utc":t.isoformat(),"duration_seconds":dur,"peak_relative_change_index":active["peak"],"timestamp_source":"algorithm","output_label":"experimentally_inferred","algorithm":{"name":"personal-threshold-collapse-detector","version":"0.1.0","threshold":threshold,"minimum_duration_seconds":min_seconds}})
            active=None
    return events

def main():
    p=argparse.ArgumentParser(); p.add_argument("features_csv"); p.add_argument("output_jsonl"); p.add_argument("--threshold",type=float,default=2.5); p.add_argument("--minimum-seconds",type=float,default=5); a=p.parse_args(); events=detect(load(a.features_csv),a.threshold,a.minimum_seconds)
    with open(a.output_jsonl,"w",encoding="utf-8") as f:
        for e in events:f.write(json.dumps(e,separators=(",", ":"))+"\n")
    print(json.dumps({"events":len(events),"output":a.output_jsonl}))
if __name__=="__main__":main()
