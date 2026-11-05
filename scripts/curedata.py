"""Load, validate and compile the Cure Watch data in this repo.

Every disease lives in diseases/<id>/ as disease.yaml (structured record) plus
research.md (sources and research notes). Pipeline stages live in pipeline/,
weekly tracker state in tracker/. build.py turns all of it into one data.json
that the static site reads.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
# How hard the treatment is (mild/moderate/difficult) is a separate axis, read from burden, not a rung.
LEVELS = ["No treatment", "Slows it", "Controlled", "Cured for some", "Cured for most", "Cured for all"]
MAX_LEVEL = len(LEVELS) - 1
BURDENS = {"light", "moderate", "heavy"}
BOTTLENECKS = {"design-limited", "biology-limited", "trial-limited", "access-limited"}
TRACKING = {"active", "proposed"}
STAGE_STATUS = {"blocking", "easing", "cleared"}
AI_IMPACT = {"high", "some", "low"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL_RE = re.compile(r"^https?://\S+$")
SOURCE_LINE = re.compile(r"^\s*[-*]\s+\[(?P<title>[^\]]+)\]\((?P<url>https?://[^\s)]+)\)\s*(?:[-:–]\s*(?P<note>.*))?$")


def read_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_research(path: Path) -> dict:
    """Return {"sources": [...], "text": str} from a research.md file.

    Sources are the markdown links listed under a "## Sources" heading:
    - [Title](https://example.org/page) - optional note
    """
    text = path.read_text(encoding="utf-8")
    sources, in_sources = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            in_sources = line[3:].strip().lower() == "sources"
            continue
        if in_sources:
            m = SOURCE_LINE.match(line)
            if m:
                sources.append({"title": m["title"].strip(), "url": m["url"], "note": (m["note"] or "").strip() or None})
    return {"sources": sources, "text": text}


def load_all() -> dict:
    cats = read_yaml(ROOT / "categories.yaml") or []
    diseases = []
    for folder in sorted((ROOT / "diseases").iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        rec = read_yaml(folder / "disease.yaml") if (folder / "disease.yaml").exists() else None
        research = parse_research(folder / "research.md") if (folder / "research.md").exists() else None
        variants = [dict(read_yaml(p) or {}, _file=p.stem) for p in sorted((folder / "variants").glob("*.yaml"))]
        variants.sort(key=lambda v: (v.get("order") if _is_int(v.get("order")) else 999, v["_file"]))
        diseases.append({"folder": folder.name, "record": rec, "research": research, "variants": variants})
    stages = [read_yaml(p) for p in sorted((ROOT / "pipeline").glob("*.yaml"))]
    tr = ROOT / "tracker"
    meta = read_yaml(tr / "meta.yaml") or {}
    checks = read_yaml(tr / "checks.yaml") or []
    calendar = read_yaml(tr / "calendar.yaml") or []
    updates = [read_yaml(p) for p in sorted((tr / "updates").glob("*.yaml"), reverse=True)]
    history = [json.loads(p.read_text()) for p in sorted((tr / "history").glob("*.json"), reverse=True)]
    return {"categories": cats, "diseases": diseases, "stages": stages, "meta": meta,
            "checks": checks, "calendar": calendar, "updates": updates, "history": history}


# ---------------------------------------------------------------- validation

def _is_int(v, lo=None, hi=None):
    return isinstance(v, int) and not isinstance(v, bool) and (lo is None or v >= lo) and (hi is None or v <= hi)


def validate_track(name, t, errs, where):
    if not isinstance(t, dict):
        errs.append(f"{where}: forecast.{name} must be a mapping"); return
    for k in ("p2035", "p2045"):
        if not _is_int(t.get(k), 0, 100):
            errs.append(f"{where}: forecast.{name}.{k} must be a whole number 0-100")
    for k in ("median", "low", "high"):
        if not _is_int(t.get(k), 1900, 2100):
            errs.append(f"{where}: forecast.{name}.{k} must be a year (2100 means after 2100)")
    if all(_is_int(t.get(k)) for k in ("p2035", "p2045")) and t["p2035"] > t["p2045"]:
        errs.append(f"{where}: forecast.{name}.p2035 can't be higher than p2045")
    if all(_is_int(t.get(k)) for k in ("low", "median", "high")) and not (t["low"] <= t["median"] <= t["high"]):
        errs.append(f"{where}: forecast.{name} years must satisfy low <= median <= high")


EFFECTS = {"big", "some", "small"}


def validate_forecast(f, errs, where, name):
    if not isinstance(f, dict) or not all(_is_int(f.get(k)) for k in ("median", "low", "high", "p2035", "p2045")):
        errs.append(f"{where}: {name} needs integer median, low, high, p2035 and p2045"); return
    if not (f["low"] <= f["median"] <= f["high"] <= 2100 and 0 <= f["p2035"] <= f["p2045"] <= 100):
        errs.append(f"{where}: {name} needs low <= median <= high <= 2100 and 0 <= p2035 <= p2045 <= 100")


def validate_reached(r, errs, where, name):
    if not isinstance(r, dict) or not _is_int(r.get("year"), 1800, 2100) or not str(r.get("basis") or "").strip():
        errs.append(f"{where}: {name} needs a year and a one-line basis")
    elif r.get("url") and not URL_RE.match(str(r["url"])):
        errs.append(f"{where}: {name}.url must be an http(s) link")


def validate_variant(v, errs, where):
    if v.get("id") != v["_file"] or not ID_RE.match(str(v.get("id"))):
        errs.append(f"{where}: id must match the file name, lowercase-with-dashes")
    for k in ("name", "treatment"):
        if not isinstance(v.get(k), str) or not v[k].strip():
            errs.append(f"{where}: '{k}' is required")
    if not _is_int(v.get("order"), 1):
        errs.append(f"{where}: order must be a whole number from 1")
    level = v.get("level")
    if not _is_int(level, 0, MAX_LEVEL):
        errs.append(f"{where}: level must be 0-{MAX_LEVEL}"); level = 0
    if v.get("burden") not in BURDENS:
        errs.append(f"{where}: burden must be light, moderate or heavy")
    for k in ("url", "share_url"):
        if v.get(k) and not URL_RE.match(str(v[k])):
            errs.append(f"{where}: {k} must be an http(s) link")
    if v.get("forecast") is not None:
        if level >= 4:
            errs.append(f"{where}: forecast is for reaching level 4; this variant is already there")
        else:
            validate_forecast(v["forecast"], errs, where, "forecast")
    mild = level >= 4 and v.get("burden") == "light"
    if v.get("easy") is not None:
        if mild:
            errs.append(f"{where}: easy is for when cured for most gets mild treatment; this variant already has it")
        else:
            validate_forecast(v["easy"], errs, where, "easy")
    if level >= 4:
        validate_reached(v.get("reached"), errs, where, "reached")
    if mild:
        validate_reached(v.get("reached_easy"), errs, where, "reached_easy")


def validate(data: dict) -> list[str]:
    errs: list[str] = []
    cat_ids = {c.get("id") for c in data["categories"]}
    seen = set()
    for d in data["diseases"]:
        where = f"diseases/{d['folder']}"
        rec, research = d["record"], d["research"]
        if rec is None:
            errs.append(f"{where}: missing disease.yaml"); continue
        if research is None:
            errs.append(f"{where}: missing research.md")
        if not ID_RE.match(d["folder"]):
            errs.append(f"{where}: folder name must be lowercase-with-dashes")
        if rec.get("id") != d["folder"]:
            errs.append(f"{where}: id '{rec.get('id')}' must match the folder name")
        if rec.get("id") in seen:
            errs.append(f"{where}: duplicate id")
        seen.add(rec.get("id"))
        for k in ("name", "summary"):
            if not isinstance(rec.get(k), str) or not rec[k].strip():
                errs.append(f"{where}: '{k}' is required")
        if rec.get("category") not in cat_ids:
            errs.append(f"{where}: category '{rec.get('category')}' isn't in categories.yaml")
        tracking = rec.get("tracking", "proposed")
        if tracking not in TRACKING:
            errs.append(f"{where}: tracking must be 'active' or 'proposed'")
        st = rec.get("status") or {}
        if not _is_int(st.get("level"), 0, MAX_LEVEL):
            errs.append(f"{where}: status.level must be 0-{MAX_LEVEL} (see METHODOLOGY.md)")
        if not isinstance(st.get("why"), str) or not st["why"].strip():
            errs.append(f"{where}: status.why is required (one plain sentence)")
        if st.get("groups") is not None:
            errs.append(f"{where}: status.groups moved to diseases/{d['folder']}/variants/ (see CONTRIBUTING.md)")
        variants = d.get("variants") or []
        vids = set()
        for v in variants:
            validate_variant(v, errs, f"{where}/variants/{v['_file']}.yaml")
            if v.get("id") in vids:
                errs.append(f"{where}: duplicate variant id '{v.get('id')}'")
            vids.add(v.get("id"))
        if rec.get("category") == "cancer" and _is_int(st.get("level"), 4) and not variants:
            errs.append(f"{where}: a cancer at level 4 or above needs variants rating each stage (see METHODOLOGY.md)")
        for item in rec.get("pipeline") or []:
            for vid in item.get("variants") or []:
                if vid not in vids:
                    errs.append(f"{where}: pipeline item '{item.get('name')}' names unknown variant '{vid}'")
            if item.get("effect") is not None and item["effect"] not in EFFECTS:
                errs.append(f"{where}: pipeline item '{item.get('name')}' effect must be big, some or small")
        tx = rec.get("treatment") or {}
        if tx.get("burden") is not None and tx["burden"] not in BURDENS:
            errs.append(f"{where}: treatment.burden must be light, moderate or heavy")
        toll = rec.get("toll") or {}
        for k in ("url", "ratio_url"):
            if toll.get(k) and not URL_RE.match(str(toll[k])):
                errs.append(f"{where}: toll.{k} must be an http(s) link")
        if toll.get("ratio") and not str(toll.get("ratio_caption") or "").strip():
            errs.append(f"{where}: toll.ratio needs a ratio_caption")
        fc = rec.get("forecast") or {}
        if fc.get("bottleneck") is not None and fc["bottleneck"] not in BOTTLENECKS:
            errs.append(f"{where}: forecast.bottleneck must be one of {sorted(BOTTLENECKS)}")
        level = st.get("level") if _is_int(st.get("level")) else 0
        if tracking == "active":
            if level >= 4:
                if not _is_int(fc.get("reached"), 1800, 2100):
                    errs.append(f"{where}: a level 4+ disease needs forecast.reached (the year it got there)")
                if tx.get("burden") == "light" and not _is_int(fc.get("reached_easy"), 1800, 2100):
                    errs.append(f"{where}: a level 4+ disease with light treatment needs forecast.reached_easy (the year the cure became mild)")
            else:
                validate_track("normal", fc.get("normal"), errs, where)
                validate_track("faster", fc.get("faster"), errs, where)
                n, f = fc.get("normal") or {}, fc.get("faster") or {}
                if all(_is_int(x.get(k)) for x in (n, f) for k in ("p2035", "p2045", "median")):
                    if f["p2035"] < n["p2035"] or f["p2045"] < n["p2045"]:
                        errs.append(f"{where}: the faster-pipeline odds can't be lower than normal pace")
                    if f["median"] > n["median"]:
                        errs.append(f"{where}: the faster-pipeline cure year can't be later than normal pace")
        for i, p in enumerate(rec.get("pipeline") or []):
            if not p.get("name"):
                errs.append(f"{where}: pipeline[{i}] needs a name")
            if p.get("url") and not URL_RE.match(str(p["url"])):
                errs.append(f"{where}: pipeline[{i}].url must be an http(s) link")
        for i, r in enumerate(rec.get("recent") or []):
            if r.get("url") and not URL_RE.match(str(r["url"])):
                errs.append(f"{where}: recent[{i}].url must be an http(s) link")
        ai = rec.get("ai") or {}
        if ai.get("impact") is not None and ai["impact"] not in AI_IMPACT:
            errs.append(f"{where}: ai.impact must be high, some or low")
        if research is not None and len(research["sources"]) < 2:
            errs.append(f"{where}: research.md needs at least 2 sources under '## Sources' as '- [Title](https://...)'")
    stage_ids = set()
    for s in data["stages"]:
        sid = s.get("id")
        where = f"pipeline/{sid}.yaml"
        stage_ids.add(sid)
        if s.get("status") not in STAGE_STATUS:
            errs.append(f"{where}: status must be blocking, easing or cleared")
        o = s.get("odds_much_faster") or {}
        for k in ("by_2030", "by_2035"):
            if not _is_int(o.get(k), 0, 100):
                errs.append(f"{where}: odds_much_faster.{k} must be 0-100")
        if s.get("kind") == "stage":
            for k in ("time_today", "time_best_case"):
                t = s.get(k) or {}
                if not (isinstance(t.get("low"), (int, float)) and isinstance(t.get("high"), (int, float)) and t["low"] <= t["high"]):
                    errs.append(f"{where}: {k} needs numeric low <= high (years)")
    disease_ids = {d["record"].get("id") for d in data["diseases"] if d["record"]}
    for c in data["checks"]:
        if c.get("disease") not in disease_ids:
            errs.append(f"tracker/checks.yaml: check '{c.get('id')}' points at unknown disease '{c.get('disease')}'")
        if not _is_int(c.get("prob"), 0, 100):
            errs.append(f"tracker/checks.yaml: check '{c.get('id')}' prob must be 0-100")
        if c.get("resolved") not in (None, "yes", "no", "void"):
            errs.append(f"tracker/checks.yaml: check '{c.get('id')}' resolved must be yes, no or void (void = not scored)")
    return errs


# ---------------------------------------------------------------- compile

def accel_index(stages) -> int | None:
    vals = [s["odds_much_faster"]["by_2030"] for s in stages if s.get("odds_much_faster")]
    return round(sum(vals) / len(vals)) if vals else None


def blend(n, f, idx):
    return round(n + (f - n) * idx / 100)


VARIANT_KEYS = ("id", "name", "what", "level", "burden", "burden_why", "survival", "share", "share_url", "caveat", "url", "forecast", "easy", "reached", "reached_easy")


def compile_variants(d: dict, data: dict) -> list[dict]:
    """Variants for the page: their own fields plus the catalysts and log entries tagged with their id."""
    rec = d["record"]
    out = []
    for v in d.get("variants") or []:
        x = {k: v[k] for k in VARIANT_KEYS if v.get(k) is not None}
        x["note"] = v.get("treatment")
        x["catalysts"] = [p for p in rec.get("pipeline") or [] if v.get("id") in (p.get("variants") or [])]
        x["events"] = [{"date": str(u["date"]), "text": f"{c['target']}: {c['from']} → {c['to']}. {c['why']}", "url": c.get("url")}
                       for u in data["updates"] for c in u.get("changes") or []
                       if c.get("disease") == rec.get("id") and c.get("variant") == v.get("id")]
        out.append(x)
    return out


def compile_site(data: dict) -> dict:
    stages = sorted(data["stages"], key=lambda s: s.get("order", 0))
    idx = accel_index(stages) or 0
    hist = data["history"]
    meta = dict(data["meta"])
    updated = str(meta.get("updated") or "")
    prev = next((h for h in hist if str(h.get("date")) < updated), None)
    prev_d = (prev or {}).get("diseases", {})
    prev_g = (prev or {}).get("gates", {})
    out_dz = []
    for i, d in enumerate(data["diseases"]):
        r = d["record"]
        st, tx, fc = r.get("status") or {}, r.get("treatment") or {}, r.get("forecast") or {}
        level = st.get("level", 0)
        n, f = fc.get("normal") or {}, fc.get("faster") or {}
        x = {
            "id": r["id"], "order": i + 1, "name": r["name"], "category": r["category"], "tracking": r.get("tracking", "proposed"),
            "short": r.get("summary"), "burden": (r.get("toll") or {}).get("text"), "burdenUrl": (r.get("toll") or {}).get("url"),
            "level": level, "levelWhy": st.get("why"), "groups": compile_variants(d, data), "reachedEasy": fc.get("reached_easy"),
            "ratio": {k: (r.get("toll") or {}).get(k) for k in ("ratio", "ratio_caption", "ratio_url")} if (r.get("toll") or {}).get("ratio") else None, "status": st.get("today"), "lastDeep": str(st["last_reviewed"]) if st.get("last_reviewed") else None,
            "bestTherapies": tx.get("best") or [], "txBurden": tx.get("burden"), "txBurdenNote": tx.get("burden_note"),
            "bottleneck": fc.get("bottleneck"), "accelNote": fc.get("faster_note"), "outlook": fc.get("outlook"), "interim": fc.get("milestones") or [],
            "pipeline": r.get("pipeline") or [], "breakthroughs": r.get("recent") or [], "nextMilestone": r.get("next_milestone"),
            "aiImpact": (r.get("ai") or {}).get("impact"), "aiNote": (r.get("ai") or {}).get("note"), "markets": r.get("markets") or [],
            "sources": [{"title": s["title"], "url": s["url"]} for s in (d["research"] or {}).get("sources", [])],
            "folder": f"diseases/{d['folder']}",
        }
        if level >= 4 and fc.get("reached"):
            x.update(p2035=100, p2045=100, timeline={"median": fc["reached"], "low": fc["reached"], "high": fc["reached"]})
        elif n and f:
            x.update(pNormal2035=n["p2035"], pNormal2045=n["p2045"], medianNormal=n["median"],
                     pAccel2035=f["p2035"], pAccel2045=f["p2045"], medianAccel=f["median"],
                     p2035=blend(n["p2035"], f["p2035"], idx), p2045=blend(n["p2045"], f["p2045"], idx),
                     timeline={k: blend(n[k], f[k], idx) for k in ("median", "low", "high")})
        p = prev_d.get(r["id"]) or {}
        x.update(prevP2035=p.get("p2035"), prevP2045=p.get("p2045"), prevMedian=p.get("median"), prevLevel=p.get("level"))
        # Estimate history for the chart: one point per weekly snapshot, plus today's if it isn't snapshotted yet.
        trend = [{"date": str(h["date"]), **{k: h["diseases"][r["id"]].get(k) for k in ("median", "low", "high", "level")}}
                 for h in reversed(hist) if r["id"] in (h.get("diseases") or {})]
        tl = x.get("timeline") or {}
        if level < 4 and tl.get("median") is not None and updated and all(t["date"] != updated for t in trend):
            trend.append({"date": updated, "median": tl["median"], "low": tl.get("low"), "high": tl.get("high"), "level": level})
        x["trend"] = trend if level < 4 else []
        # News that moved this disease: update changes and news items tagged with its id.
        events = []
        for u in data["updates"]:
            for c in u.get("changes") or []:
                if c.get("disease") == r["id"]:
                    events.append({"date": str(u["date"]), "text": f"{c['target']}: {c['from']} → {c['to']}. {c['why']}", "url": c.get("url")})
            for nw in u.get("news") or []:
                if isinstance(nw, dict) and nw.get("disease") == r["id"]:
                    events.append({"date": str(nw.get("date") or u["date"]), "text": nw.get("text"), "url": nw.get("url")})
        x["events"] = events
        out_dz.append(x)
    out_st = []
    for s in stages:
        o = s.get("odds_much_faster") or {}
        t, b = s.get("time_today") or {}, s.get("time_best_case") or {}
        out_st.append({
            "id": s["id"], "order": s.get("order"), "name": s["name"], "question": s.get("question"), "criterion": s.get("cleared_when"),
            "status": s.get("status"), "statusNote": s.get("status_note"), "pOpen2030": o.get("by_2030"), "pOpen2035": o.get("by_2035"),
            "prevPOpen2030": prev_g.get(s["id"]), "aiLinked": s.get("ai_linked"), "signals": s.get("signals") or [], "watch": s.get("watch"),
            "todayLow": t.get("low"), "todayHigh": t.get("high"), "todayLabel": t.get("label"), "todayNote": t.get("note"),
            "fastLow": b.get("low"), "fastHigh": b.get("high"), "fastLabel": b.get("label"), "fastNote": b.get("note"),
            "effectNote": s.get("effect_note"), "shortens": s.get("shortens"), "sources": s.get("sources") or [],
        })
    meta_out = {"updatedAt": updated, "week": meta.get("week"), "nextUpdate": str(meta.get("next_update") or ""),
                "headline": meta.get("headline"), "thisWeek": meta.get("this_week") or [], "scorecard": meta.get("scorecard") or [],
                "accelIndex": idx, "prevAccelIndex": (prev or {}).get("accelIndex"), "repo": meta.get("repo")}
    checks = [{"id": c["id"], "disease": c.get("disease"), "label": c.get("label"), "resolvesBy": str(c.get("resolves_by")),
               "prob": c.get("prob"), "resolved": c.get("resolved"), "lastForecast": c.get("last_forecast"), "note": c.get("note"), "url": c.get("url")}
              for c in data["checks"]]
    cal = [{"date": str(c["date"]), "event": c.get("event"), "url": c.get("url"), "disease": c.get("disease")} for c in data["calendar"]]
    return {"meta": meta_out, "categories": [{"id": c["id"], "name": c["name"], "order": i + 1} for i, c in enumerate(data["categories"])],
            "diseases": out_dz, "gates": out_st, "checks": checks, "calendar": cal, "updates": data["updates"][:3]}
