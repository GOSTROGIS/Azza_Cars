import React, { Suspense, lazy, useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import { buildIndex, rank, highlight, parseQuery, compact } from "./search.js";
import { BODY_LABELS, BODY_ORDER, MARKETS, SOURCES, STATUS_LABELS, years } from "./labels.js";

const Viewer = lazy(() => import("./Viewer.jsx"));

const EMPTY_FILTERS = { bodies: [], markets: [], status: "all", from: "", to: "", brand: null };

function useCatalog() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    fetch("data/catalog.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);
  return { data, error };
}

function useHashSelection() {
  const read = () => decodeURIComponent(location.hash.replace(/^#\/?model\//, "")) || null;
  const [id, setId] = useState(read);
  useEffect(() => {
    const on = () => setId(read());
    addEventListener("hashchange", on);
    return () => removeEventListener("hashchange", on);
  }, []);
  const select = useCallback((next) => {
    history.replaceState(null, "", next ? `#/model/${encodeURIComponent(next)}` : location.pathname + location.search);
    setId(next);
  }, []);
  return [id, select];
}

function Highlighted({ text, words }) {
  return highlight(text, words).map((p, i) => (p.mark ? <mark key={i}>{p.text}</mark> : <span key={i}>{p.text}</span>));
}

function BrandMark({ brand, size = "sm" }) {
  if (brand?.logo) return <img className={`brandmark brandmark--${size}`} src={brand.logo} alt="" loading="lazy" />;
  const initials = (brand?.name || "?").replace(/\(.*\)/, "").trim().split(/\s+/).map((w) => w[0]).join("").slice(0, 2);
  return <span className={`brandmark brandmark--${size} brandmark--text`} aria-hidden="true">{initials}</span>;
}

/* ------------------------------------------------------------------ search box (combobox) */
function SearchBox({ index, query, setQuery, onPickModel, onPickBrand, ranked, words }) {
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const inputRef = useRef(null);
  const options = useMemo(() => {
    if (!words.length) return [];
    return [
      ...ranked.brands.slice(0, 3).map((b) => ({ kind: "brand", key: "b:" + b.slug, b })),
      ...ranked.models.slice(0, 8).map((m) => ({ kind: "model", key: "m:" + m.i, m })),
    ];
  }, [ranked, words]);

  useEffect(() => setActive(0), [ranked]);
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "/" && document.activeElement?.tagName !== "INPUT") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, []);

  const choose = (o) => {
    if (!o) return;
    setOpen(false);
    if (o.kind === "brand") onPickBrand(o.b.slug);
    else onPickModel(o.m.i);
  };
  const onKeyDown = (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setOpen(true); setActive((a) => Math.min(a + 1, options.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === "Enter") { e.preventDefault(); choose(options[active]); }
    else if (e.key === "Escape") { if (open) setOpen(false); else setQuery(""); }
  };
  const showList = open && options.length > 0;

  return (
    <div className="searchbox">
      <label htmlFor="q" className="az-visually-hidden">Search brands and models</label>
      <div className="searchbox__field">
        <svg className="searchbox__icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></svg>
        <input
          id="q"
          ref={inputRef}
          className="az-input searchbox__input"
          type="search"
          autoComplete="off"
          spellCheck="false"
          placeholder="Try crv, f150, camry 1998…"
          role="combobox"
          aria-expanded={showList}
          aria-controls="q-list"
          aria-autocomplete="list"
          aria-activedescendant={showList ? `opt-${active}` : undefined}
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 120)}
          onKeyDown={onKeyDown}
        />
        <span className="searchbox__hint" aria-hidden="true"><span className="az-kbd">/</span></span>
      </div>
      {showList && (
        <div className="searchbox__pop az-panel">
          <ul id="q-list" className="az-listbox" role="listbox" aria-label="Suggestions">
            {options.map((o, i) => {
              const b = o.kind === "brand" ? o.b : index.brandBySlug.get(o.m.b);
              return (
                <li key={o.key} id={`opt-${i}`} role="option" aria-selected={i === active} className="az-option"
                  onMouseDown={(e) => { e.preventDefault(); choose(o); }} onMouseEnter={() => setActive(i)}>
                  <BrandMark brand={b} />
                  {o.kind === "brand" ? (
                    <span><Highlighted text={b.name} words={words} /><br /><span className="az-muted small">Brand · {b.models.toLocaleString()} models</span></span>
                  ) : (
                    <span><Highlighted text={o.m.n} words={words} /><br /><span className="az-muted small">{b?.name} · {years(o.m)}{o.m.t.length ? " · " + o.m.t.map((t) => BODY_LABELS[t]).join(", ") : ""}</span></span>
                  )}
                  {o.kind === "brand" ? <span className="az-badge">Brand</span> : <span className={`az-badge az-badge--${o.m.s}`}>{STATUS_LABELS[o.m.s]}</span>}
                </li>
              );
            })}
          </ul>
          <div className="searchbox__foot az-muted small"><span className="az-kbd">↑</span><span className="az-kbd">↓</span> move <span className="az-kbd">Enter</span> open <span className="az-kbd">Esc</span> close</div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ filters */
function Chip({ pressed, onClick, children, count }) {
  return (
    <button type="button" className="az-chip" aria-pressed={pressed} onClick={onClick}>
      {children}{count != null && <span className="az-count">{count.toLocaleString()}</span>}
    </button>
  );
}

function Filters({ filters, setFilters, counts, yearBounds }) {
  const toggle = (key, v) => setFilters((f) => ({ ...f, [key]: f[key].includes(v) ? f[key].filter((x) => x !== v) : [...f[key], v] }));
  return (
    <div className="filters">
      <fieldset>
        <legend className="az-eyebrow">Body type</legend>
        <div className="chips">
          {BODY_ORDER.filter((b) => counts.bodies[b]).map((b) => (
            <Chip key={b} pressed={filters.bodies.includes(b)} onClick={() => toggle("bodies", b)} count={counts.bodies[b]}>{BODY_LABELS[b]}</Chip>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend className="az-eyebrow">Market</legend>
        <div className="chips">
          {MARKETS.map((m) => (
            <Chip key={m.id} pressed={filters.markets.includes(m.id)} onClick={() => toggle("markets", m.id)} count={counts.markets[m.id] || 0}>
              <span title={m.basis}>{m.id}</span>
            </Chip>
          ))}
        </div>
        <p className="az-muted small">US: vPIC or EPA lists it. CA: NRCan lists it. MX: INEGI reports sales.</p>
      </fieldset>
      <fieldset>
        <legend className="az-eyebrow">Status</legend>
        <div className="az-seg" role="group" aria-label="Status">
          {["all", "current", "discontinued", "unknown"].map((s) => (
            <button key={s} type="button" aria-pressed={filters.status === s} onClick={() => setFilters((f) => ({ ...f, status: s }))}>
              {s === "all" ? "All" : s === "unknown" ? "Unknown" : STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend className="az-eyebrow">Model years</legend>
        <div className="years">
          <label><span className="az-visually-hidden">From year</span>
            <input className="az-input az-input--sm" inputMode="numeric" placeholder={`From ${yearBounds[0]}`} value={filters.from}
              onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value.replace(/\D/g, "").slice(0, 4) }))} /></label>
          <span className="az-muted">to</span>
          <label><span className="az-visually-hidden">To year</span>
            <input className="az-input az-input--sm" inputMode="numeric" placeholder={`To ${yearBounds[1]}`} value={filters.to}
              onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value.replace(/\D/g, "").slice(0, 4) }))} /></label>
        </div>
      </fieldset>
      <button type="button" className="az-btn az-btn--ghost" onClick={() => setFilters(EMPTY_FILTERS)}>Reset filters</button>
    </div>
  );
}

/* ------------------------------------------------------------------ brand grid */
function BrandGrid({ brands, selected, onSelect }) {
  const [q, setQ] = useState("");
  const [seg, setSeg] = useState("all");
  const [expanded, setExpanded] = useState(false);
  const list = brands
    .filter((b) => b.models > 0)
    .filter((b) => seg === "all" || b.segment === seg)
    .filter((b) => !q || compact(b.name).includes(compact(q)))
    .sort((a, b) => (b.logo ? 1 : 0) - (a.logo ? 1 : 0) || b.models - a.models);
  const shown = expanded || q ? list : list.slice(0, 24);
  return (
    <section className="az-panel block" aria-labelledby="h-brands">
      <div className="block__head">
        <h2 className="az-h2" id="h-brands">Brands</h2>
        <div className="block__tools">
          <div className="az-seg" role="group" aria-label="Segment">
            {[["all", "All"], ["light", "Cars & light trucks"], ["truck", "Trucks"]].map(([v, l]) => (
              <button key={v} type="button" aria-pressed={seg === v} onClick={() => setSeg(v)}>{l}</button>
            ))}
          </div>
          <label className="brandfilter"><span className="az-visually-hidden">Filter brands</span>
            <input className="az-input az-input--sm" placeholder="Filter brands" value={q} onChange={(e) => setQ(e.target.value)} /></label>
        </div>
      </div>
      <div className="tiles">
        <button type="button" className="az-tile" aria-pressed={!selected} onClick={() => onSelect(null)}>
          <span className="az-tile__wordmark">All brands</span>
          <span className="az-tile__count">{brands.filter((b) => b.models).length}</span>
        </button>
        {shown.map((b) => (
          <button key={b.slug} type="button" className="az-tile" aria-pressed={selected === b.slug} onClick={() => onSelect(selected === b.slug ? null : b.slug)}>
            {b.logo ? <img className="az-tile__logo" src={b.logo} alt={`${b.name} logo`} loading="lazy" /> : null}
            <span className="az-tile__wordmark">{b.name}</span>
            {!b.logo && <span className="az-tile__note">{b.inegi_company ? "INEGI company group" : "Logo pending audit"}</span>}
            <span className="az-tile__count">{b.models.toLocaleString()} models</span>
          </button>
        ))}
      </div>
      {!q && list.length > 24 && (
        <button type="button" className="az-btn az-btn--ghost more" onClick={() => setExpanded((e) => !e)}>
          {expanded ? "Show fewer brands" : `Show all ${list.length} brands`}
        </button>
      )}
    </section>
  );
}

/* ------------------------------------------------------------------ results */
const ResultCard = React.memo(function ResultCard({ m, brand, words, selected, onSelect, has3d }) {
  return (
    <li>
      <button type="button" className={`az-card az-card--interactive result ${selected ? "az-card--selected" : ""}`} onClick={() => onSelect(m.i)} aria-pressed={selected}>
        <BrandMark brand={brand} />
        <span className="result__main">
          <span className="result__name"><Highlighted text={m.n} words={words} /></span>
          <span className="az-muted small">{brand?.name} · {years(m)}</span>
        </span>
        <span className="result__meta">
          {has3d && <span className="az-badge az-badge--current">3D</span>}
          {m.k.map((k) => <span key={k} className="az-badge az-badge--market">{k}</span>)}
          <span className={`az-badge az-badge--${m.s}`}>{STATUS_LABELS[m.s]}</span>
        </span>
      </button>
    </li>
  );
});

/* ------------------------------------------------------------------ detail */
function SourceList({ m }) {
  return (
    <ul className="sources">
      {Object.entries(m.src).map(([k, s]) => (
        <li key={k} className="source">
          <span className="source__name">{SOURCES[k]?.name || k}</span>
          <span className="az-muted small">{SOURCES[k]?.what}{s.years ? ` · model years ${s.years[0]}–${s.years[1]}` : ""}</span>
          {s.qids && <span className="small">{s.qids.slice(0, 4).map((q) => <a key={q} href={`https://www.wikidata.org/wiki/${q}`} target="_blank" rel="noreferrer">{q} </a>)}</span>}
          {s.model_ids && <span className="small az-mono">vPIC model id {s.model_ids.slice(0, 4).join(", ")}</span>}
          <a className="small" href={s.url} target="_blank" rel="noreferrer">Open source ↗</a>
        </li>
      ))}
    </ul>
  );
}

function Detail({ m, brand, vehicle, onClose }) {
  const mx = m.mx ? Object.entries(m.mx) : [];
  const mxMax = Math.max(1, ...mx.map(([, u]) => u));
  return (
    <article className="detail az-panel" aria-labelledby="detail-title">
      <div className="detail__head">
        <BrandMark brand={brand} size="lg" />
        <div>
          <div className="az-eyebrow">{brand?.name}</div>
          <h2 className="az-h1" id="detail-title">{m.n}</h2>
          <div className="az-muted">{years(m)}{m.yb === "wikidata" ? " (Wikidata dates)" : ""}</div>
        </div>
        <button type="button" className="az-btn az-btn--ghost detail__close" onClick={onClose} aria-label="Close details">✕</button>
      </div>
      {vehicle ? (
        <Suspense fallback={<div className="stage stage--loading">Loading 3D…</div>}>
          <Viewer vehicle={vehicle} />
        </Suspense>
      ) : (
        <div className="stage stage--empty"><span className="az-muted">No 3D recreation for this model yet.</span></div>
      )}
      <div className="detail__badges">
        <span className={`az-badge az-badge--${m.s}`}>{STATUS_LABELS[m.s]}</span>
        {m.k.map((k) => <span key={k} className="az-badge az-badge--market" title={MARKETS.find((x) => x.id === k)?.basis}>{k}</span>)}
        {m.t.map((t) => <span key={t} className="az-badge">{BODY_LABELS[t]}</span>)}
      </div>
      {m.co && <div className="az-notice" role="note">INEGI reports this model under the company “{m.co}” without naming the brand. It is listed here as reported.</div>}
      <dl className="facts">
        {Object.entries(m.c).map(([k, v]) => (
          <div key={k}><dt className="az-eyebrow">{SOURCES[k]?.name} class</dt><dd>{v.join(" · ")}</dd></div>
        ))}
        {m.a.length > 0 && <div><dt className="az-eyebrow">Also listed as</dt><dd className="small">{m.a.slice(0, 18).join(" · ")}{m.a.length > 18 ? ` and ${m.a.length - 18} more` : ""}</dd></div>}
      </dl>
      {mx.length > 0 && (
        <div className="mx">
          <div className="az-eyebrow">Mexico sales by year (INEGI RAIAVL)</div>
          <div className="mx__bars" role="img" aria-label={`Mexico sales: ${mx.map(([y, u]) => `${y}: ${u}`).join(", ")}`}>
            {mx.map(([y, u]) => <span key={y} className="mx__bar" style={{ height: `${Math.max(2, (u / mxMax) * 100)}%` }} title={`${y}: ${u.toLocaleString()} units`} />)}
          </div>
          <div className="mx__axis az-muted small"><span>{mx[0][0]}</span><span>{mx[mx.length - 1][0]}{+mx[mx.length - 1][0] === new Date().getFullYear() ? " (year to date)" : ""}</span></div>
        </div>
      )}
      <h3 className="az-h3">Sources</h3>
      <SourceList m={m} />
    </article>
  );
}

/* ------------------------------------------------------------------ featured 3D */
function Featured({ vehicles, models, onSelect }) {
  const [i, setI] = useState(0);
  if (!vehicles.length) return null;
  const v = vehicles[i];
  return (
    <section className="featured az-panel" aria-labelledby="h-3d">
      <div className="featured__copy">
        <div className="az-eyebrow">3D fleet preview</div>
        <h2 className="az-h1" id="h-3d">{v.name}</h2>
        <p className="az-muted">{v.generation}. Drag to orbit, scroll or pinch to zoom.</p>
        <div className="az-notice" role="note">Faithful recreation traced from public reference photos and cited dimensions. Not factory CAD, not identical to the real vehicle.</div>
        <div className="chips featured__tabs" role="tablist" aria-label="3D vehicles">
          {vehicles.map((x, j) => (
            <button key={x.slug} type="button" role="tab" aria-selected={j === i} className="az-chip" aria-pressed={j === i} onClick={() => setI(j)}>{x.short || x.name}</button>
          ))}
        </div>
        {models.has(v.catalog_id) && <button type="button" className="az-btn az-btn--primary" onClick={() => onSelect(v.catalog_id)}>View model details</button>}
      </div>
      <Suspense fallback={<div className="stage stage--loading">Loading 3D…</div>}>
        <Viewer vehicle={v} big />
      </Suspense>
    </section>
  );
}

/* ------------------------------------------------------------------ app */
export default function App() {
  const { data, error } = useCatalog();
  const [theme, setTheme] = useState(() => localStorage.getItem("az-theme") || "carbon");
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [limit, setLimit] = useState(60);
  const [selectedId, select] = useHashSelection();
  const deferredQuery = useDeferredValue(query);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem("az-theme", theme); } catch { /* private mode */ }
  }, [theme]);

  const index = useMemo(() => (data ? buildIndex(data.brands, data.models) : null), [data]);
  const byId = useMemo(() => new Map((data?.models || []).map((m) => [m.i, m])), [data]);
  const vehicleById = useMemo(() => new Map((data?.vehicles || []).map((v) => [v.catalog_id, v])), [data]);
  const yearBounds = useMemo(() => {
    if (!data) return [1900, 2027];
    const ys = data.models.flatMap((m) => m.y).filter((y) => y != null);
    return [Math.min(...ys), Math.max(...ys)];
  }, [data]);

  const accept = useMemo(() => {
    const from = filters.from.length === 4 ? +filters.from : null;
    const to = filters.to.length === 4 ? +filters.to : null;
    return (m) =>
      (!filters.brand || m.b === filters.brand) &&
      (!filters.bodies.length || m.t.some((t) => filters.bodies.includes(t))) &&
      (!filters.markets.length || filters.markets.every((k) => m.k.includes(k))) &&
      (filters.status === "all" || m.s === filters.status) &&
      (from == null || (m.y[1] ?? m.y[0]) >= from) &&
      (to == null || (m.y[0] ?? m.y[1]) <= to) &&
      (from == null && to == null ? true : m.y[0] != null || m.y[1] != null);
  }, [filters]);

  // Score once per query. Filters only re-filter the ranked list, they never re-score it.
  const words = useMemo(() => parseQuery(deferredQuery).words, [deferredQuery]);
  const ranked = useMemo(() => (index ? rank(index, deferredQuery) : { brands: [], models: [] }), [index, deferredQuery]);
  const results = useMemo(() => {
    const models = ranked.models.filter(accept);
    return { models, total: models.length };
  }, [ranked, accept]);

  // Facet counts for the current query and brand, ignoring the facets' own filters.
  const counts = useMemo(() => {
    const c = { bodies: {}, markets: {} };
    for (const m of ranked.models) {
      if (filters.brand && m.b !== filters.brand) continue;
      for (const t of m.t) c.bodies[t] = (c.bodies[t] || 0) + 1;
      for (const k of m.k) c.markets[k] = (c.markets[k] || 0) + 1;
    }
    return c;
  }, [ranked, filters.brand]);
  const setBrand = useCallback((slug) => setFilters((f) => ({ ...f, brand: slug })), []);

  useEffect(() => setLimit(60), [deferredQuery, filters]);

  if (error) return <main className="shell"><div className="az-notice">Could not load the catalog ({error}).</div></main>;
  if (!data) return <main className="shell loading"><div className="az-eyebrow">Loading catalog…</div></main>;

  const selected = selectedId ? byId.get(selectedId) : null;
  const brand = (slug) => index.brandBySlug.get(slug);
  const report = data.built;

  return (
    <>
      <a className="skip" href="#results">Skip to results</a>
      <header className="topbar">
        <div className="shell topbar__inner">
          <a className="wordmark" href="./" aria-label="Azza Cars home">AZZA<span>CARS</span></a>
          <nav className="topbar__nav" aria-label="Main">
            <a href="#h-brands">Brands</a>
            <a href="#results">Models</a>
            {data.vehicles.length > 0 && <a href="#h-3d">3D fleet</a>}
          </nav>
          <div className="az-seg" role="group" aria-label="Theme">
            <button type="button" aria-pressed={theme === "carbon"} onClick={() => setTheme("carbon")}>Carbon</button>
            <button type="button" aria-pressed={theme === "bone"} onClick={() => setTheme("bone")}>Bone</button>
          </div>
        </div>
      </header>

      <main className="shell">
        <section className="hero">
          <div className="az-eyebrow">Car &amp; truck rental · US · Canada · Mexico</div>
          <h1 className="az-display">Every brand.<br />Every model. <span className="az-accent">Cited.</span></h1>
          <p className="hero__lede az-muted">Search {report.models.toLocaleString()} models from {data.brands.filter((b) => b.models && !b.inegi_company).length} brands, built only from public sources: NHTSA vPIC, EPA, NRCan, INEGI and Wikidata.</p>
          <SearchBox index={index} query={query} setQuery={setQuery} ranked={ranked} words={words}
            onPickModel={select}
            onPickBrand={(slug) => { setBrand(slug); setQuery(""); document.getElementById("results")?.scrollIntoView({ behavior: "smooth" }); }} />
          <dl className="stats">
            <div className="az-stat"><dt className="az-stat__label">Models</dt><dd className="az-stat__value">{report.models.toLocaleString()}</dd></div>
            <div className="az-stat"><dt className="az-stat__label">Current</dt><dd className="az-stat__value">{report.by_status.current.toLocaleString()}</dd></div>
            <div className="az-stat"><dt className="az-stat__label">Audited logos</dt><dd className="az-stat__value">{report.logos_audited.length}</dd></div>
            <div className="az-stat"><dt className="az-stat__label">3D vehicles</dt><dd className="az-stat__value">{data.vehicles.length}</dd></div>
          </dl>
        </section>

        <Featured vehicles={data.vehicles} models={byId} onSelect={select} />

        <BrandGrid brands={data.brands} selected={filters.brand} onSelect={setBrand} />

        <div className={`workspace ${selected ? "workspace--detail" : ""}`}>
          <aside className="az-panel block filters-panel" aria-label="Filters">
            <Filters filters={filters} setFilters={setFilters} counts={counts} yearBounds={yearBounds} />
          </aside>
          <section className="results" id="results" aria-labelledby="h-results">
            <div className="block__head">
              <h2 className="az-h2" id="h-results">
                {filters.brand ? brand(filters.brand)?.name : "All models"}
                <span className="az-muted count"> {results.total.toLocaleString()}</span>
              </h2>
              {filters.brand && <button type="button" className="az-chip" aria-pressed="true" onClick={() => setBrand(null)}>{brand(filters.brand)?.name} ✕</button>}
            </div>
            <p className="az-visually-hidden" aria-live="polite">{results.total} models match</p>
            {results.total === 0 ? (
              <div className="az-notice">No models match. Try fewer filters or a shorter search.</div>
            ) : (
              <ul className="resultlist">
                {results.models.slice(0, limit).map((m) => (
                  <ResultCard key={m.i} m={m} brand={brand(m.b)} words={words} selected={m.i === selectedId} onSelect={select} has3d={vehicleById.has(m.i)} />
                ))}
              </ul>
            )}
            {results.models.length > limit && (
              <button type="button" className="az-btn more" onClick={() => setLimit((l) => l + 120)}>Show more ({(results.total - limit).toLocaleString()} left)</button>
            )}
          </section>
          {selected && (
            <div className="detail-wrap">
              <Detail m={selected} brand={brand(selected.b)} vehicle={vehicleById.get(selected.i)} onClose={() => select(null)} />
            </div>
          )}
        </div>
      </main>

      <footer className="shell footer az-muted small">
        <p>Data: NHTSA vPIC, EPA fueleconomy.gov, NRCan Fuel Consumption Ratings, INEGI RAIAVL, Wikidata. Each model lists its sources. Latest model year in the data: {report.latest_model_year}.</p>
        <p>Logos appear only after passing the Azza Cars logo audit. Brand logos are trademarks of their owners and do not imply sponsorship or endorsement.</p>
      </footer>
    </>
  );
}
