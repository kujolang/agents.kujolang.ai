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
    expected_counts={"chain-of-command":28,"webops":28,"publishing-house":23,"videoops":5}
    expected_categories={"chain-of-command":"Chain of Command","webops":"WebOps","publishing-house":"Publishing House","videoops":"VideoOps"}
    for set_id,expected_count in expected_counts.items():
        slugs=sets.get(set_id,[])
        if len(slugs)!=expected_count or len(slugs)!=len(set(slugs)): errors.append(f"{set_id}: expected {expected_count} unique managed slugs")
        for slug in slugs:
            path=CONTENT/f"{slug}.md"
            if not path.is_file(): errors.append(f"{set_id}: missing {slug}.md"); continue
            meta,text=fields(path)
            for field in REQUIRED:
                if not meta.get(field): errors.append(f"{slug}: missing {field}")
            source_slug=slug.removeprefix("videoops-") if set_id=="videoops" else slug
            expected=f"/kujo-agents/blob/main/{set_id}/{source_slug}/AGENT.md"
            if expected not in meta.get("source_url",""): errors.append(f"{slug}: wrong canonical source URL")
            if not re.search(r"^last_updated: \d{4}-\d{2}-\d{2}$",text,re.M): errors.append(f"{slug}: invalid last_updated")
            expected_category=f'[{json.dumps(expected_categories[set_id])}]'
            if meta.get("categories")!=expected_category: errors.append(f"{slug}: wrong {expected_categories[set_id]} category")
            if set_id in ("webops","publishing-house","videoops") and re.search(r"(?i)coming soon|lorem ipsum|placeholder",text): errors.append(f"{slug}: placeholder content")
            expected_portrait=f'"content/media/agents/{slug}.webp"'
            portrait=ROOT/expected_portrait.strip('"')
            if portrait.is_file():
                if meta.get("featured_image")!=expected_portrait: errors.append(f"{slug}: wrong agent portrait")
            elif meta.get("featured_image")!='"assets/images/kujo-logomark.svg"':
                errors.append(f"{slug}: missing portrait must use generic Kujo fallback")
            route=OUTPUT/"agents"/slug/"index.html"
            if OUTPUT.is_dir() and not route.is_file(): errors.append(f"{slug}: generated route missing")
            elif OUTPUT.is_dir():
                route_text=route.read_text()
                blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',route_text,re.S)
                schemas=[]
                for block in blocks:
                    try: schemas.append(json.loads(block))
                    except json.JSONDecodeError: pass
                source_schema=next((value for value in schemas if value.get("@type")=="SoftwareSourceCode"),None)
                expected_name=json.loads(meta["title"])
                if not source_schema: errors.append(f"{slug}: SoftwareSourceCode schema missing")
                else:
                    if source_schema.get("name")!=expected_name: errors.append(f"{slug}: schema name does not match visible title")
                    if source_schema.get("mainEntityOfPage",{}).get("@id")!=f"https://agents.kujolang.ai/agents/{slug}/": errors.append(f"{slug}: schema mainEntityOfPage mismatch")
                    parent=source_schema.get("isPartOf",{})
                    if parent.get("url")!=f"https://agents.kujolang.ai/agents/{set_id}/": errors.append(f"{slug}: schema agent-set relationship mismatch")
                portrait_tag=re.search(r'<img[^>]+class="featured-image"[^>]*>',route_text)
                if portrait_tag and ('loading="eager"' not in portrait_tag.group(0) or 'fetchpriority="high"' not in portrait_tag.group(0)):
                    errors.append(f"{slug}: profile portrait is not prioritized")
    if OUTPUT.is_dir():
        for route in (OUTPUT/"index.html",OUTPUT/"agents/index.html",OUTPUT/"agents/chain-of-command/index.html",OUTPUT/"agents/webops/index.html",OUTPUT/"agents/publishing-house/index.html",OUTPUT/"agents/videoops/index.html",OUTPUT/"sitemap.xml",OUTPUT/"llms.txt"):
            if not route.is_file(): errors.append(f"generated output missing: {route.relative_to(ROOT)}")
        for set_id,expected_count in expected_counts.items():
            route=OUTPUT/"agents"/set_id/"index.html"
            if not route.is_file(): continue
            text=route.read_text()
            blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)
            schemas=[]
            for block in blocks:
                try: schemas.append(json.loads(block))
                except json.JSONDecodeError: pass
            collection=next((value for value in schemas if value.get("@type")=="CollectionPage"),None)
            if not collection or len(collection.get("hasPart",[]))!=expected_count: errors.append(f"{set_id}: incomplete CollectionPage membership schema")
            if f'https://github.com/kujolang/kujo-agents/tree/main/{set_id}' not in text: errors.append(f"{set_id}: visible source provenance missing")
    if errors:
        print(json.dumps({"valid":False,"errors":errors},indent=2)); return 1
    print(json.dumps({"valid":True,"chain_of_command":28,"webops":28,"publishing_house":23,"videoops":5,"individual_routes":84},indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
