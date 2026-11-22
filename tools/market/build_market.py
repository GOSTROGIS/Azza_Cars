"""Build the Metro Vancouver supply layer, municipality metrics, station layer and map.

Reads only the archived extracts in market/sources/ (run fetch_sources.py first) and writes:
  market/supply.geojson          every rental, carshare and dealer location, deduplicated
  market/municipalities.csv      per municipality metrics, long field names
  market/municipalities.geojson  the same metrics on WGS84 polygons, field names of 10 characters or fewer
  market/stations.geojson        rapid transit stations with distance to the nearest rental location
  market/analysis.json           every number the written report quotes
  market/map.html                static Leaflet map

Usage: python tools/market/build_market.py
Needs: shapely.
"""
import csv, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
from shapely.geometry import shape, Point, mapping

REPO = Path(__file__).resolve().parents[2]
MARKET = REPO / 'market'
SRC = MARKET / 'sources'
CONF_MIN = 0.5  # Overture records below this confidence are kept in the layer but not counted
SITE_M = 60     # rental brands closer than this share one physical site (counter cluster)

# Boundary member slug to 2021 census subdivision code, checked against the census name below.
CSD = {'bowen-island': ('5915062', 'Bowen Island'), 'burnaby': ('5915025', 'Burnaby'), 'coquitlam': ('5915034', 'Coquitlam'), 'delta': ('5915011', 'Delta'),
       'langley-city': ('5915002', 'Langley'), 'maple-ridge': ('5915075', 'Maple Ridge'), 'new-westminster': ('5915029', 'New Westminster'),
       'north-vancouver-city': ('5915051', 'North Vancouver'), 'pitt-meadows': ('5915070', 'Pitt Meadows'), 'port-coquitlam': ('5915039', 'Port Coquitlam'),
       'port-moody': ('5915043', 'Port Moody'), 'richmond': ('5915015', 'Richmond'), 'surrey': ('5915004', 'Surrey'), 'vancouver': ('5915022', 'Vancouver'),
       'white-rock': ('5915007', 'White Rock'), 'west-vancouver': ('5915055', 'West Vancouver'), 'mvrd-ea-a': ('5915020', 'Metro Vancouver A'),
       'north-vancouver-district': ('5915046', 'North Vancouver'), 'langley-district': ('5915001', 'Langley'), 'anmore': ('5915038', 'Anmore'),
       'belcarra': ('5915036', 'Belcarra'), 'lions-bay': ('5915065', 'Lions Bay')}

# Overture taxonomy to supply category. rental_service is only kept for U-Haul dealers, matched by name.
OV_CATEGORY = {'car_rental_service': 'car_rental', 'truck_rental_service': 'truck_rental', 'trailer_rental_service': 'truck_rental',
               'car_sharing': 'carshare', 'rv_rental_service': 'rv_rental', 'auto_dealer': 'car_dealer', 'used_auto_dealer': 'used_dealer',
               'truck_dealer': 'truck_dealer', 'commercial_vehicle_dealer': 'truck_dealer', 'auto_leasing': 'car_leasing'}
RENTAL = {'car_rental', 'truck_rental', 'carshare'}
DEALER = {'car_dealer', 'used_dealer', 'truck_dealer'}
CARSHARE_BRANDS = {'Evo', 'Modo', 'Zipcar', 'Car2Go'}  # carshare operators, whatever their Overture category
# Rental and carshare brand patterns, applied to the name and the Overture brand.
BRANDS = [('Enterprise', r'\benterprise\b'), ('National', r'\bnational car rental\b|^national$'), ('Alamo', r'\balamo\b'), ('Hertz', r'\bhertz\b'),
          ('Dollar', r'\bdollar (car )?rent'), ('Thrifty', r'\bthrifty\b'), ('Avis', r'\bavis\b'), ('Budget', r'\bbudget\b'), ('Sixt', r'\bsixt\b'),
          ('U-Haul', r'u-?haul'), ('Penske', r'\bpenske\b'), ('Ryder', r'\bryder\b'), ('Evo', r'\bevo\b'), ('Modo', r'\bmodo\b'), ('Zipcar', r'zipcar'), ('Car2Go', r'car2go'),
          ('Discount', r'\bdiscount car'), ('Routes', r'\broutes\b'), ('Mr. Rent-A-Car', r'mr\.? rent'), ('Turo', r'\bturo\b'), ('Fox', r'\bfox rent')]


