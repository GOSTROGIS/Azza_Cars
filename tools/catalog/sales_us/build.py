import functools,json,hashlib,re,csv
R='catalog/sources/sales_us/raw/'
log={}
for row in csv.reader(open('catalog/sources/sales_us/fetch_log.tsv'),delimiter='\t'):
    log[row[0]]=row  # last wins
def norm(s): return re.sub(r'\s+',' ',s).strip()
def sha(f): return hashlib.sha256(open(R+f,'rb').read()).hexdigest()
@functools.cache
def txt(f):
    base=f.rsplit('.',1)[0]
    return norm(open(R+base+'.txt',encoding='utf-8').read())
TPRN24='https://www.prnewswire.com/news-releases/toyota-motor-north-america-reports-2024-us-sales-results-302341917.html'
E=[]
def add(make,model,year,units,scope,f,quote,note=None):
    name=f
    L=log[name]
    assert L[1]=='200',name
    q=norm(quote)
    assert q in txt(f), (model,year,q)
    assert f"{units:,}" in q, (model,year)
    d=dict(make=make,model=model,year=year,units=units,scope=scope,source_url=L[5],retrieved_utc=L[3],sha256=sha(f),local_file=R+f,quote=q)
    assert d['sha256']==L[4] or name.startswith('honda_2024.html'), name
    if note: d['note']=note
    E.append(d)
def miss(make,model,year,note,urls=None):
    d=dict(make=make,model=model,year=year,units=None,scope=None,source_url=urls,retrieved_utc=None,sha256=None,local_file=None,quote=None,note=note)
    E.append(d)
TOY_SCOPE="U.S. sales, calendar year to date (table 'TOYOTA U.S. SALES SUMMARY', column '-- CALENDAR YEAR TO DATE --', volume)"
PRN_NOTE="Toyota-issued release distributed via PR Newswire (SOURCE Toyota Motor North America). The pressroom.toyota.com page carries the same release text but its model table is a linked PDF on S3 that returned HTTP 403 (Access Denied)."
hdr24="TOYOTA U.S. SALES SUMMARY | December 2024 | | -- CURRENT MONTH -- | -- CALENDAR YEAR TO DATE -- | | 2024 | 2023 | DSR % | VOL % | 2024 | 2023 | DSR % | VOL %"
hdr25="TOYOTA U.S. SALES SUMMARY | December 2025 | | -- CURRENT MONTH -- | -- CALENDAR YEAR TO DATE -- | | 2025 | 2024 | DSR % | VOL % | 2025 | 2024 | DSR % | VOL %"
for f,y,hdr,rows in [('toyota_2024_prn.html',2024,hdr24,{'RAV4':(475193,'RAV4 | 44,296 | 47,044 | -2.1 | -5.8 | 475,193 | 434,943 | 8.5 | 9.3'),'Camry':(309876,'CAMRY | 26,811 | 25,405 | 9.8 | 5.5 | 309,876 | 290,649 | 5.9 | 6.6'),'Tacoma':(192813,'TACOMA | 22,715 | 19,475 | 21.3 | 16.6 | 192,813 | 234,768 | -18.4 | -17.9'),'Corolla':(232908,'COROLLA | 17,720 | 23,400 | -21.2 | -24.3 | 232,908 | 232,370 | -0.4 | 0.2')}),
                     ('toyota_2025_prn.html',2025,hdr25,{'RAV4':(479288,'RAV4 | 42,028 | 44,296 | -8.8 | -5.1 | 479,288 | 475,193 | 1.2 | 0.9'),'Camry':(316185,'CAMRY | 28,512 | 26,811 | 2.3 | 6.3 | 316,185 | 309,876 | 2.4 | 2.0'),'Tacoma':(274638,'TACOMA | 25,075 | 22,715 | 6.1 | 10.4 | 274,638 | 192,813 | 42.9 | 42.4'),'Corolla':(248088,'COROLLA | 23,517 | 17,720 | 27.6 | 32.7 | 248,088 | 232,908 | 6.9 | 6.5')})]:
    t=txt(f); assert norm(hdr) in t
    for m,(u,q) in rows.items():
        add('Toyota',m,y,u,TOY_SCOPE,f,q,note=PRN_NOTE+f" Table header: '{hdr}'. Row 'COROLLA' is listed separately from 'COROLLA CROSS'." if m=='Corolla' else PRN_NOTE+f" Table header: '{hdr}'.")
# Honda
add('Honda','CR-V',2024,402791,"Honda brand U.S. sales, 2024 calendar year (American Honda year-end release)",'honda_2024.html',
    "CR-V remains top-selling Honda, up 11% to 402,791 units (a new record) and first Honda model to cross 400k units since 2001 (Accord).",
    note="The 2026 Honda Digital FactBook table 'Honda Vehicles Sales in the U.S.' also lists CR-V Total 2024 = 402,791 (raw/honda_factbook_2026.html).")
