# Is it cured yet?

An open tracker of how close major diseases are to being cured. Each disease gets a place on a 0 to 5 cure ladder, a best-guess year for when most patients could be cured, the odds of that by 2035 and 2045, the burden of today's treatment, and the sources behind every claim.

It also tracks the **cure pipeline**: the six stages every cure moves through, how long each takes today, and how short each could get with AI and faster rules.

The site rebuilds from the files in this repo. Forecasts are refreshed every Thursday.

> A research tracker, not medical advice.

## What's in here

```
diseases/
  lymphoma/
    disease.yaml     the structured record: level, treatment, forecasts, pipeline
    research.md      sources, research log and open questions
  _template/         copy this to add a disease
pipeline/            one file per pipeline stage, with sourced durations
tracker/             weekly summary, short-range forecasts, calendar, history
categories.yaml      disease categories, in display order
scripts/             validate.py and build.py
site/                the web page that renders data.json
METHODOLOGY.md       the cure ladder, treatment burden, forecasts and base rates
CONTRIBUTING.md      how to add a disease or fix a fact
```

## Add a disease or fix a fact

1. Copy `diseases/_template/` to `diseases/<your-disease-id>/`.
2. Fill in `disease.yaml` and list at least two sources in `research.md`.
3. Run `python scripts/validate.py`.
4. Open a pull request.

You don't need to write forecasts. Leave `tracking: proposed` and the weekly review adds them. Full guide: [CONTRIBUTING.md](CONTRIBUTING.md).

## Run it locally

```sh
pip install pyyaml
python scripts/validate.py
python scripts/build.py
python -m http.server -d _site 8000   # open http://localhost:8000
```

## How the numbers are made

Each disease has two forecasts: one at today's pace and one where the drug pipeline gets much faster. The headline numbers blend the two by the **acceleration index**, the average chance each pipeline stage gets much faster by 2030. Forecasts start from shared base rates (about 1 in 10 drugs that enter human trials get approved, and past cures took decades) and move only on evidence. Dated yes-or-no forecasts in `tracker/checks.yaml` resolve within months and score the tracker's accuracy. Details: [METHODOLOGY.md](METHODOLOGY.md).

## License

Code is MIT. Data and text in `diseases/`, `pipeline/` and `tracker/` are CC BY 4.0. See [LICENSE.md](LICENSE.md).
