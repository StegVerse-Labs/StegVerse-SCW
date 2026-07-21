#!/usr/bin/env python3
"""Generate synchronized synthetic wearable streams and append-only JSONL frames."""
from __future__ import annotations
import argparse, hashlib, json, math, random, uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def generate(duration_s:int, sample_rate:int, heart_rate:float, seed:int):
    random.seed(seed); session=str(uuid.uuid4()); start=datetime.now(timezone.utc)
    rows=[]
    for i in range(duration_s*sample_rate):
        t=i/sample_rate; phase=2*math.pi*(heart_rate/60.0)*t
        ecg=0.08*math.sin(phase)+1.2*math.exp(-((phase%(2*math.pi))-0.25)**2/0.002)+random.gauss(0,0.01)
        delay=0.18; pphase=2*math.pi*(heart_rate/60.0)*max(0,t-delay)
        ppg=0.5+0.35*max(0,math.sin(pphase))**2+random.gauss(0,0.005)
        accel=0.02+random.gauss(0,0.004)
        rows.append({"session_id":session,"sequence":i,"time_utc":(start+timedelta(seconds=t)).isoformat(),"ecg_mv":ecg,"ppg_ir":ppg,"accel_g":accel,"skin_temp_c":33.2+0.05*math.sin(t/60),"contact_kpa":2.0+random.gauss(0,0.03)})
    return session, rows

def main():
    p=argparse.ArgumentParser(); p.add_argument("output"); p.add_argument("--duration",type=int,default=60); p.add_argument("--rate",type=int,default=100); p.add_argument("--heart-rate",type=float,default=72); p.add_argument("--seed",type=int,default=7); a=p.parse_args()
    session,rows=generate(a.duration,a.rate,a.heart_rate,a.seed); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("a",encoding="utf-8") as f:
        for r in rows:
            rec={"schema_version":"pom.synthetic-sample.v1",**r}; rec["record_sha256"]=sha(rec); f.write(json.dumps(rec,separators=(",", ":"))+"\n")
    print(json.dumps({"session_id":session,"samples":len(rows),"output":str(out)}))
if __name__=="__main__": main()
