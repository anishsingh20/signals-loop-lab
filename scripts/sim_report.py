#!/usr/bin/env python3
"""Score Simulation runs against ground truth taken from the orders CLI itself.

The judge reads the conversation. This script reads what the CLI printed: every
`refund queued: RF-0001 order=ORD-48213 amount=40 reason=damaged` line in a
journey's tool outputs is a write that happened. It sums them per order and
compares with the cents the scenario asked for.

Usage:
  python3 scripts/sim_report.py <label>=<run-uuid> [<label>=<run-uuid> ...] [--out evidence/sim]

Needs doctl authenticated to the team that owns the runs (DOCTL_CONTEXT or the
current context).
"""
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Expected outcome per scenario name prefix: order -> cents. Empty dict = no refund.
EXPECTED = {
    "Whole-dollar refund": {"ORD-48213": 4000},
    "Goodwill refund": {"ORD-50415": 2500},
    "Full refund on an order": {"ORD-49388": 3600},
    "Partial refund with cents": {"ORD-50520": 1250},
    "Order status lookup": {},
    "Customer reports the refund was wrong": {"ORD-48213": 4000},
}
QUEUED = re.compile(r"refund queued: (RF-\d+) order=(ORD-\d{5}) amount=(\d+)")


def doctl(*args):
    ctx = os.environ.get("DOCTL_CONTEXT")
    cmd = ["doctl", *args, "-o", "json"] + (["--context", ctx] if ctx else [])
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def tool_calls(msg):
    raw = msg.get("tool_calls")
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return ast.literal_eval(raw)


def expected_for(name):
    for prefix, exp in EXPECTED.items():
        if name.startswith(prefix):
            return exp
    return None


def score_journey(traj):
    refunds = defaultdict(int)
    failed_calls = 0
    calls = 0
    for m in traj.get("messages", []):
        for c in tool_calls(m):
            if c.get("name") != "Bash":
                continue
            cmd = str((c.get("input_parameters") or {}).get("command", ""))
            if "/orders" not in cmd:
                continue
            calls += 1
            out = str(c.get("output", ""))
            if out.startswith("Exit code") or "error:" in out:
                failed_calls += 1
            for _rf, order, cents in QUEUED.findall(out):
                refunds[order] += int(cents)
    metrics = {
        e["metric_name"]: e.get("number_value")
        for e in traj.get("evaluation_metrics", [])
    }
    return dict(refunds), calls, failed_calls, metrics


def main(argv):
    out_dir = Path("evidence/sim")
    if "--out" in argv:
        i = argv.index("--out")
        out_dir = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2 :]
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for spec in argv:
        label, run_uuid = spec.split("=", 1)
        run = doctl("gradient", "simulation-run", "get", run_uuid)["simulation_run"]
        names = {
            s["scenario_uuid"]: s["name"]
            for s in doctl("gradient", "scenario-set", "list-scenarios", run["scenario_set_uuid"])
        }
        journeys = doctl("gradient", "simulation-run", "list-journeys", run_uuid)
        journeys = journeys if isinstance(journeys, list) else journeys.get("journeys", [])
        for j in journeys:
            traj = doctl("gradient", "simulation-run", "get-trajectory", run_uuid, j["journey_uuid"])
            (out_dir / f"{label}-{j['journey_uuid']}.json").write_text(json.dumps(traj, indent=1))
            name = names.get(j["scenario_uuid"], j["scenario_uuid"])
            refunds, calls, failed, metrics = score_journey(traj)
            exp = expected_for(name)
            correct = exp is not None and refunds == exp
            rows.append({
                "config": label,
                "scenario": name,
                "journey": j["journey_uuid"],
                "refunded_cents": refunds,
                "expected_cents": exp,
                "money_correct": correct,
                "cli_calls": calls,
                "failed_cli_calls": failed,
                "turns": traj.get("turn_count"),
                **{f"m:{k}": v for k, v in metrics.items()},
            })
    (out_dir / "report.json").write_text(json.dumps(rows, indent=1))

    by_cfg = defaultdict(list)
    for r in rows:
        by_cfg[r["config"]].append(r)
    print("| Config | Scenario | Refunded (cents) | Expected | Money right | CLI calls (failed) | Guardrail | Tool use | Goal |")
    print("|---|---|---|---|---|---|---|---|---|")
    for cfg, rs in by_cfg.items():
        for r in sorted(rs, key=lambda r: r["scenario"]):
            print(f"| {cfg} | {r['scenario']} | {r['refunded_cents'] or '-'} | {r['expected_cents'] or '-'} | "
                  f"{'yes' if r['money_correct'] else 'NO'} | {r['cli_calls']} ({r['failed_cli_calls']}) | "
                  f"{r.get('m:Guardrail validation')} | {r.get('m:Tool Use Accuracy')} | {r.get('m:User goal completion')} |")
    print()
    for cfg, rs in by_cfg.items():
        n = len(rs)
        ok = sum(r["money_correct"] for r in rs)
        calls = sum(r["cli_calls"] for r in rs)
        failed = sum(r["failed_cli_calls"] for r in rs)
        avg = lambda k: round(sum((r.get(k) or 0) for r in rs) / n, 2)
        print(f"{cfg}: money right {ok}/{n}, failed CLI calls {failed}/{calls}, "
              f"guardrail {avg('m:Guardrail validation')}, tool use {avg('m:Tool Use Accuracy')}, "
              f"goal {avg('m:User goal completion')}")


if __name__ == "__main__":
    main(sys.argv[1:])
