# signals-loop-lab

Companion repo for the DigitalOcean tutorial *Closing the Loop from Observability to Deployment*.

An order-support agent runs on DigitalOcean Harness Runtime. Its skill was written for
version 1 of an internal `orders` CLI; the CLI shipped 2.0.0 with a breaking change to
refund amounts (dollars became cents). The tutorial follows one loop end to end:

1. **Detect**: Signals (private preview) annotates production sessions and surfaces the
   corrections and failed tool calls in Insights.
2. **Reproduce**: the flagged sessions become a Simulation scenario set (Evaluations,
   public preview).
3. **Test**: the same scenarios score three agent configs: the stale baseline, a
   "be careful" prompt fix, and a contract fix written from the Signals evidence.
4. **Deploy and verify**: the winning config ships and Signals is re-read on fresh traffic.

## Layout

| Path | What it is |
|---|---|
| `orders-cli/orders` | The v2.0.0 CLI the agent calls. Single file, Python standard library. |
| `orders-cli/CHANGELOG.md` | The breaking change nobody propagated to the agent's skill. |
| `specs/support-v1.yaml` | Baseline environment spec, skill written for CLI v1. |
| `specs/support-v2-intuition.yaml` | v1 plus a generic "double-check your arguments" rule. |
| `specs/support-v3-evidence.yaml` | Contract fix; each rule maps to a signal in `evidence/`. |
| `scripts/mars.py` | Send turns to a session and stream its events. |
| `evidence/` | Raw transcripts, Signals exports, simulation results. |

The agent downloads only `orders-cli/orders`, pinned to the `orders-cli-v2.0.0` tag, so it
never sees the specs or evidence in this repo.

## Requirements

- `doctl` with Harness Runtime and `gradient` commands, authenticated to your team.
- A [model access key](https://docs.digitalocean.com/products/inference/how-to/manage-model-access-keys/)
  exported as `HARNESS_INFERENCE_API_KEY`.
- Signals enabled on the config (private preview; ask your account team for access).
