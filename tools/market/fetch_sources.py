"""Fetch and archive every source the Metro Vancouver market analysis uses.

Writes small, Metro Vancouver only extracts to market/sources/ and records the URL,
retrieval time and SHA-256 of each raw input in market/sources/provenance.json.

Inputs read from a local checkout of the consulting repository (read only):
  Metro Vancouver member boundaries, the 2021 census profile by census subdivision,
  the Canadian Business Counts table and the AllThePlaces chain extract.
Inputs fetched over HTTPS:
  Overture Maps places (GeoParquet, read with DuckDB over HTTP range requests),
  the TransLink GTFS feed, and a short list of web pages for demand drivers.

Usage: python tools/market/fetch_sources.py [--consulting /home/user/consulting]
Needs: duckdb, shapely, pypdf.
"""
import argparse, csv, datetime, gzip, hashlib, html, io, json, os, re, shutil, sys, urllib.request, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools' / 'catalog'))
from common import sha256 as sha  # noqa: E402
OUT = REPO / 'market' / 'sources'
UA = 'Azza_Cars-market-research/1.0 (+https://github.com/GOSTROGIS/Azza_Cars)'
# Search window around Metro Vancouver. Points are clipped to the member boundaries later.
BBOX = (-123.45, 48.98, -122.20, 49.60)
OVERTURE_STAC = 'https://stac.overturemaps.org/catalog.json'
GTFS_URL = 'https://gtfs-static.translink.ca/gtfs/google_transit.zip'
ATP_RUN = 'https://alltheplaces-data.openaddresses.io/runs/2026-11-14-13-32-33'
MV_CD = '5915'  # census division code of Metro Vancouver (Greater Vancouver)

# Overture taxonomy values kept. Everything else is dropped before archiving.
OVERTURE_SUPPLY = {'car_rental_service', 'truck_rental_service', 'trailer_rental_service', 'rv_rental_service', 'car_sharing',
                   'auto_dealer', 'used_auto_dealer', 'truck_dealer', 'commercial_vehicle_dealer', 'auto_leasing', 'rental_service'}
# Anchors for demand drivers, matched by exact Overture name and category.
OVERTURE_ANCHORS = [('Vancouver International Airport', 'airport'), ('Port of Vancouver Cruise Ship Terminal', 'travel_and_transportation')]

# Web pages for demand drivers. Each phrase must appear in the page text, or the fetch fails.
WEB = [
    ('yvr-traffic-2025-11', 'https://www.yvr.ca/-/media/yvr/documents/facts-sheets/2025/11---november/traffic-update-nov25.pdf', 'pdf',
     ['Total (All Sectors)', 'November 2025']),
    ('dailyhive-yvr-2025', 'https://dailyhive.com/vancouver/vancouver-international-airport-yvr-all-time-passenger-record-2025-statistics', 'html',
     ['26.914 million passengers', '73,736 passengers']),
    ('dailyhive-cruise-2025', 'https://dailyhive.com/vancouver/vancouver-cruise-ship-season-2025-statistics', 'html',
     ['1.2 million passengers on 301 cruise ship visits']),
    ('destination-vancouver-fast-facts', 'https://www.destinationvancouver.com/vancouver/fast-facts/', 'html',
     ['11.3M Overnight visitors 2025']),
    ('dailyhive-modo-1000', 'https://dailyhive.com/vancouver/modo-carshare-fleet-size', 'html',
     ['fleet size of 1,000 vehicles', 'roughly 2,300 vehicles']),
    ('modo-impact', 'https://www.modo.coop/our-impact', 'html', ['1 in 5 vehicles are electric']),
    ('turo-help-canada-hosts', 'https://help.turo.com/en_us/sharing-your-car-canada-hosts-S1uY7_OIc.md', 'text',
     ['British Columbia', 'Permits policyholders to list their vehicles on Turo']),
    ('destination-bc-vcm-profile-2026', 'https://www.destinationbc.ca/content/uploads/2026/08/DBC-Regional-Profile-VCM-2026.pdf', 'pdf',
     ['49% of BC', '62.5%']),
    ('hertz-q4-2025-results', 'https://newsroom.hertz.com/press-releases/press-release-details/hertz-transformation-drives-structural-revenue-gains-and-builds-sustainable-momentum/', 'html',
     ['averaged 81% for the full year', 'Depreciation per Unit per Month (DPU) was $330 in Q4 and $300 for the full year']),
    ('avis-budget-q4-2025-results', 'https://www.avisbudgetgroup.com/home/news-and-media/press-release/avis-budget-group-reports-fourth-quarter-and-full-year-results', 'html',
     ['revenue per day, excluding exchange rate effects, down 2%']),
    # Tried and kept in the log even when refused, so the report can say what could not be read.
    ('vancouver-transportation-snapshot-2025', 'https://vancouver.ca/files/cov/2025-transportation-snapshot.pdf', 'pdf', ['Evo']),
]


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def get(url, limit=200_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(limit + 1)


def write(rel, data):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {'path': f'market/sources/{rel}', 'sha256': sha(data), 'bytes': len(data)}


def text_of(kind, raw):
    if kind == 'pdf':
        from pypdf import PdfReader
        return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages)
    t = raw.decode('utf-8', errors='replace')
    if kind == 'html':
        t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', t, flags=re.S)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return re.sub(r'[ \t\r\f\v]+', ' ', t)


