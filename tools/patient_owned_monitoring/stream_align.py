#!/usr/bin/env python3
"""Align timestamped CSV streams to a shared grid and report timing quality."""
from __future__ import annotations
import argparse, csv, json, math
from datetime import datetime

def epoch(v): return datetime.fromisoformat(v.replace("Z","+00:00")).timestamp()
def read(path):
    with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader(f))
def nearest(rows,t,key):
    return min(rows,key=lambda r:abs(epoch(r[key])-t)) if rows else None
def main():
    p=argparse.ArgumentParser(); p.add_argument("stream_a"); p.add_argument("stream_b"); p.add_argument("output"); p.add_argument("--time-key",default="time_utc"); p.add_argument("--step-ms",type=float,default=10); p.add_argument("--max-offset-ms",type=float,default=25); a=p.parse_args()
    A,B=read(a.stream_a),read(a.stream_b); start=max(epoch(A[0][a.time_key]),epoch(B[0][a.time_key])); end=min(epoch(A[-1][a.time_key]),epoch(B[-1][a.time_key])); step=a.step_ms/1000
    aligned=[]; offsets=[]; t=start
    while t<=end:
        ra,rb=nearest(A,t,a.time_key),nearest(B,t,a.time_key); oa=abs(epoch(ra[a.time_key])-t)*1000; ob=abs(epoch(rb[a.time_key])-t)*1000
        if max(oa,ob)<=a.max_offset_ms:
            aligned.append({"grid_time_epoch":t,"a":ra,"b":rb,"a_offset_ms":oa,"b_offset_ms":ob}); offsets.extend([oa,ob])
        t+=step
    report={"schema_version":"pom.alignment-report.v1","grid_step_ms":a.step_ms,"aligned_count":len(aligned),"coverage":len(aligned)/max(1,math.floor((end-start)/step)+1),"mean_abs_offset_ms":sum(offsets)/len(offsets) if offsets else None,"max_abs_offset_ms":max(offsets) if offsets else None}
    with open(a.output,"w",encoding="utf-8") as f: json.dump({"report":report,"aligned":aligned},f,separators=(",", ":"))
    print(json.dumps(report))
if __name__=="__main__": main()
