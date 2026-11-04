# Methodology

## The cure ladder

Each disease gets one level for the typical patient in rich countries.

| Level | Name | Meaning |
|---|---|---|
| 0 | No treatment | Nothing changes the course of the disease. |
| 1 | Slows it | Treatments slow it or ease symptoms, but it still advances. |
| 2 | Controlled | Near-normal life on ongoing treatment, but not cured. |
| 3 | Cured for some | A real cure or durable remission exists for a meaningful subset: some stages or subtypes, or an approved curative therapy that only some patients can get. |
| 4 | Cured for most | Most patients who get standard care can be cured, and most could realistically tolerate and get that cure. A cure too toxic, risky or costly for most patients stays at level 3. |
| 5 | Gone | Eradicated or reliably prevented at population scale. |

On the site, levels 0 to 2 read "Not yet", level 3 "For some", and levels 4 and 5 "Yes".

**Outbreak diseases** (Ebola, rabies and others) are rated by how well a patient can be treated once disease has started. Vaccines and post-exposure prevention are described in the text.

**Aging** uses the ladder for biological aging itself: 0 nothing proven to slow human aging, 1 something modestly slows aging measures, 2 something durably slows aging, 3 reversal for some, 4 most people can halt or reverse it. Aging also carries interim milestones with their own odds, so real progress shows before a full cure.

A level only changes on a discrete event: an approved curative therapy reaching a meaningful share of patients, or a change in standard care. Never on early-phase data alone.

## Treatment burden

Rates the best current standard option for a typical patient.

- **Light**: a short course or easy treatment, mild and uncommon side effects, broadly affordable. Example: 8 to 12 weeks of hepatitis C pills.
- **Moderate**: ongoing or lifelong treatment, or real but manageable side effects, regular monitoring or meaningful cost. Example: GLP-1 obesity drugs.
- **Heavy**: serious risks (life-threatening toxicity, infertility, organ damage), intensive procedures (chemotherapy, transplant, surgery), heavy monitoring, or very high cost or poor access. Example: sickle cell gene therapy.

A safer or easier treatment counts as progress even when the level doesn't move.

## Forecasts

For each disease below level 4:

- **Best guess** (`median`): the year most patients in rich countries could be cured (level 4).
- **Range** (`low`, `high`): 10th and 90th percentile years. 2100 means after 2100.
- **Chance by 2035 / 2045**: probability of level 4 by the end of that year.

Each is forecast twice:

- **Normal**: progress at roughly today's pace.
- **Faster**: the pipeline stages are broadly much faster by 2030.

The headline number is a blend, computed by the build:

```
blended = normal + (faster - normal) × acceleration index / 100
```

The **acceleration index** is the average, across the seven pipeline stages, of each stage's chance of getting much faster by 2030.

AI speeds discovery more than proof. Even a drug designed in 2029 usually needs years of human testing, so acceleration mostly moves the 2045 odds, not 2035.

### Base rates

Forecasts start from these and move only on evidence:

- About 1 in 10 drugs entering human trials are approved (oncology about 5%; hematology and rare genetic disease higher).
- Phase 3 to approval succeeds roughly 50 to 60% of the time.
- Clinical development takes 8 to 10 years; standard FDA review about 10 months, priority about 6.
- Real cures have taken decades. Hepatitis C: virus identified 1989, curative pills 2013. HIV: identified 1983, effective control 1996, still no cure.
- A level 0 or 1 disease with no Phase 3 curative candidate should usually have a normal-pace chance by 2035 under 5%.

### Weekly update rules

- A track's odds can move 3+ points, or its year 2+ years, only if a cited forecasting market moved the same way or a discrete event happened (approval, rejection, pivotal trial result, program shutdown). Otherwise moves are capped at 2 points and 1 year.
- No single move larger than 10 points or 5 years in a week without a major event.
- If a forecast moves the same direction three weeks running, it gets re-checked against markets and expert outlooks before moving again.
- Five diseases get a full re-review each week on rotation; the rest get a news sweep.

## The cure pipeline

Six sequential stages, from **disease discovered** to **cure reaches most patients**:

1. **Biology**: understanding the cause and picking a target.
2. **Design**: designing a drug that hits it.
3. **Lab testing**: showing it's safe enough to try in people.
4. **Trials**: Phase 1 through 3.
5. **Approval**: regulatory review.
6. **Access**: making it, paying for it and reaching most patients.

Plus one **booster**, **Simulation**: computer models that predict what a drug does in the body. It doesn't add time; it shortens lab testing and trials.

Each stage records a sourced **time today** and a **best case**. The best case is built from things that have already happened somewhere, like COVID vaccine trials finishing in about 7 months. Each stage also has a status:

- **Blocking**: still holding progress back.
- **Easing**: real progress, not solved yet.
- **Cleared**: solved in practice, not just announced.

For stages driven mostly by AI, the odds of getting much faster by 2030 are tied to AI capability scenarios: P(much faster | transformative AI) × P(transformative AI) + the same for "powerful but jagged" AI and for a plateau.

## Short-range forecasts and scoring

`tracker/checks.yaml` holds dated yes-or-no forecasts that resolve within 1 to 9 months, such as FDA decisions and trial readouts. Each resolved check is scored with the Brier score, `(forecast − outcome)²`. Lower is better; always guessing 50% scores 0.25. These are the tracker's honest accuracy test, since the long-range forecasts can't be scored for years.
