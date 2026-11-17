"""CI gate: compare a PR eval report with the main-branch baseline using the metric spec.

    python -m lab9.gate --pr reports/eval_workflow.json --baseline reports/baseline_v1.json

exit 0 = merge, exit 1 = blocked. Safety metrics: max 0, no averaging away.
Capability metrics: meet the floor AND the paired CI of (PR - main) is not entirely below 0.
Thresholds may only get stricter on the same eval-set version (ratchet).
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import stats
from lab9.eval import SPEC, aggregate, load_spec, per_item
from lab9.graders import GRADERS


def integrity_check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> list[str]:
    """M7 (Expert): refuse to compare reports that cannot be trusted. Return a list of problems
    (empty = trustworthy). A gate that passes a broken report is worse than no gate.
    Must catch at least:
      - any metric value in pr["metrics"] that is NaN or inf
      - len(pr["rows"]) != manifest items x len(manifest seeds)   (dropped / duplicated rows)
      - the (item_id, seed) set of PR differs from the baseline's (cherry-picked seeds/items)
      - pr["evaluator_failures"] non-empty, or a row whose value for a graded spec metric is
        None (a crashed grader silently scores as "missing" and drops out of the mean)
      - base_spec given and a threshold in spec is LOOSER than in base_spec for the same
        eval-set version (ratchet: max may not rise, min may not fall, a blocking metric may
        not become non-blocking, a metric may not disappear; the same for spec["slices"],
        including dropping no_significant_drop)
      - an item's slice tags in PR rows differ from the baseline's (relabelling an item out of a
        slice hides its regression from the slice gate)"""
    problems = []
    graded = {m["id"] for m in spec["metrics"]
              if m["id"] in GRADERS or any(m["id"] in r for r in base.get("rows", []))}
    indices = []
    for name, report in (("PR", pr), ("baseline", base)):
        manifest, rows = report.get("manifest", {}), report.get("rows", [])
        seeds, items = manifest.get("seeds", []), manifest.get("items", 0)
        if not seeds or len(set(seeds)) != len(seeds) or items < 1:
            problems.append(f"{name}: invalid items/seeds manifest")
        if len(rows) != items * len(seeds):
            problems.append(f"{name}: row count differs from items x seeds")
        if report.get("evaluator_failures"):
            problems.append(f"{name}: evaluator_failures is non-empty")
        keys = [(r.get("item_id"), r.get("seed")) for r in rows]
        if any(n != 1 for n in Counter(keys).values()):
            problems.append(f"{name}: duplicate item/seed rows")
        item_ids = {k[0] for k in keys}
        expected = {(i, s) for i in item_ids for s in seeds}
        if len(item_ids) != items or set(keys) != expected:
            problems.append(f"{name}: incomplete item/seed grid")
        if "seeds" in spec and set(seeds) != set(spec["seeds"]):
            problems.append(f"{name}: seeds differ from spec")
        if any(not isinstance(v, (int, float)) or not math.isfinite(v)
               for v in report.get("metrics", {}).values()):
            problems.append(f"{name}: non-finite or missing aggregate metric")
        for m in spec["metrics"]:
            if m["id"] not in report.get("metrics", {}):
                problems.append(f"{name}: missing aggregate {m['id']}")
        valid_rows = True
        tags_by_item = {}
        for row in rows:
            for mid in graded:
                v = row.get(mid)
                if not isinstance(v, (bool, int, float)) or not math.isfinite(v) or v not in (0, 1):
                    problems.append(f"{name}: missing/invalid row metric {mid}")
                    valid_rows = False
            tags = row.get("slices", [])
            if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags) or len(set(tags)) != len(tags):
                problems.append(f"{name}: invalid slice tags")
                valid_rows = False
                continue
            item = row.get("item_id")
            if item in tags_by_item and tags_by_item[item] != set(tags):
                problems.append(f"{name}: slice tags vary across seeds")
            tags_by_item[item] = set(tags)
            if "cost" in row and (not isinstance(row["cost"], (int, float)) or
                                  not math.isfinite(row["cost"]) or row["cost"] < 0):
                problems.append(f"{name}: invalid cost")
                valid_rows = False
        if rows and valid_rows:
            # Do not trust a green summary if the underlying trials disagree.
            normalized = [{**r, "cost": r.get("cost", 0.0)} for r in rows]
            recomputed = aggregate(normalized, sorted(graded), k_values=spec.get("pass_k", []))
            for mid, value in report.get("metrics", {}).items():
                if mid in recomputed:
                    actual = recomputed[mid]
                    if actual is None or not isinstance(value, (int, float)) or not math.isfinite(value) or abs(value - actual) > 0.00011:
                        problems.append(f"{name}: aggregate {mid} disagrees with rows")
        indices.append({k: set(r.get("slices") or []) for k, r in zip(keys, rows)
                        if isinstance(r.get("slices", []), list) and
                        all(isinstance(t, str) for t in r.get("slices", []))})
    if indices[0].keys() != indices[1].keys():
        problems.append("PR item/seed set differs from baseline")
    elif indices[0] != indices[1]:
        problems.append("PR slice tags differ from baseline")
    if pr.get("manifest", {}).get("items") != base.get("manifest", {}).get("items"):
        problems.append("PR item count differs from baseline")
    if base_spec and spec.get("eval_set_version") == base_spec.get("eval_set_version"):
        for section, key in (("metrics", "id"), ("slices", "name")):
            current = {m[key]: m for m in spec.get(section, [])}
            if len(current) != len(spec.get(section, [])):
                problems.append(f"ratchet: duplicate {section}")
            for old in base_spec.get(section, []):
                new = current.get(old[key])
                if new is None:
                    problems.append(f"ratchet: removed {section} {old[key]}")
                    continue
                if old.get("blocking") and not new.get("blocking"):
                    problems.append(f"ratchet: disabled blocking {old[key]}")
                if section == "metrics":
                    before, after = old.get("threshold", {}), new.get("threshold", {})
                    for field in ("kind", "level", "grader"):
                        if field in old and old[field] != new.get(field):
                            problems.append(f"ratchet: changed {field} of {old[key]}")
                else:
                    before, after = old, new
                    if old.get("metric") != new.get("metric"):
                        problems.append(f"ratchet: changed slice metric {old[key]}")
                for bound in ("min", "max", "max_increase"):
                    if bound in before and (bound not in after or
                            (after[bound] < before[bound] if bound == "min" else after[bound] > before[bound])):
                        problems.append(f"ratchet: loosened {bound} of {old[key]}")
                if before.get("no_significant_drop") and not after.get("no_significant_drop"):
                    problems.append(f"ratchet: removed no_significant_drop from {old[key]}")
        for field in ("eval_set", "labels", "seeds", "pass_k", "adversarial_pack", "bootstrap"):
            if field in base_spec and spec.get(field) != base_spec[field]:
                problems.append(f"ratchet: changed evaluation protocol {field}")
    return list(dict.fromkeys(problems))


def slice_check(pr: dict, base: dict, spec: dict) -> tuple[list[str], list[str]]:
    """M5 (Advanced): an average can hide a regression on a small, important slice.
    For each entry of spec["slices"] ({"name", "metric", "min"?, "no_significant_drop"?, "blocking"}):
      - value = mean of per_item(pr, metric, slice_name=name)
      - fail if below "min", or if no_significant_drop and the paired CI over the slice's items
        lies entirely below 0
    Return (blocked ids like "slice:money_movement/pass_rate", report lines)."""
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for entry in spec.get("slices", []):
        name, mid = entry["name"], entry["metric"]
        sid = f"slice:{name}/{mid}"
        a, b = per_item(pr, mid, name), per_item(base, mid, name)
        note = ""
        failed = not a or a.keys() != b.keys()
        value = sum(a.values()) / len(a) if a else None
        if value is not None:
            failed |= "min" in entry and value < entry["min"]
            failed |= "max" in entry and value > entry["max"]
        if a and a.keys() == b.keys() and entry.get("no_significant_drop"):
            keys = sorted(a)
            delta, lo, hi = stats.paired_bootstrap(
                [a[k] for k in keys], [b[k] for k in keys],
                n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                confidence=bs.get("confidence", 0.95))
            note = f"Δ {delta:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            failed |= hi < 0
        if failed and entry.get("blocking"):
            blocked.append(sid)
        verdict = "BLOCK" if failed and entry.get("blocking") else "warn" if failed else "ok"
        lines.append(f"  {sid:<40} {value!s:<10} {note} {verdict}")
    return blocked, lines


def check(pr: dict, base: dict, spec: dict, base_spec: dict | None = None) -> tuple[list[str], list[str]]:
    if pr["manifest"]["eval_set_sha"] != base["manifest"]["eval_set_sha"]:
        return ["eval_set_sha"], ["  EVAL SET differs from the baseline's: re-run the baseline on the same eval set"]
    problems = integrity_check(pr, base, spec, base_spec)
    if problems:
        return ["integrity"], [f"  INTEGRITY {p}" for p in problems]
    blocked, lines = [], []
    bs = spec.get("bootstrap", {})
    for m in spec["metrics"]:
        mid, th, val = m["id"], m.get("threshold", {}), pr["metrics"].get(m["id"])
        verdict, note = "ok", ""
        if val is None:
            verdict = "missing"
        elif "max" in th and val > th["max"]:
            verdict = "fail"
        elif "min" in th and val < th["min"]:
            verdict = "fail"
        elif "max_increase" in th and base["metrics"].get(mid):
            if val > base["metrics"][mid] * (1 + th["max_increase"]):
                verdict = "fail"
        if th.get("no_significant_drop") and val is not None:
            a, b = per_item(pr, mid), per_item(base, mid)
            keys = sorted(set(a) & set(b))
            d, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                               n_resamples=bs.get("n_resamples", 1000), rng=bs.get("rng", 2027),
                                               confidence=bs.get("confidence", 0.95))
            note = f"Δ {d:+.3f} CI [{lo:+.3f}, {hi:+.3f}]"
            if hi < 0:
                verdict = "fail"
        if verdict != "ok" and m.get("blocking"):
            blocked.append(mid)
        label = {"ok": "ok", "missing": "MISSING"}.get(verdict, "BLOCK" if m.get("blocking") else "warn")
        lines.append(f"  {mid:<22} {val!s:<8} {json.dumps(th):<40} {note:<28} {label}")
    if spec.get("slices"):
        sb, sl = slice_check(pr, base, spec)
        blocked += sb
        lines += sl
    return blocked, lines


def main(argv: list[str] | None = None) -> int:
    utf8_stdio()
    ap = argparse.ArgumentParser(prog="lab9.gate")
    ap.add_argument("--pr", required=True)
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--spec", default=str(SPEC))
    ap.add_argument("--base-spec", help="metric spec on main, for the ratchet check (M7)")
    args = ap.parse_args(argv)
    pr = json.loads(Path(args.pr).read_text(encoding="utf-8"))
    base = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    base_spec = load_spec(Path(args.base_spec)) if args.base_spec else None
    blocked, lines = check(pr, base, load_spec(Path(args.spec)), base_spec)
    print(f"gate: PR {pr['run_id']} vs main {base['run_id']} · eval set {pr['manifest']['eval_set_sha']}")
    print("\n".join(lines))
    if blocked:
        print(f"exit 1 — blocked: {', '.join(blocked)}")
        return 1
    print("exit 0 — merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