def brand_of(*texts):
    t = ' '.join(x for x in texts if x).lower()
    for b, pat in BRANDS:
        if re.search(pat, t): return b
    return ''


def metres(a, b):
    """Haversine distance between two (lon, lat) points in metres."""
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(h))


def norm_name(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


def load():
    prov = json.loads((SRC / 'provenance.json').read_text())
    members = json.loads((SRC / 'boundaries/members.geojson').read_text())['features']
    region = shape(json.loads((SRC / 'boundaries/region.geojson').read_text())['features'][0]['geometry'])
    census = {r['CSDUID']: r for r in csv.DictReader(open(SRC / 'census/csd-profile-2021-metro-vancouver.csv'))}
    bc = defaultdict(dict)
    for r in csv.DictReader(open(SRC / 'business-counts/business-counts-2026-metro-vancouver.csv')):
        if r['employment_size'] == 'Total, with employees':
            code = re.search(r'\[([0-9-]+)\]$', r['naics']).group(1)
            bc[r['csduid']][code] = int(r['value']) if r['value'] else None
            bc[r['csduid']]['_ref'] = r['ref_date']
    return prov, members, region, census, bc


def supply_records(prov):
    recs = []
    ov = json.loads((SRC / prov['overture']['extract']['path'].split('market/sources/')[1]).read_text())['features']
    for f in ov:
        p = f['properties']; cat = p['category']
        if p.get('operating_status') in ('permanently_closed', 'temporarily_closed'): continue
        sub = cat
        if cat == 'rental_service':
            if not re.search(r'u-?haul', (p['name'] or '').lower()): continue
            cat = 'truck_rental'
        elif cat in OV_CATEGORY: cat = OV_CATEGORY[cat]
        else: continue  # anchors and anything else
        brand = brand_of(p['name'], p['brand']) if cat in RENTAL | {'rv_rental'} else (p['brand'] or '')
        if brand in CARSHARE_BRANDS: cat = 'carshare'
        recs.append({'lonlat': tuple(f['geometry']['coordinates']), 'name': p['name'], 'brand': brand, 'category': cat, 'subcat': sub,
                     'source': 'overture', 'src_id': p['id'], 'conf': round(p['confidence'] or 0, 3), 'address': p.get('address') or '',
                     'upstream': ';'.join(p.get('sources') or [])})
    for r in csv.DictReader(open(SRC / prov['alltheplaces']['extract']['path'].split('market/sources/')[1])):
        if r['amenity'] == 'car_rental': cat = 'car_rental'
        elif r['amenity'] == 'truck_rental': cat = 'truck_rental'
        elif r['amenity'] == 'car_sharing': cat = 'carshare'
        elif r['shop'] == 'truck': cat = 'truck_dealer'
        elif r['shop'] == 'car': cat = 'car_dealer'
        else: continue
        brand = brand_of(r['brand'], r['name']) if cat in RENTAL else r['brand']
        recs.append({'lonlat': (float(r['longitude']), float(r['latitude'])), 'name': r['name'] or r['brand'], 'brand': brand or r['brand'], 'category': cat,
                     'subcat': r['amenity'] or r['shop'], 'source': 'alltheplaces', 'src_id': f"{r['spider']}:{r['ref']}", 'conf': 1.0,
                     'address': r['addr_full'] or ' '.join(x for x in (r['addr_street_address'], r['addr_city']) if x), 'upstream': r['source_uri']})
    return recs


def same_place(a, b):
    """Dedupe rule. Same category group, and one of: same brand within 250 m, same make in a dealer name within 150 m, or the same normalised name within 100 m."""
    ga = 'rental' if a['category'] in RENTAL | {'rv_rental'} else 'dealer'
    gb = 'rental' if b['category'] in RENTAL | {'rv_rental'} else 'dealer'
    if ga != gb: return False
    d = metres(a['lonlat'], b['lonlat'])
    if ga == 'rental':
        if a['brand'] and a['brand'] == b['brand'] and d <= 250: return True
    else:
        for x, y in ((a, b), (b, a)):
            if x['source'] == 'alltheplaces' and x['brand'] and x['brand'].lower() in norm_name(y['name']) and d <= 150: return True
    return norm_name(a['name']) == norm_name(b['name']) and d <= 100


def dedupe(recs):
    # AllThePlaces first, so a brand locator point is kept as the primary record when it matches an Overture place.
    recs = sorted(recs, key=lambda r: (r['source'] != 'alltheplaces', -r['conf'], r['src_id']))
    kept = []
    for r in recs:
        for k in kept:
            if same_place(k, r):
                k['dups'].append(f"{r['source']}:{r['src_id']}"); k['sources'].add(r['source'])
                if r['category'] in RENTAL and k['category'] not in RENTAL: k['category'] = r['category']
                k['conf'] = max(k['conf'], r['conf']); break
        else:
            kept.append({**r, 'dups': [], 'sources': {r['source']}})
    return kept


def main():
    prov, members, region, census, bc = load()
    polys = [(m['properties']['_slug'], m['properties']['ADMIN_AREA_NAME'], shape(m['geometry'])) for m in members]
    for slug, (code, name) in CSD.items():
        if not census[code]['CSDNAME'].startswith(name): raise ValueError(f'{slug}: census name {census[code]["CSDNAME"]} does not match {name}')
    raw = supply_records(prov)
    inside = []
    for r in raw:
        pt = Point(r['lonlat'])
        if not region.covers(pt): continue
        r['muni'] = next((s for s, _, g in polys if g.covers(pt)), 'other')
        inside.append(r)
    kept = dedupe(inside)
    for k in kept:
        k['counted'] = 'alltheplaces' in k['sources'] or k['conf'] >= CONF_MIN
    rentals = [k for k in kept if k['category'] in RENTAL and k['counted']]

    # Physical rental sites: counted rental brands within SITE_M metres of each other are one site.
    sites = []
    for r in sorted(rentals, key=lambda r: r['src_id']):
        for s in sites:
            if metres(s[0]['lonlat'], r['lonlat']) <= SITE_M: s.append(r); break
        else: sites.append([r])

    # Supply layer.
    feats = []
    for k in sorted(kept, key=lambda k: (k['category'], k['muni'], k['name'] or '')):
        feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(k['lonlat'][0], 6), round(k['lonlat'][1], 6)]},
                      'properties': {'name': k['name'], 'brand': k['brand'] or None, 'category': k['category'], 'subcat': k['subcat'], 'source': '+'.join(sorted(k['sources'])),
                                     'src_id': f"{k['source']}:{k['src_id']}", 'dup_ids': '|'.join(k['dups']) or None, 'conf': k['conf'], 'counted': k['counted'],
                                     'muni': k['muni'], 'address': k['address'] or None}})
    supply = {'type': 'FeatureCollection', 'name': 'supply',
              'attribution': 'Overture Maps Foundation (CDLA-Permissive-2.0) and AllThePlaces (CC0). See market/sources/provenance.json.', 'features': feats}
    (MARKET / 'supply.geojson').write_text(json.dumps(supply, ensure_ascii=False) + '\n')

    # Stations.
    stations = [s for s in csv.DictReader(open(SRC / 'translink/rapid-transit-stations.csv')) if region.covers(Point(float(s['lon']), float(s['lat'])))]
    st_feats = []
    for s in stations:
        ll = (float(s['lon']), float(s['lat']))
        ds = sorted((metres(ll, r['lonlat']), r) for r in rentals) if rentals else []
        near = ds[0] if ds else (None, None)
        muni = next((slug for slug, _, g in polys if g.covers(Point(ll))), 'other')
        st_feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [ll[0], ll[1]]},
                         'properties': {'name': s['name'], 'lines': s['lines'], 'muni': muni, 'near_m': round(near[0]) if near[0] is not None else None,
                                        'near_name': near[1]['name'] if near[1] else None, 'rent_1km': sum(1 for d, _ in ds if d <= 1000),
                                        'rent_2km': sum(1 for d, _ in ds if d <= 2000)}})
    (MARKET / 'stations.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'name': 'stations',
        'attribution': 'TransLink GTFS static feed, see market/sources/provenance.json', 'features': st_feats}, ensure_ascii=False) + '\n')

    # Municipalities.
    by = defaultdict(Counter)
    for k in kept:
        if k['counted']: by[k['muni']][k['category']] += 1
    rows, mfeats = [], []
    codes = ['4411', '4412', '441', '5321', '532', '5324', '484', '493', '4885', '48-49', '23', '721', '1']
    for slug, name, geom in polys:
        code = CSD[slug][0]; c = census[code]; pop = int(c['population_2021']); hh = int(c['occupied_private_dwellings']); b = bc.get(code, {})
        cnt = by[slug]; rent = sum(cnt[x] for x in RENTAL); deal = sum(cnt[x] for x in DEALER)
        st = [f for f in st_feats if f['properties']['muni'] == slug]
        row = {'slug': slug, 'name': name, 'csduid': code, 'population_2021': pop, 'households_2021': hh, 'land_area_km2': float(c['land_area_km2']),
               'rental_locations': rent, 'car_rental': cnt['car_rental'], 'truck_rental': cnt['truck_rental'], 'carshare': cnt['carshare'],
               'rentals_per_10k': round(rent / pop * 10000, 2) if pop else None, 'dealerships': deal,
               'dealers_per_10k': round(deal / pop * 10000, 2) if pop else None, 'rapid_transit_stations': len(st),
               'stations_no_rental_2km': sum(1 for f in st if f['properties']['rent_2km'] == 0)}
        for x in codes: row[f'bc_{x}'] = b.get(x)
        row['bc_ref_date'] = b.get('_ref')
        trades = (b.get('484') or 0) + (b.get('493') or 0) + (b.get('23') or 0)
        row['truck_rental_per_1k_trade_firms'] = round(cnt['truck_rental'] / trades * 1000, 2) if trades else None
        rows.append(row)
        short = {'slug': slug, 'name': name, 'csduid': code, 'pop21': pop, 'hh21': hh, 'rent_all': rent, 'rent_car': cnt['car_rental'],
                 'rent_trk': cnt['truck_rental'], 'rent_cshr': cnt['carshare'], 'rent_p10k': row['rentals_per_10k'], 'dealers': deal,
                 'deal_p10k': row['dealers_per_10k'], 'bc4411': b.get('4411'), 'bc5321': b.get('5321'), 'bc532': b.get('532'), 'bc484': b.get('484'),
                 'bc493': b.get('493'), 'bc23': b.get('23'), 'bc4849': b.get('48-49'), 'bc721': b.get('721'), 'bc_ref': b.get('_ref'),
                 'stations': len(st), 'st_no2km': row['stations_no_rental_2km'], 'trk_p1kt': row['truck_rental_per_1k_trade_firms']}
        mfeats.append({'type': 'Feature', 'geometry': mapping(geom.simplify(0.0001, preserve_topology=True)), 'properties': short})
    rows.sort(key=lambda r: -r['population_2021'])
    with open(MARKET / 'municipalities.csv', 'w', newline='') as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (MARKET / 'municipalities.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'name': 'municipalities',
        'attribution': 'Boundaries: Province of BC (OGL-BC). Census: Statistics Canada 2021 Census Profile (Open Licence). Business counts: Statistics Canada table 33-10-1176. Supply: Overture Maps, AllThePlaces.',
        'features': mfeats}, ensure_ascii=False) + '\n')

    # Anchors.
    anchors = {}
    for f in json.loads((SRC / prov['overture']['extract']['path'].split('market/sources/')[1]).read_text())['features']:
        p = f['properties']
        if p['category'] in ('airport', 'travel_and_transportation') and p['name'] in ('Vancouver International Airport', 'Port of Vancouver Cruise Ship Terminal'):
            if p['name'] not in anchors or (p['confidence'] or 0) > anchors[p['name']]['conf']:
                anchors[p['name']] = {'id': p['id'], 'conf': p['confidence'], 'lonlat': f['geometry']['coordinates']}
    anchor_stats = {}
    for n, a in anchors.items():
        near = [r for r in rentals if metres(a['lonlat'], r['lonlat']) <= 3000]
        anchor_stats[n] = {**a, 'rentals_3km': len(near), 'brands_3km': sorted(Counter(r['brand'] or 'unbranded' for r in near).items()),
                           'categories_3km': dict(Counter(r['category'] for r in near))}

    total_pop = sum(r['population_2021'] for r in rows)
    allc = Counter(k['category'] for k in kept if k['counted'])
    analysis = {
        'confidenceThreshold': CONF_MIN, 'siteRadiusM': SITE_M,
        'recordsRead': {'overture': sum(1 for r in raw if r['source'] == 'overture'), 'alltheplaces': sum(1 for r in raw if r['source'] == 'alltheplaces')},
        'insideRegion': len(inside), 'afterDedupe': len(kept), 'mergedDuplicates': len(inside) - len(kept),
        'crossSourceMatches': sum(1 for k in kept if len(k['sources']) > 1),
        'countedByCategory': dict(allc), 'allByCategory': dict(Counter(k['category'] for k in kept)),
        'rentalLocations': len(rentals), 'rentalSites': len(sites), 'rentalsOutsideMembers': sum(1 for r in rentals if r['muni'] == 'other'),
        'metroPopulation2021': total_pop, 'metroRentalsPer10k': round(sum(r['rental_locations'] for r in rows) / total_pop * 10000, 2),
        'rentalBrands': Counter(r['brand'] or 'unbranded' for r in rentals).most_common(),
        'rentalBrandsByCategory': {c: Counter(r['brand'] or 'unbranded' for r in rentals if r['category'] == c).most_common() for c in RENTAL},
        'anchors': anchor_stats,
        'stationsTotal': len(st_feats), 'stationsNoRental1km': sum(1 for f in st_feats if f['properties']['rent_1km'] == 0),
        'stationsNoRental2km': sorted([(f['properties']['name'], f['properties']['muni'], f['properties']['near_m']) for f in st_feats if f['properties']['rent_2km'] == 0], key=lambda x: -x[2]),
        'municipalities': rows,
    }
    (MARKET / 'analysis.json').write_text(json.dumps(analysis, indent=1, ensure_ascii=False) + '\n')
    write_map(mfeats, feats, st_feats)
    print(json.dumps({k: v for k, v in analysis.items() if k not in ('municipalities', 'stationsNoRental2km')}, indent=1)[:4000])


