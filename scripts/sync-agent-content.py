#!/usr/bin/env python3
"""Safely synchronize multiple canonical kujo-agents sets into Kujo SSG."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SITE_ROOT=Path(__file__).resolve().parents[1]
OUTPUT_ROOT=SITE_ROOT/"content/agents"
STATE_PATH=OUTPUT_ROOT/".sync-state.json"
CHAIN_ORDER=["general-commander","chief-of-staff","systems-architect","product-strategist","planner","spec-writer","research-analyst","risk-officer","core-developer","tooling-developer","frontend-developer","backend-developer","integration-engineer","code-reviewer","qa-lead","triage-agent","visual-qa-agent","release-verifier","security-reviewer","documentation-writer","context-packager","sitrep-agent","routine-worker","test-runner","lint-runner","issue-hygiene-worker","dependency-scanner","receipt-collector"]
SETS={
  "chain-of-command":{"source":"chain-of-command","category":"Chain of Command","tag_field":"Rank/layer","keywords":"Kujo agent, chain of command","order":CHAIN_ORDER,"catalog":None,"public_prefix":""},
  "webops":{"source":"webops","category":"WebOps","tag_field":"Category","keywords":"Kujo agent, WebOps, website operations","order":None,"catalog":"webops-catalog.json","public_prefix":""},
  "publishing-house":{"source":"publishing-house","category":"Publishing House","tag_field":"Desk","keywords":"Kujo agent, Publishing House, editorial operations","order":None,"catalog":"publishing-house-catalog.json","public_prefix":""},
  "videoops":{"source":"videoops","category":"VideoOps","tag_field":"Stage","keywords":"Kujo agent, VideoOps, video production","order":None,"catalog":"videoops-catalog.json","public_prefix":"videoops-"},
}
def field(body:str,name:str)->str:
    match=re.search(rf"^- {re.escape(name)}:\s*(.+)$",body,re.MULTILINE)
    if not match: raise ValueError(f"missing {name}")
    return match.group(1).strip()

def updated_date(repo:Path,contract:Path)->str:
    try:
        rel=contract.relative_to(repo)
        result=subprocess.run(["git","-C",str(repo),"log","-1","--format=%cs","--",str(rel)],text=True,capture_output=True,timeout=10)
        if result.returncode==0 and re.fullmatch(r"\d{4}-\d{2}-\d{2}",result.stdout.strip()): return result.stdout.strip()
    except (ValueError,OSError,subprocess.SubprocessError): pass
    return datetime.fromtimestamp(contract.stat().st_mtime,timezone.utc).date().isoformat()

def current_category(path:Path)->str:
    match=re.search(r'^categories:\s*\["([^"]+)"\]',path.read_text(encoding="utf-8"),re.M)
    return match.group(1) if match else ""

def source_order(source_root:Path,set_id:str,config:dict)->list[str]:
    if config["order"]: return config["order"]
    catalog=source_root/config["source"]/(config["catalog"] or "")
    if catalog.is_file(): return [x["slug"] for x in json.loads(catalog.read_text())["agents"]]
    return sorted(x.parent.name for x in (source_root/config["source"]).glob("*/AGENT.md"))

def sync_set(source_root:Path,set_id:str,state:dict)->tuple[int,list[str]]:
    config=SETS[set_id]; source_dir=source_root/config["source"]
    if not source_dir.is_dir(): raise ValueError(f"source directory not found: {source_dir}")
    contracts={x.parent.name:x for x in source_dir.glob("*/AGENT.md")}
    if not contracts: raise ValueError(f"no agent contracts found in: {source_dir}")
    order=source_order(source_root,set_id,config); order_by={slug:i for i,slug in enumerate(order,1)}
    missing=set(order)-set(contracts)
    if missing: raise ValueError(f"{set_id} order references missing contracts: {sorted(missing)}")
    generated=[]
    for slug in order:
        contract=contracts[slug]; body=contract.read_text(encoding="utf-8").strip(); heading,_,remainder=body.partition("\n")
        if not heading.startswith("# "): raise ValueError(f"missing title heading: {contract}")
        title=heading[2:].strip(); purpose=field(body,"Purpose"); tag=field(body,config["tag_field"])
        public_slug=config["public_prefix"]+slug
        portrait=f"content/media/agents/{public_slug}.webp"
        featured=portrait if (SITE_ROOT/portrait).is_file() else "assets/images/kujo-logomark.svg"
        source_url=f"https://github.com/kujolang/kujo-agents/blob/main/{config['source']}/{slug}/AGENT.md"
        frontmatter=["---",f"title: {json.dumps(title)}",f"custom_url: {json.dumps(public_slug)}",f"description: {json.dumps(purpose)}",f"excerpt: {json.dumps(purpose)}",f"seo_title: {json.dumps(title+' | Kujo '+config['category'])}",f"seo_description: {json.dumps(purpose)}",f"keywords: {json.dumps(config['keywords']+', '+title)}",f"featured_image: {json.dumps(featured)}",f"categories: [{json.dumps(config['category'])}]",f"tags: [{json.dumps(tag)}]",f"order: {order_by[slug]}",f"last_updated: {updated_date(source_root,contract)}",f"source_url: {json.dumps(source_url)}","---",""]
        remainder=re.sub(r"(^- (?:Required KUJO skills|WebOps domain skills|Existing Kujo skills):\s*)(.+)$",lambda m:m.group(1)+m.group(2).replace("`",""),remainder,flags=re.MULTILINE)
        destination=OUTPUT_ROOT/f"{public_slug}.md"; destination.write_text("\n".join(frontmatter)+remainder.lstrip()+"\n",encoding="utf-8"); generated.append(public_slug)
    previous=set(state.get("sets",{}).get(set_id,[]))
    if not previous:
        previous={path.stem for path in OUTPUT_ROOT.glob("*.md") if current_category(path)==config["category"]}
    for stale in sorted(previous-set(generated)):
        path=OUTPUT_ROOT/f"{stale}.md"
        if path.is_file() and current_category(path)==config["category"]: path.unlink()
    state.setdefault("sets",{})[set_id]=generated
    return len(generated),generated

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("source",type=Path,help="path to kujo-agents root (legacy set directory also accepted)"); parser.add_argument("--set",dest="sets",action="append",choices=sorted(SETS)); args=parser.parse_args()
    source=args.source.expanduser().resolve(); selected=args.sets or sorted(SETS)
    if source.name in SETS and (source/"README.md").is_file(): selected=[source.name]; source=source.parent
    if not any((source/set_id).is_dir() for set_id in SETS): print(f"kujo-agents root not found: {source}",file=sys.stderr); return 2
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=True); state=load_state(); total=0
    try:
        for set_id in selected:
            count,_=sync_set(source,set_id,state); total+=count; print(f"Generated {count} {SETS[set_id]['category']} agent entries")
    except (OSError,ValueError,json.JSONDecodeError) as exc: print(f"sync failed: {exc}",file=sys.stderr); return 1
    state["schema"]="agents-site.sync-state/v1"; state["updated_at"]=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"); STATE_PATH.write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    print(f"Generated {total} agent entries in {OUTPUT_ROOT}"); return 0

def load_state()->dict:
    if not STATE_PATH.is_file(): return {"schema":"agents-site.sync-state/v1","sets":{}}
    value=json.loads(STATE_PATH.read_text()); return value if isinstance(value,dict) else {"schema":"agents-site.sync-state/v1","sets":{}}

if __name__=="__main__": raise SystemExit(main())
