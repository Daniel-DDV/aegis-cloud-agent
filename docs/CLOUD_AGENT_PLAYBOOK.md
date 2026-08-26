# Cloud Agent Playbook — Aegis

How a Cursor Cloud Agent should operate this repository.

## Boot checklist

1. Confirm `./scripts/cloud-agent-install.sh` has been applied (deps present).
2. Ensure terminals `aegis-api` and `aegis-dashboard` are up (or start them).
3. Hit `GET http://127.0.0.1:8000/health` and open `http://127.0.0.1:3000`.
4. Run `./scripts/demo-scan.sh` then `./scripts/demo-scan.sh --self`.
5. Read the generated report under `reports/<scan-id>/report.md`.

## Parallel work pattern

When extending agents or rubrics:

1. Update `packages/rubric` signals / scorers.
2. Add a fixture in `packages/eval/fixtures.json`.
3. Run `pytest -q`.
4. Re-run the municipal + self-audit demos.
5. Commit with a clear message; push; subscribe to CI if available.

## Event-driven loop (optional)

On PRs that touch `apps/api/agents/` or `packages/rubric/`:

1. Subscribe to GitHub PR / CI events for this repo.
2. On wake, re-run `pytest -q` and `./scripts/demo-scan.sh`.
3. Summarize risk-tier deltas in the PR conversation.
4. Never claim legal compliance — always include the demonstration disclaimer.

## Secrets

- No secrets required for the core deterministic demo.
- Optional: `OPENAI_API_KEY` for future LLM-backed agent modes (not used by default).
- Never bake secrets into `environment.json`, Dockerfiles, or reports.