FB="Honda Digital FactBook (hondanews.com), table 'Honda Vehicles Sales in the U.S.', yearly row; first cell of each model's column pair is total U.S. sales, the parenthesized cell is the N.A.-produced subset"
fb_rows={('CR-V',2025):(403768,'CR-V Total*** 2025 403,768 (403,768)'),('Civic',2025):(238661,'Civic 2025 238,661 (221,566)'),('Civic',2024):(242005,'Civic 2024 242,005 (235,988)')}
FBH="Honda Vehicles Sales in the U.S. Scroll right to view full table | Accord | Accord hybrid* | Civic | Civic hybrid* | Civic Natural Gas** | Prelude | Odyssey | CR-V Total***"
FBN=("Header cells Accord, Accord hybrid*, Civic, Civic hybrid*, Odyssey and CR-V Total*** each span 2 columns (colspan=2: total, then parenthesized N.A.-produced subset); Civic Natural Gas** and Prelude span 1. "
     "So in the row, after '2025': Accord=150,196 (150,196), Accord hybrid=76,187 (76,187), Civic=238,661 (221,566), Civic hybrid=86,407 (75,672), Civic Natural Gas=blank, Prelude=204, Odyssey=88,462 (88,462), CR-V Total=403,768 (403,768). "
     "Header quoted: '"+FBH+"'. Civic hybrid is listed as its own column; the table does not state whether the Civic column includes hybrids (the 2025 release says Civic was 'over 36% hybrid').")
fbsc="U.S. sales, calendar year (Honda Digital FactBook table 'Honda Vehicles Sales in the U.S.', yearly row, total column of the model's column pair)"
add('Honda','CR-V',2025,403768,fbsc,'honda_factbook_2026.html',"2025 | 150,196 | (150,196) | 76,187 | (76,187) | 238,661 | (221,566) | 86,407 | (75,672) | | 204 | 88,462 | (88,462) | 403,768 | (403,768)",note=FBN+" The 2025 year-end release itself (raw/honda_2025.html) only says 'Record sales of CR-V, with the model posting over 400,000 units for the second straight year'.")
add('Honda','Civic',2025,238661,fbsc,'honda_factbook_2026.html',"2025 | 150,196 | (150,196) | 76,187 | (76,187) | 238,661 | (221,566)",note=FBN+" The 2025 year-end release text gives no Civic unit total.")
add('Honda','Civic',2024,242005,fbsc,'honda_factbook_2026.html',"2024 | 162,723 | (162,723) | 83,237 | (83,237) | 242,005 | (235,988)",note=FBN+" The 2024 year-end release text (raw/honda_2024.html) only says 'Civic sales up 21% to remain #1 in compact segment'.")
# Ford
FS="U.S. sales, Year-to-Date (full year), table 'FORD MOTOR COMPANY Q4 {y} U.S. SALES'"
add('Ford','F-Series',2024,765649,FS.format(y=2024),'ford_2024_q4_sales.pdf',"F-Series 214,814 177,419 21.1 765,649 750,789 2.0",
    note="Columns: Q4 2024 | Q4 2023 | % Change | Year-to-Date 2024 | Year-to-Date 2023 | % Change. PDF linked/hosted on Ford investor CDN (s205.q4cdn.com). The 2025 release lists the same 2024 YTD value (765,649) as its prior-year column.")
add('Ford','F-Series',2025,828832,"U.S. sales, calendar year 2025 (Ford Q4 2025 U.S. sales release)",'ford_2025_q4_sales.pdf',"F-Series sold 828,832 trucks in 2025, an increase of 8.3%, outselling its nearest competitor by almost 250,000 trucks and expanding its lead over 2024.",
    note="Same figure in the release table: 'F-Series 208,252 214,814 -3.1 828,832 765,649 8.3' (Q4 2025 | Q4 2024 | % | YTD 2025 | YTD 2024 | %).")
# Stellantis
SS="U.S. sales, CYTD Sales Curr Yr (FCA US LLC Sales Summary Q4 {y})"
add('Ram','Ram pickup (Ram P/U)',2024,373120,SS.format(y=2024),'stellantis_2024_chart.pdf',"Ram P/U 104,454 112,486 -7% 373,120 444,926 -16%",
    note="Columns: Q4 Sales Curr Yr | Pr Yr | Vol % Change | CYTD Sales Curr Yr | Pr Yr | Vol % Change. Ram P/U excludes ProMaster vans (listed separately); RAM BRAND total 439,039. PDF attached to FCA US release 'FCA US Reports Fourth-quarter and Full-year 2024 Sales Results' (media.stellantisnorthamerica.com newsrelease id=26525).")
add('Ram','Ram pickup (TOTAL Ram PU)',2025,374059,SS.format(y=2025),'stellantis_2025_chart.pdf',"TOTAL Ram PU 111,673 104,454 7% 374,059 373,120 0%",
    note="Same column layout. 2025 table splits Ram LD PU 204,139 and Ram HD PU 169,920. PDF attached to FCA US full-year 2025 release (newsrelease id=27358).")
