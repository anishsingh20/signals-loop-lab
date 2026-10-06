# signals-loop-lab

Companion repo for the DigitalOcean tutorial *Closing the Loop from Observability to
Deployment: Fix an AI Agent with Signals and Evaluations*.

An order-support agent runs on DigitalOcean Harness Runtime. Its skill was written for
version 1 of an internal `orders` CLI. The CLI shipped 2.0.0 with breaking changes, the
worst of which is silent: `--amount` became integer cents, so `--amount 40` refunds
$0.40 and exits 0. The tutorial follows one loop end to end:

1. **Enable**: Signals (private preview) on the production agent config.
2. **Detect**: Signals Insights flags 6 of 6 production sessions (24 Invalid Args,
   7 Parameter Drift, 1 Bad Query). Session Insights shows nothing wrong.
3. **Troubleshoot**: the Signals session trace shows `--amount 40` next to a teammate
   saying "her bank shows $0.40".
4. **Test**: the flagged sessions become a Simulation scenario set (Evaluations,
   public preview) that scores three configs.
5. **Deploy**: the passing spec ships as a new config with the same content hash.
6. **Verify**: the same six requests replayed in production, and Signals re-read.

## Results (6 October 2026)

| | v1 (stale skill) | v2 ("be careful" prompt) | v3 (contract fix from Signals) |
|---|---|---|---|
| Simulation journeys, money correct (ledger) | 6 of 12 | 6 of 12 | **12 of 12** |
| Simulation failed `orders` CLI calls | 44 | 46 | **0** |
| Console average pass rate (3 judge metrics) | 78% | 85% | 100% |
| Production failed tool calls (6 sessions) | 25 of 58 | not deployed | **0 of 38** |
| Production refunds right the first time | 2 of 5 | not deployed | **5 of 5** |
| Signals execution-layer labels (production) | 32 (24 Invalid Args, 7 Parameter Drift, 1 Bad Query) | not deployed | **0** on 18 analysed turns |

Signals did not label the three teammate corrections on v1, and labelled none of the six
thank-yous or six duplicate requests on v3. Its execution layer matched the raw logs one for
one; read sentiment from the traces yourself.

The judge's average put the "be careful" prompt ahead of the baseline while it still
paid cents on every round-dollar refund. Gate releases on the metric written from the
observed failure, and check it against your system of record (here, the sandbox ledger).

## Signal to fix

| What Signals showed | Root cause in CLI 2.0.0 | Rule in `support-v3-evidence.yaml` |
|---|---|---|
| Invalid Args: `unknown command 'lookup'` | `lookup` renamed to `get` | Use `orders get --order-id`, never `lookup` |
| Invalid Args: `arguments are required: --order-id` | positional id became a flag | Always pass `--order-id` |
| Invalid Args: `order id must look like ORD-#####` | ids gained a prefix | Prefix bare numbers with `ORD-` |
| Invalid Args: `arguments are required: --reason` | `--reason` became required | The five values and how to map words to them |
| Invalid Args: `amount must be a whole number of cents` | `--amount` became cents | "`--amount` is CENTS. $40 is 4000." |
| Silent: `amount=40` accepted, teammate says "$0.40" | same, with no error | Read `refunded:` back before replying; refund only the difference |
| Parameter Drift (7) | the four errors above, retried | Fixed by the rules above |

## Layout

| Path | What it is |
|---|---|
| `orders-cli/orders` | The v2.0.0 CLI the agent calls. Single file, Python standard library. |
| `orders-cli/CHANGELOG.md` | The breaking change nobody propagated to the agent's skill. |
| `specs/support-v1.yaml` | Baseline environment spec, skill written for CLI v1. |
| `specs/support-v2-intuition.yaml` | v1 plus a generic "double-check your arguments" rule. |
| `specs/support-v3-evidence.yaml` | Contract fix; each rule maps to a signal in `evidence/`. |
| `scenarios/refund-regressions.jsonl` | 6 Simulation scenarios rebuilt from the flagged sessions. |
| `scripts/mars.py` | Send a turn to a session and stream its events. |
| `scripts/replay.py` | Send one turn to every session in parallel (foreground, one log per session). |
| `scripts/traffic.tsv` | The six first-turn requests. |
| `scripts/traffic-v1-followup.tsv`, `traffic-v3-followup.tsv` | Teammate replies written from the true ledger. |
| `scripts/sim_report.py` | Pulls simulation trajectories and scores each journey against the CLI's refund output. |
| `evidence/prod-v1/`, `evidence/prod-v3/` | Turn logs, session history, and the ledger read with `exec`. |
| `evidence/signals/` | Signals annotations per session (labels, confidence, snippet, step). |
| `evidence/sim/` | Simulation runs, per-journey trajectories, and `report.md`. |