MAP = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Metro Vancouver Rental Supply</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>
:root { --bg: #ffffff; --fg: #1d1d1f; --muted: #5f6368; --panel: rgba(255,255,255,0.92); }
@media (prefers-color-scheme: dark) { :root { --bg: #121212; --fg: #f1f1f1; --muted: #b0b0b0; --panel: rgba(30,30,30,0.92); } }
html, body { margin: 0; height: 100%; background: var(--bg); color: var(--fg); font: 14px/1.4 system-ui, sans-serif; }
#map { position: absolute; inset: 0; }
.panel { background: var(--panel); color: var(--fg); padding: 8px 10px; border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,.3); max-width: 260px; }
.panel h1 { font-size: 15px; margin: 0 0 4px; }
.panel p { margin: 2px 0; color: var(--muted); font-size: 12px; }
.sw { display: inline-block; width: 14px; height: 10px; margin-right: 4px; vertical-align: middle; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
</style>
</head>
<body>
<div id="map"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
// Data is embedded so the page works from a local file. Generated by tools/market/build_market.py.
const MUNIS = __MUNIS__;
const SUPPLY = __SUPPLY__;
const STATIONS = __STATIONS__;
const map = L.map('map').setView([49.22, -122.95], 10);
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  maxZoom: 19, subdomains: 'abcd',
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a> | Places: <a href="https://overturemaps.org">Overture Maps Foundation</a>, <a href="https://www.alltheplaces.xyz">AllThePlaces</a> | Census: Statistics Canada | Boundaries: Province of BC | Stations: TransLink'
}).addTo(map);
const BREAKS = [0, 0.25, 0.5, 1, 2];
const COLORS = ['#f7fbff', '#c6dbef', '#6baed6', '#2171b5', '#08306b'];
function colour(v) { let c = COLORS[0]; BREAKS.forEach((b, i) => { if (v !== null && v >= b && (i > 0 || v > 0)) c = COLORS[i]; }); return v === 0 ? '#fde0dd' : c; }
const munis = L.geoJSON(MUNIS, {
  style: f => ({ color: '#555', weight: 1, fillOpacity: 0.6, fillColor: colour(f.properties.rent_p10k) }),
  onEachFeature: (f, l) => { const p = f.properties; l.bindPopup(`<b>${p.name}</b><br>Population 2021: ${p.pop21.toLocaleString()}<br>Rental locations: ${p.rent_all} (car ${p.rent_car}, truck ${p.rent_trk}, carshare ${p.rent_cshr})<br>Per 10,000 residents: ${p.rent_p10k}<br>Dealerships: ${p.dealers}<br>Business counts 5321: ${p.bc5321 ?? 'n/a'} (${p.bc_ref})`); }
}).addTo(map);
const CAT = { car_rental: '#d62728', truck_rental: '#ff7f0e', carshare: '#2ca02c', rv_rental: '#9467bd', car_dealer: '#7f7f7f', used_dealer: '#bcbd22', truck_dealer: '#8c564b', car_leasing: '#17becf' };
const layers = {};
SUPPLY.features.forEach(f => {
  const p = f.properties; const c = p.category;
  if (!layers[c]) layers[c] = L.layerGroup();
  L.circleMarker([f.geometry.coordinates[1], f.geometry.coordinates[0]], { radius: c.endsWith('rental') || c === 'carshare' ? 5 : 3, color: CAT[c], weight: 1, fillOpacity: p.counted ? 0.9 : 0.25 })
    .bindPopup(`<b>${p.name ?? ''}</b><br>${c}${p.brand ? ' | ' + p.brand : ''}<br>Source: ${p.source} (${p.src_id})<br>Confidence: ${p.conf}${p.counted ? '' : ' (not counted)'}`)
    .addTo(layers[c]);
});
['car_rental', 'truck_rental', 'carshare'].forEach(c => layers[c] && layers[c].addTo(map));
const st = L.layerGroup();
STATIONS.features.forEach(f => { const p = f.properties;
  L.circleMarker([f.geometry.coordinates[1], f.geometry.coordinates[0]], { radius: 4, color: '#000', weight: 1, fillColor: p.rent_2km === 0 ? '#000' : '#fff', fillOpacity: 1 })
    .bindPopup(`<b>${p.name}</b><br>${p.lines}<br>Nearest counted rental: ${p.near_m} m`).addTo(st); });
const overlays = { 'Rapid transit stations (black: no rental within 2 km)': st };
Object.keys(layers).sort().forEach(c => overlays[`<span class="dot" style="background:${CAT[c]}"></span>${c}`] = layers[c]);
L.control.layers({}, overlays, { collapsed: false }).addTo(map);
const info = L.control({ position: 'bottomleft' });
info.onAdd = () => { const d = L.DomUtil.create('div', 'panel');
  d.innerHTML = '<h1>Rental locations per 10,000 residents</h1>' + ['0', '0 to 0.25', '0.25 to 0.5', '0.5 to 1', '1 to 2', '2 and over'].map((t, i) =>
    `<div><span class="sw" style="background:${i === 0 ? '#fde0dd' : COLORS[i - 1]}"></span>${t}</div>`).join('') +
    '<p>Car rental, truck rental and carshare locations counted in market/supply.geojson, over 2021 Census population. Faded points are below the confidence threshold and are not counted.</p>';
  return d; };
info.addTo(map);
map.fitBounds(munis.getBounds());
</script>
</body>
</html>
'''


# Supply fields the map script reads. The full records stay in supply.geojson.
MAP_FIELDS = ('name', 'brand', 'category', 'conf', 'counted', 'source', 'src_id')


def write_map(mfeats, feats, st_feats):
    html = (MAP.replace('__MUNIS__', json.dumps({'type': 'FeatureCollection', 'features': mfeats}, separators=(',', ':')))
               .replace('__SUPPLY__', json.dumps({'type': 'FeatureCollection', 'features': [
                   {**f, 'properties': {k: f['properties'].get(k) for k in MAP_FIELDS}} for f in feats]}, separators=(',', ':')))
               .replace('__STATIONS__', json.dumps({'type': 'FeatureCollection', 'features': st_feats}, separators=(',', ':'))))
    (MARKET / 'map.html').write_text(html)


if __name__ == '__main__':
    main()
