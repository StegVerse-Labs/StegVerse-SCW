#!/usr/bin/env python3
"""Create append-only fluid-sample records with hashes and chain-of-custody entries."""
from __future__ import annotations
import argparse, hashlib, json, uuid
from datetime import datetime, timezone

def digest(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("output_jsonl"); p.add_argument("--sample-type",required=True,choices=["saliva","urine","capillary-blood","blood-smear","microhematocrit"]); p.add_argument("--method",required=True); p.add_argument("--mass-g",type=float); p.add_argument("--volume-ml",type=float); p.add_argument("--lot",action="append",default=[]); p.add_argument("--image",action="append",default=[]); a=p.parse_args()
    now=datetime.now(timezone.utc).isoformat(); rec={"schema_version":"pom.sample.v1","sample_id":str(uuid.uuid4()),"sample_type":a.sample_type,"collection_start_utc":now,"collection_end_utc":now,"collection_method":a.method,"container_tare_g":None,"sample_mass_g":a.mass_g,"sample_volume_ml":a.volume_ml,"lot_ids":a.lot,"image_refs":a.image,"chain_of_custody":[{"time_utc":now,"action":"created","actor":"operator"}]}; rec["sample_sha256"]=digest(rec)
    with open(a.output_jsonl,"a",encoding="utf-8") as f:f.write(json.dumps(rec,separators=(",", ":"))+"\n")
    print(json.dumps(rec))
if __name__=="__main__":main()
