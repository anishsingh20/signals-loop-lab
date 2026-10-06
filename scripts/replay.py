#!/usr/bin/env python3
"""Replay one turn of the traffic file against a set of sessions, in parallel.

    python3 scripts/replay.py --prefix prod-v3- --turn 1 --out evidence/prod-v3
    python3 scripts/replay.py --prefix prod-v3- --turn 2 --out evidence/prod-v3 --messages turn2.tsv

Turn 1 reads `first_turn` from scripts/traffic.tsv. Later turns read a
two-column TSV (session, text) given with --messages. Session names are the
traffic names with `prod-` replaced by --prefix, so prod-01 becomes prod-v3-01.
Each send is `scripts/mars.py send`, logged to <out>/<session>.turn<N>.log.
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(path: Path) -> list[tuple[str, str]]:
    with path.open() as fh:
        reader = csv.reader(fh, delimiter="\t")
        next(reader)
        return [(r[0], r[1]) for r in reader if len(r) >= 2]


def send(session: str, text: str, log: Path, wait: int) -> tuple[str, int]:
    with log.open("w") as fh:
        proc = subprocess.run(
            [sys.executable, "-u", str(HERE / "mars.py"), "send", session, text, "--wait", str(wait)],
            stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=os.environ.copy(),
        )
    return session, proc.returncode


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--turn", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--messages", type=Path, default=HERE / "traffic.tsv")
    ap.add_argument("--wait", type=int, default=480)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name, text in rows(args.messages):
        session = name.replace("prod-", args.prefix, 1) if not name.startswith(args.prefix) else name
        jobs.append((session, text, out / f"{session}.turn{args.turn}.log"))

    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        for session, code in pool.map(lambda j: send(*j, args.wait), jobs):
            print(f"{session}: exit {code}", flush=True)


if __name__ == "__main__":
    main()