def fetch_web(log):
    for key, url, kind, phrases in WEB:
        entry = {'id': key, 'url': url, 'retrievedAt': now(), 'userAgent': UA}
        try:
            raw = get(url, 20_000_000)
        except Exception as e:  # noqa: BLE001 - a refused page is recorded, not fatal
            entry.update({'status': 'not retrieved', 'error': str(e)})
            log['web'].append(entry); print('web', key, 'FAILED', e); continue
        text = text_of(kind, raw)
        flat = re.sub(r'\s+', ' ', text)
        missing = [p for p in phrases if p not in flat]
        if missing: raise ValueError(f'{key}: expected phrases not found {missing}')
        if kind == 'pdf' and len(text) < 20_000:
            extract = text  # a short sheet of figures, kept whole as text
        else:
            spans = []
            for p in phrases:
                for m in re.finditer(re.escape(p), flat):
                    spans.append(flat[max(0, m.start() - 400): m.end() + 400])
            extract = '\n\n...\n\n'.join(spans)
        rec = write(f'web/{key}.txt', (f'Source: {url}\nRetrieved: {entry["retrievedAt"]}\nRaw SHA-256: {sha(raw)}\n'
                                         f'Extract: text near the quoted phrases {phrases}\n\n' + extract + '\n').encode('utf-8'))
        entry.update({'status': 'retrieved', 'rawSha256': sha(raw), 'rawBytes': len(raw), 'phrases': phrases, 'extract': rec})
        log['web'].append(entry); print('web', key, 'ok')


