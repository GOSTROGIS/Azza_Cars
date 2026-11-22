# Working in this repo

## Ground rules

- **Never invent data.** Every brand, logo file and colour value must trace back to
  a source recorded in the repo. If something cannot be verified, flag it rather
  than guess.
- **Generated files are generated.** `register/brands.csv` and everything under
  `logos/audit/` come from scripts in `tools/`. Change the script or its input,
  then re-run. Do not hand-edit the output.
- **Keep source artwork untouched.** Files in `logos/sources/` are kept exactly as
  downloaded, so anyone can re-check them against their recorded SHA-256 hashes.
- **Nothing ships unverified.** An SVG goes into `logos/svg/` only after it passes the
  audit described in `logos/README.md`. Anything that fails stays listed as
  flagged until it is fixed.

## Folders

One folder per workstream, with a `README.md` in each that explains what it holds
and how it is produced. Tools live under `tools/<workstream>/`. Per-brand files use
the brand `slug` from `register/brands.csv` (lowercase, hyphenated, e.g.
`land-rover`).

## Tooling

- Python 3.11 or newer, plus `pillow`, `numpy` and `resvg_py` (`pip install pillow numpy resvg_py`)
- Node 18 or newer, for `npx svgo@4.0.0`

## Commits

Small commits with a clear subject line. Say what changed and why, and name the
sources touched when data changes.
