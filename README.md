# Azza Cars

Everything for Azza Cars, a car and truck rental business, built from scratch.

The first workstream is a verified library of automotive brand logos in SVG,
for use in documents and on the website.

The second is the customer-facing website: the Ember Rent landing page, the business plan,
the market map and a popular-models page with real photos of Canada's 2025 best sellers.
The cited catalog of every model and the 3D vehicles below are kept as data, but the site no longer shows them.

## Repository layout

```
Azza_Cars/
├── README.md              This file
├── CONTRIBUTING.md        How to work in this repo
├── register/              Which brands exist, with sources (see register/README.md)
│   ├── candidates.csv     Hand-maintained input list
│   ├── brands.csv         Generated, cross-checked register (do not edit by hand)
│   └── sources/           Raw source responses, queries and hashes
├── logos/                 Brand logos (see logos/README.md)
│   ├── svg/               Final SVGs that passed the audit
│   ├── sources/           Downloaded source artwork and provenance, per brand
│   └── audit/             Renders, pixel diffs and audit reports, per brand
├── catalog/               Every model of every register brand, with sources (see catalog/README.md)
│   ├── models.json        Generated catalog (do not edit by hand)
│   └── sources/           Raw vPIC, EPA, NRCan, INEGI, Wikidata and sales-release files with hashes
├── design/                Design system: tokens, components, specimen (see design/README.md)
├── vehicles/              3D pipeline output: references, traced outlines, GLB, provenance (see vehicles/README.md)
├── market/                Metro Vancouver gap analysis, TAM/SAM/SOM, map and GIS layers (see market/README.md)
├── plan/                  Business plan, rendered as plan.html on the website (plan/BUSINESS_PLAN.md)
├── brand/                 Naming and marketing research, with sources (see brand/README.md)
├── site/                  Website, Vite with plain HTML pages (see site/README.md)
└── tools/                 Scripts, grouped by workstream
    ├── register/          Builds register/brands.csv
    ├── logos/             Fetches, rebuilds and audits logos
    ├── catalog/           Fetches sources and builds catalog/
    ├── design/            Contrast checks for design/
    └── vehicles/          Traces outlines and builds 3D vehicles
```

## Logo trademarks

Brand logos are trademarks of their owners. Azza Cars may show the logo of a make
it rents (for example, "Toyota vehicles available") without implying sponsorship
or endorsement. Do not alter the marks, and follow each owner's usage guidelines
where they are published.
