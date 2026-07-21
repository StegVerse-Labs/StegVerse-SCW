#!/usr/bin/env python3
"""Extract simple, transparent ECG R peaks, PPG feet, HR and pulse-arrival time."""
from __future__ import annotations
import argparse, csv, json, statistics
from datetime import datetime

def load(path):
    with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
def ts(s): return datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
def local_max(values,i,w=2): return all(values[i]>=values[j] for j in range(max(0,i-w),min(len(values),i+w+1)))
def extract(rows,ecg_key="ecg_mv",ppg_key="ppg_ir",time_key="time_utc"):
    times=[ts(r[time_key]) for r in rows]; ecg=[float(r[ecg_key]) for r in rows]; ppg=[float(r[ppg_key]) for r in rows]
    ebase=statistics.median(ecg); eth=ebase+0.45*(max(ecg)-ebase)
    rpeaks=[i for i in range(2,len(ecg)-2) if ecg[i]>=eth and local_max(ecg,i)]
    beats=[]
    for k,i in enumerate(rpeaks):
        end=rpeaks[k+1] if k+1<len(rpeaks) else min(len(ppg),i+int(1.2/max(1e-6,times[1]-times[0])))
        if end<=i+2: continue
        segment=ppg[i:end]; foot=i+min(range(len(segment)),key=segment.__getitem__)
        pat_ms=(times[foot]-times[i])*1000
        rr=(times[i]-times[rpeaks[k-1]]) if k else None
        beats.append({"r_index":i,"ppg_foot_index":foot,"r_time_utc":rows[i][time_key],"ppg_foot_time_utc":rows[foot][time_key],"pulse_arrival_time_ms":pat_ms,"heart_rate_bpm":60/rr if rr and rr>0 else None})
    return beats

def main():
    p=argparse.ArgumentParser(); p.add_argument("input_csv"); p.add_argument("output_jsonl"); a=p.parse_args(); beats=extract(load(a.input_csv))
    with open(a.output_jsonl,"w",encoding="utf-8") as f:
        for b in beats: f.write(json.dumps({"schema_version":"pom.beat.v1",**b},separators=(",", ":"))+"\n")
    print(json.dumps({"beats":len(beats),"output":a.output_jsonl}))
if __name__=="__main__": main()
