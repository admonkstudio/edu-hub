#!/usr/bin/env python3
"""
Edu Hub Egypt raw education-institution acquisition database.

Purpose:
- preserve source records BEFORE canonical modelling
- retain provenance and raw payloads
- expose field census and source coverage
- never merge or overwrite source facts

Outputs:
  edu_hub_egypt_raw.sqlite
  source_counts.csv
  field_inventory.csv
  coverage.csv
  acquisition_summary.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

USER_AGENT = "EduHubResearchBot/0.1 (+https://github.com/admonkstudio/edu-hub; source-acquisition)"
RETRIEVED_AT = datetime.now(timezone.utc).isoformat()

SOURCES = [
    dict(source_id="scu_official_snapshot", name="Supreme Council of Universities official lists — source-backed snapshot", url="https://scu.eg/en/universities-and-institutions/", source_type="official_registry", authority="primary", notes="327 source-backed higher-education identities collected from SCU category pages; stored unchanged as snapshot CSV."),
    dict(source_id="osm_geofabrik_egypt", name="OpenStreetMap Egypt — Geofabrik extract", url="https://download.geofabrik.de/africa/egypt.html", source_type="open_geodata", authority="secondary", notes="Current OSM education POIs/polygons. Useful for discovery and coordinates; not proof of regulatory status."),
    dict(source_id="egyptschools_github_excel", name="EgyptSchools.info Cairo/Giza scrape — public GitHub Excel", url="https://github.com/Mohmedashraf67/EgyptionSchools-Excel", source_type="secondary_directory_snapshot", authority="secondary", notes="Repository README says data was scraped from egyptschools.info for Cairo/Giza. Preserve source attribution."),
    dict(source_id="emis_getdata_2022", name="Historical EMIS school-directory scrape — GetData.io", url="https://getdata.io/data-sources/113429-%D8%AF%D9%84%D9%8A%D9%84-%D8%A7%D9%84%D9%85%D8%AF%D8%A7%D8%B1%D8%B3-%D8%A7%D9%84%D9%85%D8%B5%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D9%85%D8%AF%D8%A7%D8%B1%D8%B3-%D8%A7%D9%84%D8%AA%D8%AC%D8%B1%D8%A8%D9%8A%D8%A9", source_type="historical_official_directory_snapshot", authority="secondary_snapshot_of_primary", notes="Captured from search.emis.gov.eg in 2022. Stale by design; use for discovery/matching, never current verification."),
]

COVERAGE_TARGETS = [
    ("moe_schools", "Ministry of Education schools", 62690, "official aggregate 2025/26", "https://emis.gov.eg/"),
    ("moss_nurseries", "MOSS nurseries", 48225, "national census 2025, current ministry figure", "https://moss.gov.eg/"),
    ("azhar_institutes", "Al-Azhar institutes", None, "separate official directory; target count to be resolved from current source", "https://azhar.gov.eg/IDSC/InstGuide/Guide_Search.aspx"),
    ("higher_ed", "Higher-education institutions", None, "multiple overlapping official categories; coverage measured per registry/category, not a single naive total", "https://scu.eg/en/universities-and-institutions/"),
]

def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=4, backoff_factor=1.0, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": USER_AGENT})
    return s

HTTP = session()

def download(url: str, timeout: int = 90) -> bytes:
    r = HTTP.get(url, timeout=timeout)
    r.raise_for_status()
    return r.content

def norm_key(k: Any) -> str:
    return re.sub(r"\s+", " ", str(k or "").strip())

def clean(v: Any) -> Any:
    try:
        if pd.isna(v): return None
    except Exception:
        pass
    if isinstance(v, float) and v.is_integer(): return int(v)
    if isinstance(v, (str, int, float, bool)) or v is None: return v
    return str(v)

def flatten_coords(obj: Any) -> list[tuple[float, float]]:
    out = []
    if isinstance(obj, list):
        if len(obj) >= 2 and isinstance(obj[0], (int, float)) and isinstance(obj[1], (int, float)):
            out.append((float(obj[0]), float(obj[1])))
        else:
            for child in obj: out.extend(flatten_coords(child))
    return out

def centroid(geometry: dict | None) -> tuple[float | None, float | None]:
    if not geometry: return None, None
    pts = flatten_coords(geometry.get("coordinates"))
    if not pts: return None, None
    return sum(p[1] for p in pts)/len(pts), sum(p[0] for p in pts)/len(pts)

def choose(payload: dict, candidates: Iterable[str]) -> Any:
    lower = {str(k).strip().lower(): v for k, v in payload.items()}
    for c in candidates:
        if c.lower() in lower and lower[c.lower()] not in (None, "", "nan"): return lower[c.lower()]
    for c in candidates:
        cl = c.lower()
        for k, v in lower.items():
            if cl in k and v not in (None, "", "nan"): return v
    return None

def setup(db: sqlite3.Connection) -> None:
    db.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS sources (source_id TEXT PRIMARY KEY,name TEXT NOT NULL,url TEXT NOT NULL,source_type TEXT NOT NULL,authority TEXT NOT NULL,notes TEXT);
    CREATE TABLE IF NOT EXISTS acquisition_runs (run_id INTEGER PRIMARY KEY AUTOINCREMENT,source_id TEXT NOT NULL REFERENCES sources(source_id),started_at TEXT NOT NULL,finished_at TEXT,status TEXT NOT NULL,records_added INTEGER NOT NULL DEFAULT 0,error TEXT);
    CREATE TABLE IF NOT EXISTS raw_records (raw_id INTEGER PRIMARY KEY AUTOINCREMENT,source_id TEXT NOT NULL REFERENCES sources(source_id),source_record_id TEXT,entity_family TEXT NOT NULL,entity_type_raw TEXT,name_raw TEXT,name_ar_raw TEXT,name_en_raw TEXT,location_raw TEXT,latitude REAL,longitude REAL,source_url TEXT,retrieved_at TEXT NOT NULL,raw_hash TEXT NOT NULL,payload_json TEXT NOT NULL,UNIQUE(source_id,raw_hash));
    CREATE INDEX IF NOT EXISTS idx_raw_source ON raw_records(source_id);
    CREATE INDEX IF NOT EXISTS idx_raw_name ON raw_records(name_raw);
    CREATE INDEX IF NOT EXISTS idx_raw_family ON raw_records(entity_family);
    CREATE INDEX IF NOT EXISTS idx_raw_geo ON raw_records(latitude,longitude);
    CREATE TABLE IF NOT EXISTS field_inventory (source_id TEXT NOT NULL,field_path TEXT NOT NULL,populated_records INTEGER NOT NULL,distinct_sample_count INTEGER NOT NULL,example_values_json TEXT NOT NULL,PRIMARY KEY(source_id,field_path));
    CREATE TABLE IF NOT EXISTS coverage_targets (target_id TEXT PRIMARY KEY,label TEXT NOT NULL,official_count INTEGER,target_basis TEXT NOT NULL,reference_url TEXT NOT NULL);
    """)
    for s in SOURCES:
        db.execute("INSERT OR REPLACE INTO sources(source_id,name,url,source_type,authority,notes) VALUES(:source_id,:name,:url,:source_type,:authority,:notes)", s)
    db.executemany("INSERT OR REPLACE INTO coverage_targets(target_id,label,official_count,target_basis,reference_url) VALUES(?,?,?,?,?)", COVERAGE_TARGETS)
    db.commit()