The agent downloads only `orders-cli/orders`, pinned to the `orders-cli-v2.0.0` tag, so it
never sees the specs or evidence in this repo.

## Requirements

- `doctl` with the `harness-runtime` and `gradient` commands, authenticated to your team.
- A [model access key](https://docs.digitalocean.com/products/inference/how-to/manage-model-access-keys/)
  exported as `HARNESS_INFERENCE_API_KEY`. Never commit it.
- Signals enabled on the production config (private preview; ask your account team).
- Python 3.10+, standard library only.

## Reproduce

```bash
# 1. Baseline config and six production sessions
doctl harness-runtime config create --spec specs/support-v1.yaml --name order-support-v1 -o json
CFG=<config-id>
for i in 1 2 3 4 5 6; do doctl harness-runtime config start-session $CFG --name prod-0$i; done

# 2. Enable Signals on order-support-v1 in the console (Signals > Configuration), then:
python3 scripts/replay.py --prefix prod- --turn 1 --out evidence/prod-v1
python3 scripts/replay.py --prefix prod- --turn 2 --out evidence/prod-v1 \
  --messages scripts/traffic-v1-followup.tsv
doctl harness-runtime exec prod-01 -- cat /workspace/.orders/refunds.jsonl

# 3. About an hour later, read Signals > Insights for order-support-v1.

# 4. Scenario set and one simulation run per candidate config
doctl gradient scenario-set create --name refund-regressions --file scenarios/refund-regressions.jsonl -o json
doctl harness-runtime config create --spec specs/support-v3-evidence.yaml --name order-support-v3-eval -o json
doctl gradient simulation-run create --name v3-contract-fix \
  --scenario-set-uuid <set> --agent-uuid <v3-eval-config> --agent-name order-support-v3-eval \
  --judge-model-uuid <judge> --metric-uuids <m1,m2,m3> --exploration-budget 2 --max-turns 3
python3 scripts/sim_report.py v1=<run> v2=<run> v3=<run> --out evidence/sim/round2

# 5. Deploy the passing spec, check the content hash matches the eval config, verify
doctl harness-runtime config create --spec specs/support-v3-evidence.yaml --name order-support-v3 -o json
for i in 1 2 3 4 5 6; do doctl harness-runtime config start-session <v3-config> --name prod-v3-0$i; done
python3 scripts/replay.py --prefix prod-v3- --turn 1 --out evidence/prod-v3
python3 scripts/replay.py --prefix prod-v3- --turn 2 --out evidence/prod-v3 \
  --messages scripts/traffic-v3-followup.tsv
```

In the published run, turn 1 on v3 was sent twice by mistake (see the tutorial). The
duplicate is kept in `evidence/prod-v3/*.turn1-duplicate.log`, and the follow-up was
sent as turn 3.

## Preview status (6 October 2026)

- **Signals**: private preview, opt-in per agent config with a consent dialog. Not in the
  public docs yet. Annotations appeared about an hour after traffic.
- **Evaluations Simulation**: labelled public preview in the console.
- **Managed Agents (Harness Runtime)**: public preview.
- **Insights**: public preview.

## Clean up

```bash
doctl harness-runtime remove prod-01   # repeat per session
doctl harness-runtime config delete <config-id>
```

Disable Signals on configs you no longer watch, and revoke the model access key you
created for the lab.

## License

MIT
