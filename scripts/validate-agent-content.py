#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; CONTENT=ROOT/"content/agents"; OUTPUT=ROOT/"output"
REQUIRED=["title","custom_url","description","excerpt","seo_title","seo_description","keywords","featured_image","categories","tags","order","last_updated","source_url"]

def fields(path):
    text=path.read_text(); block=text.split("---",2)[1] if text.startswith("---") else ""; values={}
    for line in block.splitlines():
        if ":" in line: key,value=line.split(":",1); values[key.strip()]=value.strip()
    return values,text

def main():
    errors=[]; state=json.loads((CONTENT/".sync-state.json").read_text()); sets=state.get("sets",{})
    for set_id in ("chain-of-command","webops"):
        slugs=sets.get(set_id,[])
        if len(slugs)!=28 or len(slugs)!=len(set(slugs)): errors.append(f"{set_id}: expected 28 unique managed slugs")
        for slug in slugs:
            path=CONTENT/f"{slug}.md"
            if not path.is_file(): errors.append(f"{set_id}: missing {slug}.md"); continue
            meta,text=fields(path)
            for field in REQUIRED:
                if not meta.get(field): errors.append(f"{slug}: missing {field}")
            expected=f"/kujo-agents/blob/main/{set_id}/{slug}/AGENT.md"
            if expected not in meta.get("source_url",""): errors.append(f"{slug}: wrong canonical source URL")
            if not re.search(r"^last_updated: \d{4}-\d{2}-\d{2}$",text,re.M): errors.append(f"{slug}: invalid last_updated")
            if set_id=="webops":
                if meta.get("categories")!='["WebOps"]': errors.append(f"{slug}: wrong WebOps category")
                if re.search(r"(?i)coming soon|lorem ipsum|placeholder",text): errors.append(f"{slug}: placeholder content")
            expected_portrait=f'"content/media/agents/{slug}.webp"'
            if meta.get("featured_image")!=expected_portrait: errors.append(f"{slug}: wrong agent portrait")
            portrait=ROOT/expected_portrait.strip('"')
            if not portrait.is_file(): errors.append(f"{slug}: agent portrait file missing")
            route=OUTPUT/"agents"/slug/"index.html"
            if OUTPUT.is_dir() and not route.is_file(): errors.append(f"{slug}: generated route missing")
    if OUTPUT.is_dir():
        for route in (OUTPUT/"index.html",OUTPUT/"agents/index.html",OUTPUT/"agents/chain-of-command/index.html",OUTPUT/"agents/webops/index.html",OUTPUT/"sitemap.xml",OUTPUT/"llms.txt"):
            if not route.is_file(): errors.append(f"generated output missing: {route.relative_to(ROOT)}")
    if errors:
        print(json.dumps({"valid":False,"errors":errors},indent=2)); return 1
    print(json.dumps({"valid":True,"chain_of_command":28,"webops":28,"individual_routes":56},indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
