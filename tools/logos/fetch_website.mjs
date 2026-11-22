// Capture the logo each brand shows on its own website, as a third independent origin.
//
// For every target in work/website_targets.json the homepage is loaded in headless
// Chromium, and up to four logo-like elements are captured:
//   - inline <svg>: serialized with each shape's computed fill/stroke written onto it,
//     so colours set through CSS (currentColor, classes) are kept, and with <use>
//     references expanded so the file stands alone;
//   - <img> logos: the file at its src is downloaded unchanged.
// Files go to logos/sources/<slug>/website/, provenance to the "website" key of provenance.json.
//
// Usage:  node tools/logos/fetch_website.mjs [slug ...]
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Playwright is pre-installed globally in this environment, which ESM imports cannot see.
const { chromium } = createRequire(import.meta.url)('playwright');
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const only = new Set(process.argv.slice(2));
const targets = JSON.parse(readFileSync(join(ROOT, 'work', 'website_targets.json'), 'utf8'))
  .filter((t) => !only.size || only.has(t.slug));

// Runs in the page. Returns logo candidates in document order.
function collect() {
  const SELECTORS = [
    'header a[href="/"] svg', 'header a[href="/"] img',
    '[class*="logo" i] svg', '[id*="logo" i] svg', 'svg[class*="logo" i]', 'svg[aria-label*="logo" i]',
    'img[class*="logo" i]', 'img[alt*="logo" i]', 'img[src*="logo" i]', 'header svg', 'header img',
  ];
  const seen = new Set();
  const out = [];
  const PAINT = ['fill', 'stroke', 'stop-color', 'stop-opacity', 'fill-opacity', 'stroke-opacity',
    'stroke-width', 'opacity', 'fill-rule', 'clip-rule'];
  // Copy each element's computed paint onto its twin. Runs before any structural change,
  // so the original and the clone still line up element for element.
  const copyPaint = (orig, copy) => {
    const src = [orig, ...orig.querySelectorAll('*')];
    const dst = [copy, ...copy.querySelectorAll('*')];
    src.forEach((el, i) => {
      const cs = getComputedStyle(el);
      PAINT.forEach((p) => { const v = cs.getPropertyValue(p); if (v) dst[i].setAttribute(p, v); });
      dst[i].removeAttribute('class');
      dst[i].removeAttribute('style');
    });
  };
  const inlineSvg = (svg) => {
    const clone = svg.cloneNode(true);
    copyPaint(svg, clone);
    // expand <use href="#id"> so the file stands alone, painting the inserted copy from the referenced element
    clone.querySelectorAll('use').forEach((u) => {
      const ref = u.getAttribute('href') || u.getAttribute('xlink:href') || '';
      const target = ref.startsWith('#') ? document.getElementById(ref.slice(1)) : null;
      if (!target) return;
      const copy = target.cloneNode(true);
      copyPaint(target, copy);
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      [...u.attributes].forEach((a) => { if (!['href', 'xlink:href'].includes(a.name)) g.setAttribute(a.name, a.value); });
      const vb = target.getAttribute('viewBox');
      if (target.tagName.toLowerCase() === 'symbol' && vb && !clone.getAttribute('viewBox')) clone.setAttribute('viewBox', vb);
      [...copy.childNodes].forEach((n) => g.appendChild(n));
      u.replaceWith(g);
    });
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    if (!clone.getAttribute('viewBox')) {
      const b = svg.getBBox();
      clone.setAttribute('viewBox', `${b.x} ${b.y} ${b.width} ${b.height}`);
    }
    return clone.outerHTML;
  };
  for (const sel of SELECTORS) {
    for (const el of document.querySelectorAll(sel)) {
      if (seen.has(el) || out.length >= 4) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 20 || r.height < 8 || r.top > 400) continue;   // visible, in the page header
      seen.add(el);
      if (el.tagName.toLowerCase() === 'svg') out.push({ kind: 'svg', selector: sel, markup: inlineSvg(el), w: r.width, h: r.height });
      else if (el.currentSrc || el.src) out.push({ kind: 'img', selector: sel, src: el.currentSrc || el.src, w: r.width, h: r.height });
    }
  }
  return out;
}

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'en-US' });
for (const t of targets) {
  const folder = join(ROOT, 'logos', 'sources', t.slug, 'website');
  const record = { page_requested: t.url, retrieved_utc: new Date().toISOString(), files: [] };
  mkdirSync(folder, { recursive: true });
  const page = await context.newPage();
  try {
    const resp = await page.goto(t.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(4000);
    record.page_final = page.url();
    record.http_status = resp ? resp.status() : null;
    const found = await page.evaluate(collect);
    for (const [i, c] of found.entries()) {
      let blob; let ext;
      if (c.kind === 'svg') { blob = Buffer.from(c.markup, 'utf8'); ext = 'svg'; }
      else {
        const r = await context.request.get(c.src, { timeout: 30000 }).catch(() => null);
        if (!r || !r.ok()) { record.files.push({ selector: c.selector, src: c.src, error: r ? `HTTP ${r.status()}` : 'request failed' }); continue; }
        blob = await r.body();
        const type = r.headers()['content-type'] || '';
        ext = type.includes('svg') ? 'svg' : type.includes('png') ? 'png' : type.includes('webp') ? 'webp' : type.includes('jpeg') ? 'jpg' : 'bin';
      }
      const name = `logo-${i + 1}.${ext}`;
      writeFileSync(join(folder, name), blob);
      record.files.push({ saved_as: `website/${name}`, kind: c.kind, selector: c.selector, src: c.src || null,
        displayed_px: [Math.round(c.w), Math.round(c.h)], sha256: createHash('sha256').update(blob).digest('hex'), bytes: blob.length });
    }
  } catch (e) {
    record.error = String(e.message || e).split('\n')[0];
  }
  await page.close();
  const provPath = join(ROOT, 'logos', 'sources', t.slug, 'provenance.json');
  const prov = existsSync(provPath) ? JSON.parse(readFileSync(provPath, 'utf8')) : {};
  prov.website = record;
  writeFileSync(provPath, JSON.stringify(prov, null, 1));
  console.log(`${t.slug.padEnd(16)} ${record.error ? 'ERROR ' + record.error : `${record.files.filter((f) => f.sha256).length} files  (${record.http_status}) ${record.page_final}`}`);
}
await browser.close();
