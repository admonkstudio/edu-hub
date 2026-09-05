#!/usr/bin/env python3
from __future__ import annotations
import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA='EduHubResearchBot/0.1 (+https://github.com/admonkstudio/edu-hub; source-acquisition)'
CATEGORIES=[
 ('government_university','Government university','university','government','https://scu.eg/الجامعات-الحكومية/',28),
 ('national_nonprofit_university','National / non-profit university','university','national_nonprofit','https://scu.eg/الجامعات-المصرية-الأهلية/',33),
 ('government_technological_university','Government technological university','university','government','https://scu.eg/government-technological-universities/',12),
 ('private_university','Private university','university','private','https://scu.eg/accredited-private-universities/',39),
 ('foreign_university_branch','Foreign university branch','university','foreign_branch','https://scu.eg/branches-of-international-universities/',9),
 ('special_nature_university','University of special nature','university','special','https://scu.eg/specialty-universities/',2),
 ('international_framework_institution','International/framework institution','higher_institution','international_framework','https://scu.eg/educational-institutions-with-international-and-framework-agreements/',9),
 ('government_supervised_institution','Government-supervised educational institution','higher_institution','government_supervised','https://scu.eg/government-sponsored-educational-institutions/',4),
 ('accredited_private_institute','Accredited private institute','higher_institute','private','https://scu.eg/private-institutes/',181),
 ('accredited_military_college','Accredited military college/academy','academy','military','https://scu.eg/accredited-military-colleges/',8),
 ('private_technological_university','Private technological university','university','private','https://scu.eg/private-technological-universities/',2),
]

def sess():
 s=requests.Session(); r=Retry(total=4,backoff_factor=1,status_forcelist=(429,500,502,503,504),allowed_methods=('GET',)); s.mount('https://',HTTPAdapter(max_retries=r)); s.headers['User-Agent']=UA; return s
S=sess()

def clean(t): return re.sub(r'\s+',' ',t or '').strip()

def page_records(url):
 r=S.get(url,timeout=60); r.raise_for_status(); soup=BeautifulSoup(r.text,'html.parser')
 root=soup.find('main') or soup
 candidates=[]
 # SCU institution pages render entries primarily as linked h4/h3 cards.
 for tag in root.select('h4 a, h3 a, h5 a'):
  name=clean(tag.get_text(' ',strip=True)); href=urljoin(url,tag.get('href') or '')
  if name: candidates.append((name,href))
 # Some category pages use heading text without a link.
 if not candidates:
  for tag in root.select('h4, h3'):
   name=clean(tag.get_text(' ',strip=True))
   if name: candidates.append((name,''))
 stop=('التسجيل للحصول','اشترك','روابط هامة','الأنظمة','sign up','important links','systems','numbers and statistics')
 out=[]; seen=set()
 for name,href in candidates:
  low=name.lower()
  if any(x in low for x in stop): continue
  if name in seen: continue
  seen.add(name); out.append((name,href))
 return out

def main(outpath='tools/data-acquisition/seeds/scu_higher_ed_snapshot.csv'):
 rows=[]; report=[]; n=0
 for key,label,etype,owner,url,expected in CATEGORIES:
  items=page_records(url)
  report.append({'category':key,'expected':expected,'found':len(items),'url':url})
  for name,site in items:
   n+=1; rows.append({
    'seed_id':f'SCU-LIVE-{n:04d}','name_ar':name,'locale':'ar-EG','entity_type_proposed':etype,
    'higher_ed_category':key,'category_label':label,'ownership_type_proposed':owner,
    'official_website_from_scu':site or None,'source_registry':'Supreme Council of Universities (SCU)',
    'source_url':url,'source_authority':1,'retrieved_on':datetime.now(timezone.utc).date().isoformat(),
    'identity_status':'source-backed','classification_status':'source-backed','english_localization_status':'pending',
    'publication_status':'draft','data_status':'candidate','import_decision':'Raw acquisition only','notes':''})
 p=Path(outpath); p.parent.mkdir(parents=True,exist_ok=True)
 fields=list(rows[0].keys()) if rows else ['seed_id','name_ar']
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
 Path(str(p)+'.report.json').write_text(json.dumps({'total':len(rows),'categories':report},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'total':len(rows),'categories':report},ensure_ascii=False,indent=2))
 if not rows: sys.exit('SCU scrape returned zero rows')
if __name__=='__main__': main()