def fetch_overture(log):
    import duckdb
    cat = json.loads(get(OVERTURE_STAC))
    release = cat['latest']
    index_url = f'https://stac.overturemaps.org/{release}/collections.parquet'
    index = get(index_url)
    tmp = OUT / '_overture_index.parquet'; tmp.write_bytes(index)
    con = duckdb.connect()
    con.sql('INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;')
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if proxy: con.sql(f"SET http_proxy='{proxy.split('://')[-1]}'")
    ca = os.environ.get('SSL_CERT_FILE')
    if ca: con.sql(f"SET ca_cert_file='{ca}'")
    x0, y0, x1, y1 = BBOX
    files = con.sql(f"""select id, assets.aws.href, assets.aws['file:size'] from '{tmp}' where collection='place'
        and bbox.xmin < {x1} and bbox.xmax > {x0} and bbox.ymin < {y1} and bbox.ymax > {y0}""").fetchall()
    tmp.unlink()
    retrieved = now(); feats = []
    cats = ','.join(f"'{c}'" for c in OVERTURE_SUPPLY)
    anchors = ' or '.join(f"(names.primary = '{n}' and taxonomy.primary = '{c}')" for n, c in OVERTURE_ANCHORS)
    file_log = []
    for fid, href, size in files:
        head = urllib.request.urlopen(urllib.request.Request(href, method='HEAD', headers={'User-Agent': UA}), timeout=60)
        file_log.append({'id': fid, 'url': href, 'bytes': size, 'etag': head.headers.get('ETag'), 'lastModified': head.headers.get('Last-Modified')})
        rows = con.sql(f"""select id, ST_X(geometry) lon, ST_Y(geometry) lat, names.primary name, brand.names.primary brand, brand.wikidata brand_wd,
              taxonomy.primary category, taxonomy.alternates alternates, basic_category, confidence, operating_status,
              addresses[1].freeform address, addresses[1].locality locality, websites[1] website,
              list_transform(sources, lambda s: s.dataset || ':' || coalesce(s.record_id, '')) src
            from read_parquet('{href}')
            where bbox.xmin > {x0} and bbox.xmax < {x1} and bbox.ymin > {y0} and bbox.ymax < {y1}
              and (taxonomy.primary in ({cats}) or {anchors})""").fetchall()
        cols = ['id', 'lon', 'lat', 'name', 'brand', 'brand_wikidata', 'category', 'alternates', 'basic_category', 'confidence', 'operating_status',
                'address', 'locality', 'website', 'sources']
        for r in rows:
            p = dict(zip(cols, r)); lon, lat = p.pop('lon'), p.pop('lat')
            feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(lon, 6), round(lat, 6)]}, 'properties': p})
    feats.sort(key=lambda f: f['properties']['id'])
    data = (json.dumps({'type': 'FeatureCollection', 'features': feats}, ensure_ascii=False, indent=0) + '\n').encode('utf-8')
    rec = write(f'overture/places-{release}-metro-vancouver.geojson', data)
    log['overture'] = {'release': release, 'stacCatalog': OVERTURE_STAC, 'itemIndex': index_url, 'itemIndexSha256': sha(index),
                       'retrievedAt': retrieved, 'files': file_log, 'bbox': BBOX, 'categories': sorted(OVERTURE_SUPPLY),
                       'anchors': OVERTURE_ANCHORS, 'licence': 'CDLA-Permissive-2.0 (https://cdla.dev/permissive-2-0/), per-source licences in the sources field',
                       'note': 'The source GeoParquet file is read by HTTP range requests and never downloaded whole, so it is identified by its S3 ETag and size. The SHA-256 is of the archived extract.',
                       'extract': rec, 'features': len(feats)}
    print('overture', release, len(feats))


STATCAN = {'21100012': 'Automotive equipment rental and leasing, summary statistics',
           '21100014': 'Automotive equipment rental and leasing, sales by type of client'}


def fetch_statcan(log):
    """Annual Survey of Service Industries tables for NAICS 5321, Canada and British Columbia rows only."""
    log['statcan'] = []
    for pid, title in STATCAN.items():
        wds = f'https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{pid}/en'
        url = json.loads(get(wds))['object']; raw = get(url); retrieved = now()
        z = zipfile.ZipFile(io.BytesIO(raw))
        rows = [r for r in csv.DictReader(io.TextIOWrapper(z.open(f'{pid}.csv'), 'utf-8-sig')) if r['GEO'] in ('Canada', 'British Columbia')]
        buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        notes = z.open(f'{pid}_MetaData.csv').read()
        log['statcan'].append({'table': pid, 'title': title, 'page': f'https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid={pid}01', 'wds': wds, 'download': url,
                               'retrievedAt': retrieved, 'rawSha256': sha(raw), 'rawBytes': len(raw), 'licence': 'https://www.statcan.gc.ca/en/terms-conditions/open-licence',
                               'extract': write(f'statcan/{pid}-canada-bc.csv', buf.getvalue().encode('utf-8')),
                               'metadata': write(f'statcan/{pid}-metadata.csv', notes)})
        print('statcan', pid, len(rows))


