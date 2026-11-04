# Contributing

Thanks for helping. The most useful contributions are:

- **A new disease** with solid sources.
- **A correction**: a fact that's wrong, out of date or missing a source.
- **A new source** for an existing disease, added to its `research.md`.
- **Research notes**: conflicting evidence, gaps or things to verify, added under "Open questions".

## Add a disease

1. Pick an id: lowercase words joined by dashes, like `cystic-fibrosis`. It becomes the folder name and the page address.
2. Copy `diseases/_template/` to `diseases/<id>/`.
3. Fill in `disease.yaml` (field guide below). Leave `tracking: proposed`.
4. In `research.md`, list at least two sources under `## Sources`, one per line:
   ```
   - [WHO fact sheet: Rabies](https://www.who.int/news-room/fact-sheets/detail/rabies) - deaths per year
   ```
5. Run `python scripts/validate.py` and fix anything it reports.
6. Open a pull request. The checks run the same validation.

The disease must fit a category in `categories.yaml`. If none fits, add one in the same pull request and say why.

## What makes a good source

Prefer, in roughly this order: regulators (FDA, EMA), WHO, CDC and national health agencies, peer-reviewed journals (NEJM, Lancet, JAMA, Nature Medicine), trial registries (ClinicalTrials.gov), and company press releases for trial results. Trade press is fine for news. Avoid blogs, forums and anything selling a treatment. Link the page that actually states the fact.

## disease.yaml field guide

| Field | What it means |
|---|---|
| `id` | Same as the folder name. |
| `name` | Display name. |
| `category` | An id from `categories.yaml`. |
| `tracking` | `proposed` for new diseases. The weekly review switches it to `active` once forecasts are in. |
| `summary` | One sentence: what the disease is. |
| `toll.text`, `toll.url` | How many people it affects, with year and source. |
| `status.level` | 0 to 5 on the cure ladder. See [METHODOLOGY.md](METHODOLOGY.md#the-cure-ladder). |
| `status.why` | One plain sentence explaining the level. It shows on the disease's card. |
| `status.today` | Two or three sentences on what treatment can do now, and for whom. |
| `status.groups` | Cancers: one entry per stage (`Stage 0` to `Stage IV`) or, for blood cancers, per subtype. Each has `name`, `what` (one plain sentence), `level` (0 to 5), `burden`, `survival`, optional `share` of new cases, `note`, optional `caveat` (limits of the evidence, shown on the page), `url` (the page stating the survival figure) and, for groups below level 4, `forecast` (`median`, `low`, `high`, `p2035`, `p2045` and a `note`, blended like the disease forecast). Required for level 4 cancers. See [METHODOLOGY.md](METHODOLOGY.md#the-cure-ladder). |
| `status.last_reviewed` | Date of the last full review, `YYYY-MM-DD`. |
| `treatment.best` | The best current treatments, short names. |
| `treatment.burden` | `light`, `moderate` or `heavy`. See [METHODOLOGY.md](METHODOLOGY.md#treatment-burden). |
| `treatment.burden_note` | One sentence on side effects, how long treatment lasts, and cost or access. |
| `forecast` | Optional for new diseases. See below. |
| `pipeline` | The most promising therapies in development: `name`, `stage`, `note`, `url`. |
| `recent` | Notable recent results: `date` (`YYYY-MM`), `text`, `url`. |
| `next_milestone` | The next dated event to watch: `date`, `what`, `url`. |
| `ai.impact`, `ai.note` | `high`, `some` or `low`: is AI plausibly speeding progress now? One sentence with an example. |
| `markets` | Forecasting-market questions about this disease: `who`, `what`, `url`. |

### Forecasts

New diseases can skip the `forecast` block; the weekly review fills it in. If you want to propose numbers, add both tracks:

```yaml
forecast:
  bottleneck: design-limited      # design-, biology-, trial- or access-limited
  normal:                         # at today's pace
    p2035: 5                      # % chance of level 4 by end of 2035
    p2045: 20
    median: 2050                  # best-guess year for level 4
    low: 2038                     # 10th percentile year
    high: 2090                    # 90th percentile year (2100 = after 2100)
  faster:                         # if the pipeline gets much faster by 2030
    p2035: 9
    p2045: 35
    median: 2045
    low: 2034
    high: 2080
  faster_note: One sentence on what a faster pipeline would change.
  outlook: Two or three sentences of reasoning.
```

Don't write the headline odds directly; the build blends the two tracks. A disease already at level 4 or 5 uses `forecast.reached: <year>` instead of the tracks.

Proposed numbers are a starting point. The weekly review checks them against the base rates in METHODOLOGY.md and may change them.

## Ground rules

- Every claim should trace to a source in `research.md`.
- Plain language. Write for a smart reader who isn't a doctor.
- Describe treatments factually. Never recommend one.
- No personal medical stories or patient data.
- Paraphrase sources; keep quotes under 15 words.

## Review

A maintainer reviews every pull request. The weekly update may also revise facts as new evidence arrives, and logs what changed in `tracker/updates/`. Tag each change or news item with `disease: <id>` so it shows on that disease's estimate chart.
