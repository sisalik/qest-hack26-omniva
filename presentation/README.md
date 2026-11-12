# Presentation

The slides are written in Markdown with [Marp](https://marp.app/). `slides.md` is the whole deck; slides are separated by `---`.

## Requirements (from the organizers)

5 minutes + 2 minutes Q&A, delivered as **Google Slides**:

1. Business problem (1 min): why it is hard, how many qubits the full (not toy) problem needs, circuit scaling (linear or quadratic?)
2. Results, numbers and graphs (2.5 min)
3. Lessons learned (1 min)
4. Next steps (30 s)

Each slide has its time budget in the speaker notes (`<!-- ... -->` blocks).

## Editing and preview

- Install the VS Code extension **Marp for VS Code** (`marp-team.marp-vscode`).
- Open `slides.md` and click the preview icon in the top right corner: the slides update as you type.
- Orange `[…]` placeholders mark what still needs to be filled in.
- Put images (plots exported from the notebooks) in `img/` and reference them as `![w:900](img/name.png)`.

## Export to Google Slides

```bash
cd presentation
npx @marp-team/marp-cli@latest slides.md --pptx -o slides.pptx
```

Then upload `slides.pptx` to Google Drive and open it with Google Slides.

By default each slide is exported as an image, so text cannot be edited in Google Slides (speaker notes are kept). For editable text, add `--pptx-editable` (experimental, requires LibreOffice). PDF or HTML for a quick check: replace `--pptx` with `--pdf` or `--html`.

Exported files (`*.pptx`, `*.pdf`, `*.html`) are build outputs and are not committed.

## Sources for the numbers on the slides

The slides show numbers only; keep the sources here.

| Number | Where it is used | Source |
|---|---|---|
| 50 M parcels delivered in 2025 (+11%), 36 M of them in the Baltic states | Slide 2 | [Omniva press release, 23 Jan 2026](https://www.omniva.lt/en/news/record-parcel-volumes-omniva-delivered-50-million-parcels-last-year/) |
| Revenue ~€155 M in 2025 (+9%) | Slide 2 | [Omniva Group 2025 report](https://www.omnivagroup.com/?p=10957) |
| 387 public parcel lockers in Estonia, plan to grow to ~600; 35 → 19 post offices by end of 2026 | Slide 2 | [ERR, Nov 2025](https://www.err.ee/1609870779/eestis-jaab-alles-19-postkontorit) |
| 1,800+ employees and 1,400+ parcel machines across the Baltics | Not on the slides yet | [Omniva Group: About us](https://www.omnivagroup.com/about/in-brief/) |
| ~300 crowd couriers (rahvakullerid) under contract in 3 countries | Not on the slides yet | [Postimees, 30 Nov 2025](https://majandus.postimees.ee/8369358/omniva-katsetab-vaikelinnas-rahvatarne-teenust-mis-see-on) |
| 52 electric cars + 15 e-bikes, "just under 10%" of the fleet (undated) | Not on the slides | [VOOL × Omniva](https://www.vool.com/resources/blog/vool-joins-omniva-on-their-journey-towards-electrifying-transportation/) |
| Tallinn population ~457,000 | Slide 3 | [ERR, Mar 2026: Tallinn population forecast](https://www.err.ee/1609956554/uus-rahvastikuprognoos-pakub-tallinnale-vaiksemat-kasvu) |
| Estonia population 1,360,745 on 1 Jan 2026 (Statistics Estonia) | Slide 3 | [Global Estonian, Apr 2026](https://globalestonian.com/en/node/8754) |
| 94 Omniva parcel lockers in Tallinn (456 for all carriers), data updated 12 Nov 2026 | Slide 3 | [pakiautomaat24.eu/tallinn](https://www.pakiautomaat24.eu/tallinn) (aggregator, not an official Omniva count) |
| 50,000 parcels a day in Estonia | Slides 2–3 | Hackathon problem statement (`README.md` in the repo root) |

### Our own estimates (not published figures)

- **~17,000 parcels a day in Tallinn** = 50,000 × Tallinn's share of Estonia's population (457,000 / 1,360,745 ≈ 34%). Assumes parcels per person are the same across the country.
- **Qubits ≈ n²** for *n* stops with the start fixed at the depot (encoding "stop × position").
- **Two-qubit terms per QAOA layer ≈ 2n³**: n(n − 1)² distance terms between consecutive positions plus n²(n − 1) one-hot penalty terms, i.e. n(n − 1)(2n − 1).
- **Not found in open sources:** Estonia-only parcel volume, number of couriers or vans, share of parcels delivered to lockers vs. to the door. Ask the Omniva team members for internal numbers.