def fetch_gtfs(log):
    raw = get(GTFS_URL); retrieved = now()
    z = zipfile.ZipFile(io.BytesIO(raw))
    read = lambda n: list(csv.DictReader(io.TextIOWrapper(z.open(n), 'utf-8-sig')))
    routes = {r['route_id']: r for r in read('routes.txt') if r['route_type'] in ('1', '2', '4')}
    trips = {t['trip_id']: t['route_id'] for t in read('trips.txt') if t['route_id'] in routes}
    stops = {s['stop_id']: s for s in read('stops.txt')}
    served = {}
    with z.open('stop_times.txt') as h:
        for st in csv.DictReader(io.TextIOWrapper(h, 'utf-8-sig')):
            rid = trips.get(st['trip_id'])
            if rid: served.setdefault(st['stop_id'], set()).add(rid)
    stations = {}
    for sid, rids in served.items():
        s = stops[sid]; parent = s.get('parent_station') or sid; p = stops.get(parent, s)
        rec = stations.setdefault(parent, {'station_id': parent, 'name': p['stop_name'], 'lat': p['stop_lat'], 'lon': p['stop_lon'], 'lines': set()})
        rec['lines'] |= {routes[r]['route_long_name'] or routes[r]['route_short_name'] for r in rids}
    buf = io.StringIO(); w = csv.writer(buf); w.writerow(['station_id', 'name', 'lat', 'lon', 'lines'])
    for s in sorted(stations.values(), key=lambda s: s['name']):
        w.writerow([s['station_id'], s['name'], s['lat'], s['lon'], '|'.join(sorted(s['lines']))])
    rec = write('translink/rapid-transit-stations.csv', buf.getvalue().encode('utf-8'))
    feed = z.open('feed_info.txt').read().decode('utf-8-sig').strip()
    log['translink'] = {'url': GTFS_URL, 'retrievedAt': retrieved, 'rawSha256': sha(raw), 'rawBytes': len(raw), 'feedInfo': feed,
                        'licence': 'TransLink Open Data terms (https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources/gtfs/gtfs-data)',
                        'filter': 'stops served by route_type 1 (SkyTrain), 2 (West Coast Express) or 4 (SeaBus), rolled up to parent stations', 'extract': rec, 'stations': len(stations)}
    print('gtfs', len(stations))


