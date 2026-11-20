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
from urllib.parse import urlsplit

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

PLATFORM_NAMES = {"slack": "Slack", "matrix": "Matrix", "teams": "Microsoft Teams",
                  "paperclip": "Paperclip", "board": "Vercel Board", "mcp": "MCP", "local": "Local"}
QUALIFICATION = {"fixture-only": "fixture tested", "experimental": "experimental",
                 "qualified": "qualified"}


def compatibility(source_root: Path, source: str) -> dict[str, list[dict]]:
    index = source_root / "collaboration-integrations.json"
    if not index.is_file():
        return {}
    payload = json.loads(index.read_text(encoding="utf-8"))
    if (payload.get("schema") != "kujo.collaboration.compatibility/v1"
            or not isinstance(payload.get("entries"), list)):
        raise ValueError("unsupported collaboration index")
    registry = json.loads((source_root / "agent-registry.json").read_text(encoding="utf-8"))
    paths = {row["id"]: row["path"] for row in registry["agents"]}
    selected: dict[str, list[dict]] = {}
    seen = set()
    for row in payload["entries"]:
        platform, state, host = row.get("platform"), row.get("status"), row.get("host")
        agents = row.get("agent_ids")
        operations = row.get("operations")
        if (platform not in PLATFORM_NAMES or state not in QUALIFICATION or row.get("protocol_major") != 1
                or not isinstance(host, str) or not re.fullmatch(r"[a-z0-9-]{1,60}", host)
                or not isinstance(agents, list) or not agents
                or not isinstance(operations, list) or not operations
                or any(not isinstance(op, str) or not re.fullmatch(r"[a-z.-]{1,48}", op) for op in operations)):
            raise ValueError("invalid collaboration entry")
        if state == "qualified":
            for key in ("setup_url", "qualification_url"):
                value = row.get(key, "")
                url = urlsplit(value)
                if (url.scheme != "https" or url.netloc not in {"agents.kujolang.ai", "github.com"}
                        or url.query or url.fragment or not re.fullmatch(r"/[A-Za-z0-9_./-]+", url.path)):
                    raise ValueError("untrusted collaboration qualification link")
        if "preview_url" in row:
            preview = row["preview_url"]
            if (state != "experimental" or platform != "slack" or not isinstance(preview, str)
                    or not re.fullmatch(r"https://agents[.]kujolang[.]ai/connect-slack-[a-z0-9-]+/", preview)):
                raise ValueError("untrusted Slack preview link")
        for agent in agents:
            key = (agent, platform, host)
            if agent not in paths or key in seen:
                raise ValueError("unknown or duplicate collaboration profile")
            seen.add(key)
            directory, _, slug = paths[agent].partition("/")
            if directory == source:
                selected.setdefault(slug, []).append(row)
    return selected


def compatibility_text(entries: list[dict], heading: str = "## Collaboration platforms") -> str:
    if not entries:
        return ""
    rows = [heading, ""]
    for row in sorted(entries, key=lambda item: (item["platform"], item["host"])):
        name = PLATFORM_NAMES[row["platform"]]
        status = QUALIFICATION[row["status"]]
        label = f"{name} ({row['host']} host, {status})"
        if row["status"] == "qualified":
            label = f"[Connect to {name}]({row['setup_url']}) ({row['host']} host), [qualification]({row['qualification_url']})"
        elif "preview_url" in row:
            label = f"[Connect to {name}]({urlsplit(row['preview_url']).path}) (self-hosted preview)"
        rows.append(f"- {label}. Operations: {', '.join(row['operations'])}.")
    return "\n\n" + "\n".join(rows) + "\n"


def sync_set(source_root:Path,set_id:str,state:dict)->tuple[int,list[str]]:
    config=SETS[set_id]; source_dir=source_root/config["source"]
    if not source_dir.is_dir(): raise ValueError(f"source directory not found: {source_dir}")
    contracts={x.parent.name:x for x in source_dir.glob("*/AGENT.md")}
    if not contracts: raise ValueError(f"no agent contracts found in: {source_dir}")
    compatibility_by_slug=compatibility(source_root,config["source"])
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
        destination=OUTPUT_ROOT/f"{public_slug}.md"; destination.write_text("\n".join(frontmatter)+remainder.lstrip()+"\n"+compatibility_text(compatibility_by_slug.get(slug,[])),encoding="utf-8"); generated.append(public_slug)
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