def start_run(db, source_id):
    cur=db.execute("INSERT INTO acquisition_runs(source_id,started_at,status) VALUES(?,?,?)",(source_id,RETRIEVED_AT,"running")); db.commit(); return int(cur.lastrowid)

def finish_run(db, run_id, added, error=None):
    db.execute("UPDATE acquisition_runs SET finished_at=?,status=?,records_added=?,error=? WHERE run_id=?",(datetime.now(timezone.utc).isoformat(),"failed" if error else "completed",added,error,run_id)); db.commit()

def add_record(db, *, source_id, source_record_id, entity_family, entity_type_raw, name_raw, name_ar_raw=None, name_en_raw=None, location_raw=None, latitude=None, longitude=None, source_url=None, payload):
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,default=str); h=hashlib.sha256((source_id+"\n"+raw).encode()).hexdigest()
    try:
        db.execute("INSERT INTO raw_records(source_id,source_record_id,entity_family,entity_type_raw,name_raw,name_ar_raw,name_en_raw,location_raw,latitude,longitude,source_url,retrieved_at,raw_hash,payload_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(source_id,source_record_id,entity_family,entity_type_raw,name_raw,name_ar_raw,name_en_raw,location_raw,latitude,longitude,source_url,RETRIEVED_AT,h,raw)); return True
    except sqlite3.IntegrityError: return False

def ingest_higher_ed(db, path: Path):
    sid="scu_official_snapshot"; run=start_run(db,sid); added=0
    try:
        with path.open("r",encoding="utf-8-sig",newline="") as f:
            for row in csv.DictReader(f):
                payload={norm_key(k):(v if v!="" else None) for k,v in row.items()}
                added += add_record(db,source_id=sid,source_record_id=row.get("seed_id"),entity_family="higher_education",entity_type_raw=row.get("entity_type_proposed"),name_raw=row.get("name_ar"),name_ar_raw=row.get("name_ar"),source_url=row.get("source_url"),payload=payload)
        db.commit(); finish_run(db,run,added); return added
    except Exception as e: finish_run(db,run,added,repr(e)); raise

def ingest_excel(db, url):
    sid="egyptschools_github_excel"; run=start_run(db,sid); added=0
    try:
        content=download(url,120); xls=pd.ExcelFile(io.BytesIO(content))
        for sheet in xls.sheet_names:
            df=pd.read_excel(io.BytesIO(content),sheet_name=sheet)
            for i,r in df.iterrows():
                payload={norm_key(k):clean(v) for k,v in r.to_dict().items() if norm_key(k)}
                if not any(v not in (None,"") for v in payload.values()): continue
                name=choose(payload,["school","school name","name","اسم المدرسة","المدرسة"]); location=choose(payload,["place","area","district","governorate","location","المنطقة","المحافظة"]); kind=choose(payload,["type","school type","نوع المدرسة"]) or "school"
                added += add_record(db,source_id=sid,source_record_id=f"{sheet}:{i+2}",entity_family="pre_university",entity_type_raw=str(kind),name_raw=str(name) if name else None,location_raw=str(location) if location else None,source_url="https://github.com/Mohmedashraf67/EgyptionSchools-Excel/blob/main/Egyptian%20Schools.xlsx",payload={"sheet":sheet,**payload})
        db.commit(); finish_run(db,run,added); return added
    except Exception as e:
        finish_run(db,run,added,repr(e)); print(f"WARN Excel source failed: {e}",file=sys.stderr); return added

def ingest_getdata(db,url):
    sid="emis_getdata_2022"; run=start_run(db,sid); added=0
    try:
        content=download(url,90).decode("utf-8-sig",errors="replace")
        for idx,row in enumerate(csv.DictReader(io.StringIO(content)),start=1):
            payload={norm_key(k):(v.strip() if isinstance(v,str) else v) for k,v in row.items()}; name=payload.get("school")
            if not name: continue
            added += add_record(db,source_id=sid,source_record_id=str(idx),entity_family="pre_university",entity_type_raw=payload.get("type") or "school",name_raw=name,location_raw=payload.get("place"),source_url=payload.get("origin_url") or SOURCES[3]["url"],payload=payload)
        db.commit(); finish_run(db,run,added); return added
    except Exception as e:
        finish_run(db,run,added,repr(e)); print(f"WARN GetData source failed: {e}",file=sys.stderr); return added

def ingest_osm(db, geojsonseq: Path):
    sid="osm_geofabrik_egypt"; run=start_run(db,sid); added=0
    try:
        with geojsonseq.open("r",encoding="utf-8",errors="replace") as f:
            for line in f:
                if not line.strip(): continue
                feat=json.loads(line); props=feat.get("properties") or {}; geom=feat.get("geometry"); lat,lon=centroid(geom); amenity=props.get("amenity") or props.get("building") or "education"; name_ar=props.get("name:ar"); name_en=props.get("name:en"); name=props.get("name") or name_ar or name_en
                loc=[props.get(x) for x in ("addr:street","addr:suburb","addr:city","addr:state","addr:governorate") if props.get(x)]; source_rec=str(props.get("@id") or feat.get("id") or "")
                family="early_education" if amenity=="kindergarten" else ("higher_education" if amenity in ("college","university") else "pre_university")
                added += add_record(db,source_id=sid,source_record_id=source_rec or None,entity_family=family,entity_type_raw=str(amenity),name_raw=name,name_ar_raw=name_ar,name_en_raw=name_en,location_raw=" | ".join(map(str,loc)) or None,latitude=lat,longitude=lon,source_url=f"https://www.openstreetmap.org/{source_rec}" if source_rec else SOURCES[1]["url"],payload={"properties":props,"geometry":geom})
        db.commit(); finish_run(db,run,added); return added
    except Exception as e: finish_run(db,run,added,repr(e)); raise

def walk_fields(value,prefix=""):
    if isinstance(value,dict):
        for k,v in value.items(): yield from walk_fields(v,f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(value,list): yield prefix,value
    else: yield prefix,value

def rebuild_field_inventory(db):
    db.execute("DELETE FROM field_inventory")
    for (sid,) in db.execute("SELECT source_id FROM sources"):
        counts=Counter(); examples=defaultdict(list); distinct=defaultdict(set)
        for (payload_json,) in db.execute("SELECT payload_json FROM raw_records WHERE source_id=?",(sid,)):
            for path,val in walk_fields(json.loads(payload_json)):
                if not path or val in (None,"",[],{}): continue
                counts[path]+=1; sample=json.dumps(val,ensure_ascii=False,default=str) if isinstance(val,(dict,list)) else str(val)
                if len(distinct[path])<1000: distinct[path].add(sample)
                if len(examples[path])<5 and sample not in examples[path]: examples[path].append(sample[:500])
        for path,count in counts.items(): db.execute("INSERT INTO field_inventory(source_id,field_path,populated_records,distinct_sample_count,example_values_json) VALUES(?,?,?,?,?)",(sid,path,count,len(distinct[path]),json.dumps(examples[path],ensure_ascii=False)))
    db.commit()

def export_reports(db,outdir: Path):
    outdir.mkdir(parents=True,exist_ok=True)
    source_counts=list(db.execute("SELECT s.source_id,s.name,s.authority,COUNT(r.raw_id),SUM(CASE WHEN r.name_raw IS NOT NULL AND TRIM(r.name_raw)<>'' THEN 1 ELSE 0 END) FROM sources s LEFT JOIN raw_records r ON r.source_id=s.source_id GROUP BY s.source_id,s.name,s.authority ORDER BY COUNT(r.raw_id) DESC"))
    with (outdir/"source_counts.csv").open("w",encoding="utf-8-sig",newline="") as f: w=csv.writer(f); w.writerow(["source_id","source_name","authority","raw_records","named_records"]); w.writerows(source_counts)
    inv=list(db.execute("SELECT source_id,field_path,populated_records,distinct_sample_count,example_values_json FROM field_inventory ORDER BY source_id,populated_records DESC,field_path"))
    with (outdir/"field_inventory.csv").open("w",encoding="utf-8-sig",newline="") as f: w=csv.writer(f); w.writerow(["source_id","field_path","populated_records","distinct_sample_count","example_values_json"]); w.writerows(inv)
    coverage=list(db.execute("SELECT target_id,label,official_count,target_basis,reference_url FROM coverage_targets ORDER BY target_id"))
    with (outdir/"coverage.csv").open("w",encoding="utf-8-sig",newline="") as f: w=csv.writer(f); w.writerow(["target_id","label","official_count","target_basis","reference_url"]); w.writerows(coverage)
    summary={"generated_at":datetime.now(timezone.utc).isoformat(),"principle":"raw-first; no cross-source deduplication or canonical merging performed","raw_record_count":db.execute("SELECT COUNT(*) FROM raw_records").fetchone()[0],"named_raw_record_count":db.execute("SELECT COUNT(*) FROM raw_records WHERE name_raw IS NOT NULL AND TRIM(name_raw)<>''").fetchone()[0],"source_counts":[{"source_id":r[0],"source_name":r[1],"authority":r[2],"raw_records":r[3],"named_records":r[4]} for r in source_counts],"known_coverage_targets":[{"target_id":r[0],"label":r[1],"official_count":r[2],"basis":r[3],"url":r[4]} for r in coverage],"warning":"Raw record count is not unique-institution count. Duplicates across sources are intentionally preserved."}
    (outdir/"acquisition_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--db",default="artifacts/edu_hub_egypt_raw.sqlite"); ap.add_argument("--outdir",default="artifacts"); ap.add_argument("--higher-ed",default="tools/data-acquisition/seeds/scu_higher_ed_snapshot.csv"); ap.add_argument("--osm",default=""); ap.add_argument("--skip-network",action="store_true"); args=ap.parse_args()
    dbpath=Path(args.db); dbpath.parent.mkdir(parents=True,exist_ok=True); db=sqlite3.connect(dbpath); setup(db); counts={}
    counts["scu_official_snapshot"]=ingest_higher_ed(db,Path(args.higher_ed))
    if not args.skip_network:
        counts["egyptschools_github_excel"]=ingest_excel(db,"https://raw.githubusercontent.com/Mohmedashraf67/EgyptionSchools-Excel/main/Egyptian%20Schools.xlsx")
        counts["emis_getdata_2022"]=ingest_getdata(db,"https://cache.getdata.io/n113429_1fe6b6aa981ca9960e80c3f10bab0c70eses/latest_all.csv")
    if args.osm and Path(args.osm).exists(): counts["osm_geofabrik_egypt"]=ingest_osm(db,Path(args.osm))
    rebuild_field_inventory(db); export_reports(db,Path(args.outdir)); db.close(); print(json.dumps({"ok":True,"added":counts,"db":str(dbpath)},ensure_ascii=False))

if __name__=="__main__": main()
