import argparse, concurrent.futures, hashlib, json, sys, urllib.request, urllib.error, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
p=argparse.ArgumentParser();p.add_argument('origin');p.add_argument('audit');p.add_argument('phase');a=p.parse_args(); out=Path(a.audit)/'raw'/'live';out.mkdir(parents=True,exist_ok=True)
def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'KujoReleaseAudit/1.0'}),timeout=20) as r:
            body=r.read();return dict(url=url,status=r.status,final_url=r.url,headers=dict(r.headers),body=body.decode('utf-8',errors='replace'),sha256=hashlib.sha256(body).hexdigest())
    except urllib.error.HTTPError as e:return dict(url=url,status=e.code,error=str(e))
    except Exception as e:return dict(url=url,status=None,error=str(e))
sitemap=fetch(a.origin+'/sitemap.xml');urls=[e.text for e in ET.fromstring(sitemap['body']).iter() if e.tag.endswith('}loc')];seen=set();receipts={}
while urls:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(fetch,sorted(set(urls)-seen)))
    urls=[]
    for r in results:
        receipts[r['url']]=r;seen.add(r['url'])
        if r['status']!=200:continue
        s=BeautifulSoup(r.get('body',''),'html.parser')
        for link in s.find_all('a',href=True):
            dest=urllib.parse.urljoin(r['url'],link['href']).split('#')[0]
            u=urllib.parse.urlparse(dest)
            if dest.startswith(a.origin+'/') and not u.query and (u.path.endswith('/') or not Path(u.path).suffix) and dest not in seen:urls.append(dest)
(out/(a.phase+'-full-crawl.json')).write_text(json.dumps(dict(retrieved_at=datetime.now(timezone.utc).isoformat(),sitemap=sitemap,pages=receipts),indent=2))
print(json.dumps({'pages':len(receipts),'non200':{u:r['status'] for u,r in receipts.items() if r['status']!=200}}))
