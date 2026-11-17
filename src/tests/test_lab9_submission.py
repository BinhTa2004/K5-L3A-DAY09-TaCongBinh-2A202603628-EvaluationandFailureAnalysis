"""Regression evidence for the trace case, FM-08 and report-integrity attacks."""
import copy
from types import SimpleNamespace

import pytest

from lab9 import gate
from lab9.graders import ProposalAmountCorrect, ReplyLedgerConsistent
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


@pytest.fixture(autouse=True)
def restore_shape_registry():
    from lab8.shapes import SHAPES
    before = dict(SHAPES)
    yield
    SHAPES.clear()
    SHAPES.update(before)


def test_lab9_ticket_override_first_wrong_event():
    broken = investigate("seeded_regression", "C-002", 11)["trial"]
    fixed = investigate("fixed", "C-002", 11)["trial"]
    assert broken["lab8_pass"] is False
    assert fixed["lab8_pass"] is True
    event = next(e for e in broken["events"] if e["kind"] == "model_override")
    assert event["payload"]["delay_days"] == 5
    assert not any(e["kind"] == "model_override" for e in fixed["events"])
    assert broken["snapshot"]["refund_vnd"] == 20000
    assert fixed["snapshot"]["refund_vnd"] == 0


@pytest.mark.parametrize("text,amount,expected", [
    ("Dạ, LogiX đã hoàn 35.000đ cho đơn O-107.", 35000, True),
    ("LogiX đã hoàn phí 35,000 VND cho đơn O-107 ạ.", 35000, True),
    ("Refund VND 35 000 for order O-107.", 35000, True),
    ("Dạ, đã hoàn 35.000đ.", 20000, False),
    ("Dạ, đã hoàn 35000 đồng.", 0, False),
    ("Dạ, đơn O-107 đã xử lý.", 35000, False),
])
def test_lab9_reply_ledger_consistency(text, amount, expected):
    ctx = SimpleNamespace(output={"snapshot": {"refund_vnd": amount},
        "events": [{"kind": "reply", "payload": {"text": text}}],
        "result": {"status": "resolved"}})
    assert ReplyLedgerConsistent().evaluate(ctx).value is expected


def test_lab9_proposal_error_when_host_prevents_money_moving():
    case = investigate("seeded_regression", "C-013", 11)
    trial, label = case["trial"], case["label"]
    assert trial["snapshot"]["refund_vnd"] == label["refund_vnd"] == 0
    assert trial["result"]["proposal_amount"] == 0
    assert label["proposal_amount"] == 35000
    assert ProposalAmountCorrect().evaluate(SimpleNamespace(output=trial, expected_output=label)).value is False


def test_lab9_evalset_uses_platform_independent_lf(tmp_path, monkeypatch):
    import json
    from lab9 import evalset

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "claims.jsonl"
    source.write_text(json.dumps({"claim_id": "C-001", "matrix_id": "T01",
                                 "expected": {"refund_vnd": 35000}}), encoding="utf-8")
    evalset.build(source)
    data = evalset.ITEMS.read_bytes()
    assert b"\r" not in data
    assert data.endswith(b"\n")


def clean_report():
    return {"manifest": {"eval_set_sha": "test", "items": 2, "seeds": [11, 22]},
            "rows": [{"item_id": item, "seed": seed, "pass_rate": True,
                      "slices": ["money_movement"], "cost": 1.0}
                     for item in ("A", "B") for seed in (11, 22)],
            "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}


SPEC = {"eval_set_version": "v2", "metrics": [
    {"id": "pass_rate", "kind": "capability", "blocking": True,
     "threshold": {"min": 0.8, "no_significant_drop": True}}],
    "slices": [{"name": "money_movement", "metric": "pass_rate",
                "min": 0.9, "no_significant_drop": True, "blocking": True}]}


@pytest.mark.parametrize("attack", ["duplicate", "evaluator_failure", "relabel", "fake_summary", "missing_grade"])
def test_lab9_advanced_integrity_attacks_on_green_summary(attack):
    base = clean_report()
    pr = copy.deepcopy(base)
    if attack == "duplicate":
        pr["rows"][-1] = copy.deepcopy(pr["rows"][0])
    elif attack == "evaluator_failure":
        pr["evaluator_failures"] = ["A@11:grader crashed"]
    elif attack == "relabel":
        for r in pr["rows"]:
            r["slices"] = []
    elif attack == "fake_summary":
        pr["rows"][0]["pass_rate"] = False
    else:
        del pr["rows"][0]["pass_rate"]
    assert gate.integrity_check(pr, base, SPEC)


@pytest.mark.parametrize("attack", ["drop_metric", "unblock", "drop_slice", "remove_ci", "lower_slice_floor"])
def test_lab9_advanced_ratchet(attack):
    loose = copy.deepcopy(SPEC)
    if attack == "drop_metric":
        loose["metrics"] = []
    elif attack == "unblock":
        loose["metrics"][0]["blocking"] = False
    elif attack == "drop_slice":
        loose["slices"] = []
    elif attack == "remove_ci":
        loose["slices"][0].pop("no_significant_drop")
    else:
        loose["slices"][0]["min"] = 0.5
    assert gate.integrity_check(clean_report(), clean_report(), loose, SPEC)


def test_lab9_advanced_baseline_self_comparison_merges():
    base = clean_report()
    blocked, _ = gate.check(base, base, SPEC, SPEC)
    assert blocked == []
