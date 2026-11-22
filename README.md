# Azza Cars

Everything for Azza Cars, a car and truck rental business, built from scratch.

The first workstream is a verified library of automotive brand logos in SVG,
for use in documents and on the website.

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
└── tools/                 Scripts, grouped by workstream
    ├── register/          Builds register/brands.csv
    └── logos/             Fetches, rebuilds and audits logos
```

## Logo trademarks

Brand logos are trademarks of their owners. Azza Cars may show the logo of a make
it rents (for example, "Toyota vehicles available") without implying sponsorship
or endorsement. Do not alter the marks, and follow each owner's usage guidelines
where they are published.