add('Jeep','Grand Cherokee',2024,216148,SS.format(y=2024),'stellantis_2024_chart.pdf',"Grand Cherokee 55,209 61,723 -11% 216,148 244,594 -12%",
    note="Release text adds: 'Jeep Grand Cherokee 4xe accounted for 27,590 units (13%) of total Grand Cherokee sales in 2024'.")
add('Jeep','Grand Cherokee',2025,210082,SS.format(y=2025),'stellantis_2025_chart.pdf',"Grand Cherokee 55,861 55,209 1% 210,082 216,148 -3%")
# Nissan
add('Nissan','Rogue',2024,245724,"U.S. sales, CYTD 2024 (Nissan Division table; reported on a volume basis)",'nissan_2024.html',"Rogue | 56,568 | 60,367 | -6.3 | -8.7 | 245,724 | 271,458 | -9.5 |",
    note="Header: 'Nissan Division | Qtr: Oct-24 to Dec-24 CY2024 | Qtr: Oct-23 to Dec-23 CY2023 | Quarterly% chg (units) | Quarterly% chg (DSR) | CYTD 2024 | CYTD 2023 | CY% chg'.")
add('Nissan','Rogue',2025,217896,"U.S. sales, CY 2025 (Nissan Division table)",'nissan_2025.html',"Rogue | 56,072 | 56,568 | -0.9 | -0.9 | 217,896 | 245,724 | -11.3 |",
    note="Header: 'NISSAN DIVISION | Qtr: Oct-25 to Dec-25 | Qtr: Oct-24 to Dec-24 | Quarterly % chg (units) | Quarterly % chg (DSR) | CY 2025 | CY 2024 | CY % chg'.")
# Hyundai
HN="Hyundai-issued release distributed via PR Newswire; the hyundainews.com release page is a JavaScript app whose fetched HTML contains no release text (raw/hyundai_2024.html). Table 'Model Total Sales'; header: '{h}'. The 'Tucson' row is the only Tucson row in the table; the release separately mentions Tucson HEV records, so the row appears to be all Tucson powertrains, but the table does not say so explicitly."
add('Hyundai','Tucson',2024,206126,"Total sales (retail + fleet), 2024 YTD (table 'Model Total Sales')",'hyundai_2024_prn.html',"Tucson | 20,172 | 19,424 | +4 % | 60,179 | 56,444 | +7 % | 206,126 | 209,624 | -2 % |",
    note=HN.format(h="Vehicles | Dec-24 | Dec-23 | % Chg | Q4 2024 | Q4 2023 | % Chg | 2024 YTD | 2023 YTD | % Chg")+" Release says fleet was 11% of 2024 total volume.")
add('Hyundai','Tucson',2025,234230,"Total sales (retail + fleet), 2025 YTD (table 'Model Total Sales')",'hyundai_2025_prn.html',"Tucson | 22,193 | 20,172 | +10 % | 68,991 | 60,179 | +15 % | 234,230 | 206,126 | +14 % |",
    note=HN.format(h="Vehicles | Dec-25 | Dec-24 | % Chg | Q4 2025 | Q4 2024 | % Chg | 2025 YTD | 2024 YTD | % Chg"))
# Missing
GMU=["https://investor.gm.com/static-files/e1bb38a4-aaf9-4141-b44a-4c61c1f2ec54","https://investor.gm.com/static-files/23adce96-ea26-4a6e-82dd-68a0042df51c","https://pressroom.gm.com/gmbx/us/en/pressroom/home/news.detail.html/Pages/news/us/en/2025/jan/0103-gmsales.html","https://investor.gm.com/news-releases/news-release-details/gm-leads-us-industry-2025-sales-6"]
gmn="GM's official Q4 U.S. deliveries tables (investor.gm.com static PDFs) and the GM pressroom/investor release pages all returned HTTP 403 'Access Denied' (Akamai) to curl with the required User-Agent on 2026-11-22; error pages saved as raw/gm_*_403.html / raw/gm_2024_pressroom.html / raw/gm_2025_release.html. No figure recorded. Note GM reports 'deliveries', not 'sales'."
for m in ['Silverado','Sierra','Equinox']:
    for y in [2024,2025]:
        miss('Chevrolet' if m!='Sierra' else 'GMC',m,y,gmn,GMU)
tn=("Tesla does not publish U.S. per-model sales; its quarterly 'Production, Deliveries & Deployments' releases give worldwide figures with Model 3 and Model Y combined as 'Model 3/Y'. "
    "The Q4 2024 IR page returned HTTP 403 'Access Denied' (raw/tesla_q4_2024.html), so not even the global combined figure was read from an official document here. No figure recorded.")
for m in ['Model Y','Model 3']:
    for y in [2024,2025]:
        miss('Tesla',m,y,tn,["https://ir.tesla.com/press-release/tesla-fourth-quarter-2024-production-deliveries-and-deployments"])
json.dump(E,open('catalog/sources/sales_us/us_sales.json','w'),indent=2,ensure_ascii=False)
print(len(E),'entries;',sum(1 for e in E if e['units']),'with units')
