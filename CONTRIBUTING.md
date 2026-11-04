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
| `status.level` | 0 to 6 on the cure ladder, for the typical patient. On a disease with variants it anchors the pooled forecast and history but isn't shown as a verdict. See [METHODOLOGY.md](METHODOLOGY.md#the-cure-ladder). |
| `status.why` | One plain sentence explaining the level. It shows on the disease's card. |
| `status.today` | Two or three sentences on what treatment can do now, and for whom. |
| `status.last_reviewed` | Date of the last full review, `YYYY-MM-DD`. |
| `treatment.best` | The best current treatments, short names. |
| `treatment.burden` | `light`, `moderate` or `heavy`. See [METHODOLOGY.md](METHODOLOGY.md#treatment-burden). |
| `treatment.burden_note` | One sentence on side effects, how long treatment lasts, and cost or access. |
| `forecast` | Optional for new diseases. See below. |
| `pipeline` | The most promising therapies in development: `name`, `stage`, `note`, `url`, plus optional `variants` (ids it applies to), `expected` (date of the next decisive event, `YYYY-MM-DD`, `YYYY-MM` or `YYYY`), `effect` (`big`, `some` or `small`: what a win would do to the estimate) and `effect_note` (one sentence). Items with an upcoming `expected` date show under "What could change it". |
| `recent` | Notable recent results: `date` (`YYYY-MM`), `text`, `url`. |
| `next_milestone` | The next dated event to watch: `date`, `what`, `url`. |
| `ai.impact`, `ai.note` | `high`, `some` or `low`: is AI plausibly speeding progress now? One sentence with an example. |
| `markets` | Forecasting-market questions about this disease: `who`, `what`, `url`. |

## Variants: stages and types

A disease whose stages or types are really different diseases (cancer stages, MS relapsing vs progressive) keeps each one in `diseases/<id>/variants/<variant-id>.yaml`, and each gets its own page under the disease's hub. Every cancer at level 4 or above needs them.

| Field | What it means |
|---|---|
| `id` | Same as the file name, lowercase-with-dashes, without repeating the disease (`stage-iv`, `relapsing`). |
| `name`, `order` | Display name (`Stage IV`) and position on the hub. |
| `what` | One plain sentence on what this stage or type is. |
| `level` | 0 to 6 on the cure ladder, rated as if it were its own disease. Level 4 needs at least ~85% cured; level 5 also needs a light burden. |
| `burden` | `light`, `moderate` or `heavy` for its standard treatment. |
| `survival`, `share` | Prognosis figure with its measure, and optionally the share of patients in this variant. |
| `treatment` | One or two sentences on the standard treatment, its toll, and whether it cures. |
| `caveat` | Optional: limits of the evidence or judgement calls. Shown on the page. |
| `url` | The page stating the survival figure. |
| `forecast` | Below level 4: when most patients with it will be curable (`median`, `low`, `high`, `p2035`, `p2045`, `note`, blended like the disease forecast). |
| `easy` | Below level 5: when the cure will get easy (same shape). |
| `reached`, `reached_easy` | At level 4+ / 5+: `year`, a one-line `basis` and a `url` for when it got there. |

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

Don't write the headline odds directly; the build blends the two tracks. A disease already at level 4 or above uses `forecast.reached: <year>` instead of the tracks, and at level 5 or above also `forecast.reached_easy: <year>`.

Proposed numbers are a starting point. The weekly review checks them against the base rates in METHODOLOGY.md and may change them.

## Ground rules

- Every claim should trace to a source in `research.md`.
- Plain language. Write for a smart reader who isn't a doctor.
- Describe treatments factually. Never recommend one.
- No personal medical stories or patient data.
- Paraphrase sources; keep quotes under 15 words.

## Review

A maintainer reviews every pull request. The weekly update may also revise facts as new evidence arrives, and logs what changed in `tracker/updates/`. Tag each change or news item with `disease: <id>` so it shows on that disease's estimate chart.