def local_sources(log, consulting):
    c = Path(consulting)
    # Boundaries: copied whole (1.6 MB) because they are the clipping geometry.
    b = c / 'data/ca/bc/metro-vancouver/boundaries'
    raw = (b / 'members.geojson').read_bytes(); prov = json.loads((b / 'provenance.json').read_bytes())
    log['boundaries'] = {'from': str(b / 'members.geojson'), 'sha256': sha(raw), 'extract': write('boundaries/members.geojson', raw),
                         'region': write('boundaries/region.geojson', (b / 'region.geojson').read_bytes()),
                         'upstreamLicence': prov['licence'], 'upstreamSources': len(prov['sources']),
                         'upstreamFirstCapture': min(s['capturedAt'] for s in prov['sources']), 'upstreamLastCapture': max(s['capturedAt'] for s in prov['sources']),
                         'upstreamExample': prov['sources'][1]['url'], 'provenance': write('boundaries/provenance.json', (b / 'provenance.json').read_bytes())}
    # Census profile: Metro Vancouver census subdivisions only, without geometry.
    path = c / 'data/ca/census/csd-profile-2021-bc-ab.geojson'; raw = path.read_bytes(); meta = json.loads((c / 'data/ca/census/csd-profile-2021-bc-ab.metadata.json').read_bytes())
    if sha(raw) != meta['sha256']: raise ValueError('census layer does not match its metadata hash')
    keep = ['CSDUID', 'CSDNAME', 'CSDTYPE', 'population_2021', 'population_2016', 'private_dwellings', 'occupied_private_dwellings', 'land_area_km2',
            'median_household_income_2020', 'renter_households', 'households_by_tenure_total', 'commute_public_transit', 'commute_mode_total']
    buf = io.StringIO(); w = csv.writer(buf); w.writerow(keep)
    bc_tot = {'csds': 0, 'population_2021': 0, 'occupied_private_dwellings': 0}
    for f in json.loads(raw)['features']:
        p = f['properties']
        if str(p['CSDUID']).startswith(MV_CD): w.writerow([p.get(k) for k in keep])
        if str(p['CSDUID']).startswith('59'):
            bc_tot['csds'] += 1
            for k in ('population_2021', 'occupied_private_dwellings'): bc_tot[k] += p.get(k) or 0
    # British Columbia totals as sums over every BC census subdivision in the same layer, for share-of-province allocations.
    tot = io.StringIO(); tw = csv.writer(tot); tw.writerow(['measure', 'value', 'method'])
    for k, v in bc_tot.items(): tw.writerow([k, v, 'sum over BC census subdivisions (CSDUID 59xxxxx) in csd-profile-2021-bc-ab.geojson'])
    log['census'] = {'from': str(path), 'sha256': sha(raw), 'metadataSha256': sha((c / 'data/ca/census/csd-profile-2021-bc-ab.metadata.json').read_bytes()),
                     'upstreamRetrievedAt': meta['retrievedAt'], 'upstream': meta['sources']['profile'], 'licence': meta['sources']['licence'],
                     'labels': {v['field']: v['statcanLabel'] for v in meta['characteristics'].values() if v['field'] in keep},
                     'extract': write('census/csd-profile-2021-metro-vancouver.csv', buf.getvalue().encode('utf-8')),
                     'bcTotals': write('census/bc-totals-2021.csv', tot.getvalue().encode('utf-8'))}
    # Business counts: Metro Vancouver census subdivisions, all employment size classes, NAICS codes relevant to vehicles and their demand.
    path = c / 'data/ca/census/business-counts-bc-ab/business-counts-2026-06.csv.gz'; raw = path.read_bytes()
    codes = {'4411', '4412', '441', '5321', '532', '5324', '4853', '485', '484', '493', '4885', '48-49', '23', '721', '1'}
    buf = io.StringIO(); w = None; bc_sum = {}
    for row in csv.DictReader(io.StringIO(gzip.decompress(raw).decode('utf-8'))):
        m = re.search(r'\[([0-9-]+)\]$', row['naics'])
        if row['csduid'].startswith('59') and m and m.group(1) in codes and row['employment_size'] == 'Total, with employees' and row['value']:
            bc_sum[m.group(1)] = bc_sum.get(m.group(1), 0) + int(row['value'])
        if row['csduid'].startswith(MV_CD) and m and m.group(1) in codes:
            if w is None: w = csv.DictWriter(buf, fieldnames=list(row)); w.writeheader()
            w.writerow(row)
    bc = meta['sources']['businessCounts']['2026']
    log['businessCounts'] = {'from': str(path), 'sha256': sha(raw), 'upstreamTable': bc['table'], 'upstreamDownload': bc['download'], 'upstreamSha256': bc['sha256'],
                             'upstreamRetrievedAt': meta['retrievedAt'], 'title': 'Canadian Business Counts, with employees, census metropolitan areas and census subdivisions, June 2026',
                             'refDate': '2026-01 as published in REF_DATE', 'codes': sorted(codes), 'licence': meta['sources']['licence'],
                             'note': 'Six-digit NAICS (532111, 532112, 532120) are not published at census subdivision level in this table, the finest rental code is 5321.',
                             'extract': write('business-counts/business-counts-2026-metro-vancouver.csv', buf.getvalue().encode('utf-8')),
                             'bcSums': write('business-counts/business-counts-2026-bc-sums.csv', ('naics,bc_sum_of_published_csd_values\n' + ''.join(f'{k},{v}\n' for k, v in sorted(bc_sum.items()))).encode('utf-8'))}
    # AllThePlaces: BC chain rows for rental brands and vehicle dealers inside the search window.
    a = c / 'data/intl/alltheplaces'; man = json.loads((a / 'chains-manifest.json').read_bytes())
    path = a / 'chains/chains-bc.csv.gz'; raw = path.read_bytes()
    entry = next(f for f in man['files'] if f['region'] == 'BC')
    if sha(raw) != entry['sha256']: raise ValueError('AllThePlaces BC file does not match its manifest hash')
    buf = io.StringIO(); w = None; n = 0
    for row in csv.DictReader(io.StringIO(gzip.decompress(raw).decode('utf-8'))):
        if not (row['amenity'] in ('car_rental', 'truck_rental', 'car_sharing') or row['shop'] in ('car', 'truck')): continue
        try: lon, lat = float(row['longitude']), float(row['latitude'])
        except ValueError: continue
        if not (BBOX[0] < lon < BBOX[2] and BBOX[1] < lat < BBOX[3]): continue
        if w is None: w = csv.DictWriter(buf, fieldnames=list(row)); w.writeheader()
        w.writerow(row); n += 1
    log['alltheplaces'] = {'from': str(path), 'sha256': sha(raw), 'runId': man['runId'], 'runUrl': man['runUrl'], 'manifestCheckedAt': man['checkedAt'],
                           'licence': 'CC0-1.0 (AllThePlaces output), brand locator data', 'filter': 'amenity car_rental, truck_rental or car_sharing, or shop car or truck, inside the search window',
                           'rows': n, 'extract': write('alltheplaces/chains-bc-vehicle-metro-vancouver.csv', buf.getvalue().encode('utf-8'))}
    # Spider outputs that the regional extract lacks. Recorded with hashes, archived only if they hold Metro Vancouver points.
    tried = []
    for spider in ('uhaul', 'avis', 'penske', 'budget', 'thrifty', 'dollar', 'zipcar'):
        url = f'{ATP_RUN}/output/{spider}.geojson'; t = now()
        try: raw = get(url)
        except Exception as e: tried.append({'spider': spider, 'url': url, 'retrievedAt': t, 'status': str(e)}); continue
        fs = json.loads(raw)['features']
        mv = [f for f in fs if f.get('geometry') and BBOX[0] < f['geometry']['coordinates'][0] < BBOX[2] and BBOX[1] < f['geometry']['coordinates'][1] < BBOX[3]
              and (f['properties'].get('addr:country') or 'CA') == 'CA']
        rec = {'spider': spider, 'url': url, 'retrievedAt': t, 'rawSha256': sha(raw), 'features': len(fs), 'canadianInWindow': len(mv)}
        if mv: rec['extract'] = write(f'alltheplaces/{spider}-metro-vancouver.geojson', json.dumps({'type': 'FeatureCollection', 'features': mv}).encode())
        tried.append(rec)
    log['alltheplaces']['spiderOutputs'] = tried
    print('local sources done')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--consulting', default='/home/user/consulting'); args = ap.parse_args()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    log = {'generatedAt': now(), 'userAgent': UA, 'web': []}
    local_sources(log, args.consulting)
    fetch_overture(log)
    fetch_gtfs(log)
    fetch_statcan(log)
    fetch_web(log)
    (OUT / 'provenance.json').write_text(json.dumps(log, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
