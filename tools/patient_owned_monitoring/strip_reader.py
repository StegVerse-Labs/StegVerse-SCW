#!/usr/bin/env python3
"""Calibrate and read colorimetric pads from measured RGB values."""
from __future__ import annotations
import argparse, csv, json, math

def dist(a,b): return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def load_cal(path):
    with open(path,newline="",encoding="utf-8") as f:
        return [{**r,"rgb":(float(r["r"]),float(r["g"]),float(r["b"]))} for r in csv.DictReader(f)]
def main():
    p=argparse.ArgumentParser(); p.add_argument("calibration_csv"); p.add_argument("--r",type=float,required=True); p.add_argument("--g",type=float,required=True); p.add_argument("--b",type=float,required=True); p.add_argument("--analyte",required=True); a=p.parse_args()
    rows=[r for r in load_cal(a.calibration_csv) if r["analyte"]==a.analyte]; target=(a.r,a.g,a.b); ranked=sorted(((dist(target,r["rgb"]),r) for r in rows),key=lambda x:x[0]); best=ranked[0]
    out={"schema_version":"pom.strip-reading.v1","analyte":a.analyte,"measured_rgb":target,"nearest_label":best[1]["label"],"nearest_value":best[1].get("value"),"unit":best[1].get("unit"),"rgb_distance":best[0],"output_label":"calculated","algorithm":{"name":"nearest-calibrated-rgb","version":"0.1.0"}}
    print(json.dumps(out,separators=(",", ":")))
if __name__=="__main__":main()
