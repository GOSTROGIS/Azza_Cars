# tools/hero

Builds the website hero images: open-licence photos of popular vehicles with the background removed.
The site fades them into the page with a CSS mask.

## Run

```sh
python3 tools/hero/cutouts.py
```

`cutouts.json` lists each image: the credit label shown on the page, the Wikimedia Commons page, author, licence, an optional source crop,
and `clear_passes`. Each pass is a list of boxes, given as fractions of the cutout, where fragments of
other objects survived background removal. After each pass only the largest region is kept.

The script downloads the 1920 px Commons thumbnail (an original already in the cache is first scaled to that width) (Wikimedia asks automated clients to use its
standard thumbnail widths), retries on HTTP 429, 5xx and network errors (the shared catalog helper), and writes:

- `site/public/hero/<slug>.webp`: the cutout, at most 1200 px wide, WebP with alpha.
- `site/public/hero/provenance.json`: the source page, author, licence, download URL, SHA-256 and
  retrieval time per image, plus the rembg version and model.

## Licences

Each cutout is an adaptation of its photo. CC BY-SA sources are shared under the same licence.
The site must show credit (author, licence, link) wherever the images appear.
The landing page builds both its random vehicle pool and its footer photo credits from `provenance.json`
(`site/vite.config.js`, using each entry's `label`), so every cutout in the pool is credited. The build
fails if an image has a licence without a known licence link.

## Choosing photos

Use a true side profile, with the whole vehicle in frame and no other vehicle overlapping it.
A Nissan Versa photo was dropped because a car behind it merged with the roofline.

Requirements: `rembg[cpu]`, `opencv-python-headless`, `numpy`, `pillow`.
