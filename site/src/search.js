// Fuzzy search over brands and models. No dependencies.
// Forgiving by design: "crv" finds CR-V, "f150" finds F-150, "camery" finds Camry,
// "toyota rav" narrows to Toyota, and a four-digit year such as "1998" filters by model year.
//
// rank() scores the query once. Filters are applied afterwards by the caller, so toggling a
// filter never re-scores the catalog.

export const fold = (s) =>
  (s || "")
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
export const compact = (s) => fold(s).replace(/[^a-z0-9]/g, "");
const tokens = (s) => fold(s).split(/[^a-z0-9]+/).filter(Boolean);
const field = (s) => ({ c: compact(s), t: tokens(s) });

// Damerau-Levenshtein distance with an early exit once it passes max.
function editDistance(a, b, max) {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev2 = [];
  let prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const cur = [i];
    let rowMin = i;
    for (let j = 1; j <= b.length; j++) {
      let v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, prev2[j - 2] + 1);
      cur[j] = v;
      if (v < rowMin) rowMin = v;
    }
    if (rowMin > max) return max + 1;
    prev2 = prev;
    prev = cur;
  }
  return prev[b.length];
}

// How well one query token matches one field ({c: compact, t: tokens}). 0 means no match.
function tokenScore(q, f, fuzzy) {
  if (f.c === q) return 100;
  if (f.c.startsWith(q)) return 85 - Math.min(20, f.c.length - q.length);
  if (f.t.includes(q)) return 80;
  if (f.t.some((t) => t.startsWith(q))) return 70;
  if (q.length >= 2 && f.c.includes(q)) return 55;
  if (fuzzy && q.length >= 4) {
    const max = q.length >= 7 ? 2 : 1;
    const near = (t) => editDistance(q, t.length > q.length + max ? t.slice(0, q.length + max) : t, max) <= max;
    if (near(f.c) || f.t.some(near)) return 40;
  }
  return 0;
}

function bestField(q, fields, fuzzy) {
  let best = 0;
  for (const f of fields) {
    const s = tokenScore(q, f, fuzzy);
    if (s > best) best = s;
    if (best === 100) break;
  }
  return best;
}

export function buildIndex(brands, models) {
  const brandBySlug = new Map(brands.map((b) => [b.slug, b]));
  const brandEntries = brands.map((b) => ({ item: b, fields: [field(b.name), field(b.slug.replace(/-/g, " "))] }));
  const modelEntries = models.map((m) => ({
    item: m,
    brand: field(brandBySlug.get(m.b)?.name),
    fields: [m.n, ...m.a].map(field),
    // Prominence: current models and models confirmed by more sources and markets rank higher.
    boost: (m.s === "current" ? 6 : 0) + 2 * m.k.length + 2 * Object.keys(m.src).length,
  }));
  return { brandBySlug, brandEntries, modelEntries };
}

export function parseQuery(query) {
  let year = null;
  const words = [];
  for (const t of tokens(query)) {
    if (year === null && /^(19|20)\d\d$/.test(t)) year = +t;
    else words.push(t);
  }
  return { words, year, whole: words.join("") };
}

function scoreModels(index, words, whole, yearOk, fuzzy) {
  const scored = [];
  const need = Math.ceil(words.length / 2);
  for (const e of index.modelEntries) {
    if (!yearOk(e.item)) continue;
    // Whole query against the model name first, so "cr v" and "f 150" match CR-V and F-150.
    let total = whole.length >= 2 ? bestField(whole, e.fields, fuzzy) * 1.2 : 0;
    if (!total) {
      let modelHits = 0;
      let hits = 0;
      for (const w of words) {
        // A one-word query was already scored against the model fields as the whole query.
        const sm = words.length === 1 && whole.length >= 2 ? 0 : bestField(w, e.fields, fuzzy);
        const sb = tokenScore(w, e.brand, fuzzy) * 0.6;
        const s = Math.max(sm, sb);
        if (s) hits++;
        else total -= 30; // an unmatched word costs, it does not exclude ("silverado 1500")
        if (sm && sm >= sb) modelHits++;
        total += s;
      }
      if (hits < need || !modelHits) total = 0;
    }
    if (total > 0) scored.push({ item: e.item, score: total + e.boost });
  }
  return scored;
}

// Scores every model and brand against the query. Returns models best first (all of them when
// the query is empty) and up to 8 brands.
export function rank(index, query) {
  const { words, year, whole } = parseQuery(query);
  const yearOk = (m) => year === null || (m.y[0] != null && m.y[0] <= year && year <= (m.y[1] ?? m.y[0]));
  if (!words.length) return { brands: [], models: index.modelEntries.map((e) => e.item).filter(yearOk) };

  const brands = [];
  for (const e of index.brandEntries) {
    let total = 0;
    for (const w of words) {
      const s = bestField(w, e.fields, true);
      if (!s) { total = 0; break; }
      total += s;
    }
    if (total) brands.push({ item: e.item, score: total });
  }
  brands.sort((a, b) => b.score - a.score);

  // Exact and prefix matching first. Typo-tolerant matching runs only when that finds little.
  let scored = scoreModels(index, words, whole, yearOk, false);
  if (scored.length < 5) scored = scoreModels(index, words, whole, yearOk, true);
  scored.sort((a, b) => b.score - a.score || (b.item.y[1] ?? 0) - (a.item.y[1] ?? 0));
  return { brands: brands.slice(0, 8).map((r) => r.item), models: scored.map((r) => r.item) };
}

// Splits text into marked and unmarked parts. Matching ignores punctuation and spacing,
// so "crv" marks all of "CR-V" and "f150" marks "F-150".
export function highlight(text, words) {
  const chars = [...text];
  const pos = []; // index in chars of each compact character
  let flat = "";
  chars.forEach((ch, i) => {
    const c = compact(ch);
    for (const x of c) { flat += x; pos.push(i); }
  });
  const marks = new Array(chars.length).fill(false);
  for (const w of [words.join(""), ...words]) {
    const at = w ? flat.indexOf(w) : -1;
    if (at < 0) continue;
    for (let i = pos[at]; i <= pos[at + w.length - 1]; i++) marks[i] = true;
    if (w === words.join("")) break;
  }
  const parts = [];
  chars.forEach((ch, i) => {
    const last = parts[parts.length - 1];
    if (last && last.mark === marks[i]) last.text += ch;
    else parts.push({ text: ch, mark: marks[i] });
  });
  return parts;
}
