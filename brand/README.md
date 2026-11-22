# brand

Naming and go-to-market research for the rental business.

| File | What it holds |
|---|---|
| `NAMING.md` | Candidate names, keyword signals, domain, handle and conflict checks, the shortlist and the recommendation |
| `MARKETING_REVIEW.md` | How rental brands market themselves, the channels that work for an independent operator, and a go-to-market plan for Metro Vancouver |
| `sources/` | The evidence behind both, with `provenance.json` giving each file's size and SHA-256 |

## How the evidence was gathered

- Domains: the GoDaddy domain availability tool, run on 22 November 2026. The `_raw.json` files keep the per-domain fields of those responses, trimmed. Batch 3 kept only the summary table. The `.tsv` files are summaries derived from the responses.
- Search demand: Google autocomplete only. Semrush and Ahrefs refused the requests (no API units, plan limit), so there are no search volumes.
- Social handles: an HTTP request per profile URL, keeping status and page title. Instagram and Facebook redirect to login and TikTok returns a generic page, so those results are inconclusive.
- Trademarks: web search and third-party aggregators. CIPO and USPTO were not queried directly. A trademark agent should run both before filing.

These checks were run once by hand through tools, not by a script in this repository.
