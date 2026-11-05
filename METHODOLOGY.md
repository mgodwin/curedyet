# Methodology

## The cure ladder

Each disease, and each stage or type of a disease, gets one level for the typical patient in rich countries.

| Level | Name | Meaning |
|---|---|---|
| 0 | No treatment | Nothing changes the course of the disease. |
| 1 | Slows it | Treatments slow it or ease symptoms, but it still advances. |
| 2 | Controlled | Near-normal life on ongoing treatment, but not cured. |
| 3 | Cured for some | A real cure or durable remission exists for a meaningful subset, or an approved curative therapy that only some patients can get, but fewer than about 85% of patients are cured. |
| 4 | Cured for most | At least about 85% of patients who get standard care are cured, and most could realistically tolerate and get that cure. |
| 5 | Cured for all | About 98% or more of patients are cured, or the disease is eradicated or reliably prevented at population scale. |

How hard the cure is gets rated separately, as the treatment burden below: mild, moderate or difficult. The goal is cured for most (or all) with mild treatment.

**The 85% line.** "Cured" means cured, not alive at five years. Where relapse after five years is common (hormone-positive breast cancer, ovarian cancer, high-risk prostate cancer), use long-term or cure-fraction data; five-year survival is a stand-in only where late relapse is rare. A cure too toxic, risky or costly for most patients to get stays at level 3, however well it works.

On the site the colour combines the rung and the burden. Cured for most or all is green with mild treatment, yellow with moderate treatment and orange with difficult treatment. Cured for some is orange whatever the treatment, since it doesn't cure most patients anyway. Levels 0 to 2 are grey. A cure for most that isn't mild yet is a waypoint, so those records also forecast when the treatment gets mild (`easy`), and records that are already mild give the year it got there (`reached_easy`).

**Stages and types.** A single level hides how different one disease can be across stages or types. Stage IV colorectal cancer is closer to a different disease than to stage I. So diseases with distinct stages or types keep each one as its own variant in `diseases/<id>/variants/`, rated on the same ladder with its own burden, prognosis, forecast, catalysts and estimate log, and each gets its own page. The disease page becomes a hub that lists them. The disease's overall level is kept for the typical patient across all variants, to anchor the pooled forecast and the history, but it is never shown as a verdict on a disease with variants, so nobody with metastatic disease is told their cancer is cured. The validator requires variants for every cancer at level 4 or above.

**Outbreak diseases** (Ebola, rabies and others) are rated by how well a patient can be treated once disease has started. Vaccines and post-exposure prevention are described in the text.

**Aging** uses the ladder for biological aging itself: 0 nothing proven to slow human aging, 1 something modestly slows aging measures, 2 something durably slows aging, 3 reversal for some, 4 most people can halt or reverse it. Aging also carries interim milestones with their own odds, so real progress shows before a full cure.

A level only changes on a discrete event: an approved curative therapy reaching a meaningful share of patients, or a change in standard care. Never on early-phase data alone.

## Treatment burden

Rates the best current standard option for a typical patient.

The data uses `light`, `moderate` and `heavy`; the site shows them as **mild**, **moderate** and **difficult** treatment.

- **Light**: a short course or easy treatment, mild and uncommon side effects, broadly affordable. Example: 8 to 12 weeks of hepatitis C pills.
- **Moderate**: ongoing or lifelong treatment, or real but manageable side effects, regular monitoring or meaningful cost. Example: GLP-1 obesity drugs.
- **Heavy**: serious risks (life-threatening toxicity, infertility, organ damage), intensive procedures (chemotherapy, transplant, surgery), heavy monitoring, or very high cost or poor access. Example: sickle cell gene therapy.

A safer or easier treatment counts as progress even when the level doesn't move.

## The prevention ladder

Infections get a second ladder for prevention: vaccines and preventive drugs, including pre-exposure (HIV PrEP) and post-exposure (rabies) prophylaxis. "Is it cured?" is only half the story for them: hepatitis B can rarely be cured but is almost fully prevented by a vaccine, and hepatitis C is the reverse.

| Level | Name | Meaning |
|---|---|---|
| 0 | No protection | No licensed vaccine or proven preventive drug. |
| 1 | Weak protection | The best licensed option cuts risk by less than about half, or its protection in people is unproven. |
| 2 | Partial protection | About 50 to 85% protection for those who get it. |
| 3 | Strong protection | About 85% or more protection for those who get it, licensed and in real use. |
| 4 | Eliminated | Prevention is used so widely the disease no longer spreads in most countries. |

The rung rates the best option for a typical person at risk. How hard it is to get and take is rated like treatment burden: **mild** (one lasting course, few side effects, cheap and broadly available), **moderate** (repeat doses, a daily pill, or real cost or access hurdles), **difficult** (urgent or intensive courses, serious risks, very high cost, or out of reach for most people at risk, such as outbreak-only use). Colours follow the cure ladder: strong or eliminated is green, yellow or orange by burden; partial is orange; weak or none is grey.

Prevention forecasts use the single-track variant shape: when strong protection will exist (`forecast`), and when it will also be easy to get and take (`easy`). Records already there give the year (`reached`, `reached_easy`). Where types of a disease differ in prevention (Ebola species), each type carries its own block.

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

### Update rules

- A track's odds can move 3+ points, or its year 2+ years, only if a cited forecasting market moved the same way or a discrete event happened (approval, rejection, pivotal trial result, program shutdown). Otherwise moves are capped at 2 points and 1 year.
- No single move larger than 10 points or 5 years in one update without a major event.
- If a forecast moves the same direction three updates running, it gets re-checked against markets and expert outlooks before moving again.
- Every disease gets a full re-review once a month. Updates run on the 1st, 8th, 15th and 22nd, and each covers one group of categories:
  - **1st**: cancers, plus the monthly review of the pipeline stages.
  - **8th**: infections and deadly outbreaks.
  - **15th**: brain and nerves, mental health, autoimmune, and aging and everyday conditions.
  - **22nd**: metabolic, genetic, heart and stroke, and eyes, kidneys and lungs.
- Every update also checks dated events for all diseases and refreshes the counts for active outbreaks. A major event, like an approval or a pivotal trial result, pulls a disease into that update out of turn. New diseases go into the next update, whatever their category.

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

## Tracking how estimates move

Each update saves a snapshot in `tracker/history/<date>.json` with every disease's level, best-guess year, optimistic year (`low`, the 10th percentile) and pessimistic year (`high`, the 90th). Each disease page charts these as **years until most patients are curable**, with the optimistic to pessimistic range as a band. Because time passes, the number falls by one each year even if the forecast never changes, so the chart also draws that "same forecast" line. A line falling faster than it means a cure is getting closer; a flat or rising line means it is slipping.

Changes and news in `tracker/updates/<date>.yaml` that carry a `disease: <id>` field appear on that disease's chart and in its list of what moved it.
