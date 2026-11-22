"""Compute the TAM, SAM and SOM tables for Metro Vancouver car and truck rental.

Reads archived extracts in market/sources/ (run fetch_sources.py first) and the owner's
SOM assumptions in tools/market/som_inputs.json, and writes market/tam_sam_som.json.
market/TAM_SAM_SOM.md quotes that file.

Every sourced figure is read from an archived file, and web figures are checked against the
archived extract text, so a changed source fails loudly instead of drifting silently.

Usage: python tools/market/tam_sam_som.py
"""
import csv, json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / 'market' / 'sources'
YEAR = '2024'  # latest reference year of StatCan table 21-10-0012 (preliminary per the table notes)


def statcan(pid):
    return list(csv.DictReader(open(SRC / f'statcan/{pid}-canada-bc.csv', encoding='utf-8')))


def quote(key, phrase):
    """Confirm a phrase is present in an archived web extract and return the extract path."""
    path = SRC / f'web/{key}.txt'
    text = re.sub(r'\s+', ' ', path.read_text(encoding='utf-8'))
    if phrase not in text: raise ValueError(f'{key}: phrase not found: {phrase}')
    return f'market/sources/web/{key}.txt'


def main():
    prov = json.loads((SRC / 'provenance.json').read_text())
    rows = statcan('21100012')
    rev = {(r['REF_DATE'], r['GEO']): float(r['VALUE']) for r in rows if r['Summary statistics'] == 'Operating revenue'}
    margin = {(r['REF_DATE'], r['GEO']): float(r['VALUE']) for r in rows if r['Summary statistics'] == 'Operating profit margin'}
    clients = {r['Type of client']: float(r['VALUE']) for r in statcan('21100014') if r['REF_DATE'] == YEAR and r['GEO'] == 'Canada'}
    tam = {'year': YEAR, 'canada_musd': rev[(YEAR, 'Canada')], 'bc_musd': rev[(YEAR, 'British Columbia')],
           'bc_share_of_canada_pct': round(rev[(YEAR, 'British Columbia')] / rev[(YEAR, 'Canada')] * 100, 1),
           'bc_margin_pct': margin[(YEAR, 'British Columbia')], 'canada_margin_pct': margin[(YEAR, 'Canada')],
           'bc_series': {y: rev[(y, 'British Columbia')] for y in sorted({k[0] for k in rev}) if (y, 'British Columbia') in rev},
           'canada_client_mix_pct': clients, 'naics': 'Automotive equipment rental and leasing [5321]',
           'source': next(s for s in prov['statcan'] if s['table'] == '21100012'), 'clientSource': next(s for s in prov['statcan'] if s['table'] == '21100014'),
           'six_digit_split': 'not found. Table 21-10-0012 publishes NAICS 5321 only. 532111, 532112 and 532120 are not published separately in any current StatCan table listed by the WDS cube list (checked getAllCubesListLite for rental and leasing titles).'}

    # Allocation drivers, Metro Vancouver (census division 5915) over British Columbia.
    census = list(csv.DictReader(open(SRC / 'census/csd-profile-2021-metro-vancouver.csv')))
    bct = {r['measure']: float(r['value']) for r in csv.DictReader(open(SRC / 'census/bc-totals-2021.csv'))}
    mv_pop = sum(float(r['population_2021'] or 0) for r in census); mv_hh = sum(float(r['occupied_private_dwellings'] or 0) for r in census)
    bcc = {r['naics']: float(r['bc_sum_of_published_csd_values']) for r in csv.DictReader(open(SRC / 'business-counts/business-counts-2026-bc-sums.csv'))}
    mv_bc = {}
    for r in csv.DictReader(open(SRC / 'business-counts/business-counts-2026-metro-vancouver.csv')):
        if r['employment_size'] == 'Total, with employees' and r['value']:
            code = re.search(r'\[([0-9-]+)\]$', r['naics']).group(1); mv_bc[code] = mv_bc.get(code, 0) + int(r['value'])
    tourism_path = quote('destination-bc-vcm-profile-2026', '49% of BC')
    drivers = [
        {'method': 'Population, 2021 Census', 'mv': mv_pop, 'bc': bct['population_2021'], 'share': mv_pop / bct['population_2021'],
         'source': 'market/sources/census/csd-profile-2021-metro-vancouver.csv and census/bc-totals-2021.csv (Statistics Canada 2021 Census Profile)'},
        {'method': 'Private households, 2021 Census', 'mv': mv_hh, 'bc': bct['occupied_private_dwellings'], 'share': mv_hh / bct['occupied_private_dwellings'],
         'source': 'same as above, private dwellings occupied by usual residents'},
        {'method': 'Business locations with employees in NAICS 5321, June 2026 edition', 'mv': mv_bc['5321'], 'bc': bcc['5321'], 'share': mv_bc['5321'] / bcc['5321'],
         'source': 'market/sources/business-counts/ (Statistics Canada table 33-10-1176, REF_DATE 2026-01). BC denominator is the sum of published census subdivision values, so suppressed small places are missing from it.'},
        {'method': 'Tourism gross spending, Vancouver Coast and Mountains region, 2024', 'mv': None, 'bc': None, 'share': 0.49,
         'source': f'{tourism_path} (Destination BC regional profile, citing BC Stats). The region is larger than Metro Vancouver, so this is an upper bound.'},
        {'method': 'YVR passenger volume', 'mv': None, 'bc': None, 'share': None,
         'source': 'not found. A BC-wide airport passenger total to divide by was not sourced, so YVR volume is reported as context only.'},
    ]
    for d in drivers:
        d['sam_musd'] = round(tam['bc_musd'] * d['share'], 1) if d['share'] is not None else None
        d['share_pct'] = round(d['share'] * 100, 1) if d['share'] is not None else None
    vals = [d['sam_musd'] for d in drivers if d['sam_musd'] is not None]
    consumer = clients['Sales to individuals and households'] / 100
    sam = {'drivers': drivers, 'low_musd': min(vals), 'high_musd': max(vals),
           'consumer_slice_pct': clients['Sales to individuals and households'],
           'consumer_low_musd': round(min(vals) * consumer, 1), 'consumer_high_musd': round(max(vals) * consumer, 1),
           'leasing_exclusion': 'not possible from the data. NAICS 5321 revenue includes passenger car leasing and is not split by product in a current published table.'}

    # SOM, bottom up from owner inputs and cited benchmarks.
    inp = json.loads((REPO / 'tools/market/som_inputs.json').read_text())
    util_cite = quote('hertz-q4-2025-results', 'averaged 81% for the full year')
    scen = {}
    for name, s in inp['scenarios'].items():
        years = []
        for y, fleet in enumerate(s['fleet_by_year'], 1):
            revenue = fleet * 365 * s['utilisation'] * s['adr_cad']
            years.append({'year': y, 'fleet': fleet, 'vehicle_days': round(fleet * 365 * s['utilisation']), 'revenue_cad': round(revenue),
                          'share_of_sam_low_pct': round(revenue / (sam['high_musd'] * 1e6) * 100, 3),
                          'share_of_sam_high_pct': round(revenue / (sam['low_musd'] * 1e6) * 100, 3)})
        scen[name] = {**s, 'years': years}
    grid = {'utilisation': inp['sensitivity']['utilisation'], 'adr_cad': inp['sensitivity']['adr_cad'],
            'revenue_per_vehicle_year_cad': [[round(365 * u * a) for a in inp['sensitivity']['adr_cad']] for u in inp['sensitivity']['utilisation']]}
    out = {'tam': tam, 'sam': sam, 'som': {'inputs': inp, 'utilisation_benchmark': {'value': 0.81, 'what': 'Hertz Global, company-wide vehicle utilisation, full year 2025', 'source': util_cite},
                                           'scenarios': scen, 'sensitivity': grid}}
    (REPO / 'market/tam_sam_som.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    print(json.dumps({'tam': {k: v for k, v in tam.items() if k not in ('source', 'clientSource')}, 'sam': sam,
                      'som': {k: [(y['year'], y['fleet'], y['revenue_cad'], y['share_of_sam_low_pct'], y['share_of_sam_high_pct']) for y in v['years']] for k, v in scen.items()},
                      'grid': grid}, indent=1, default=str))


if __name__ == '__main__':
    main()
