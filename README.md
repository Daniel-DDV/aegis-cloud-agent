# Aegis — EU AI Act Governance Cloud Agent

**Multi-agent conformity assessment lab for public-sector AI**, built as a Cursor Cloud Agent showcase for Daniel Verloop (CiviQs / EU AI Alliance / NLAIC Publieke Diensten).

> Draft conformity assessment for demonstration — **not legal advice**.

## 60-second demo

```bash
./scripts/cloud-agent-install.sh   # once
# terminal A
cd apps/api && PYTHONPATH="../../packages:$PYTHONPATH" uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# terminal B
cd apps/dashboard && npm run dev -- --port 3000 --hostname 0.0.0.0
# terminal C
./scripts/demo-scan.sh
./scripts/demo-scan.sh --self
```

Open **http://127.0.0.1:3000** — five specialist agents run in parallel with live traces, then produce an audit-ready Markdown + JSON bundle under `reports/`.

## What it does

| Agent | EU AI Act focus |
| --- | --- |
| RiskClassifier | Art. 5 prohibited practices, Art. 6 / Annex III |
| DocumentationGap | Art. 11 technical docs, Art. 13 transparency, Art. 14 oversight |
| BiasAuditor | Art. 10 data governance & fairness |
| RedTeam | Art. 15 accuracy, robustness, cybersecurity |
| ReportGenerator | Conformity assessment draft (Markdown + JSON) |

The municipal sample (`samples/municipal-chatbot-stub`) is a **Mai-inspired** citizen-service chatbot with intentional gaps. Self-audit mode turns Aegis on itself — meta-governance you can show a client in five minutes.

## Cloud Agent environment

Configured via [`.cursor/environment.json`](.cursor/environment.json):

- `install` → [`scripts/cloud-agent-install.sh`](scripts/cloud-agent-install.sh) (idempotent)
- terminals: `aegis-api` (:8000) and `aegis-dashboard` (:3000)
- optional Dockerfile for Python 3.12 + Node 22

See [`docs/CLOUD_AGENT_PLAYBOOK.md`](docs/CLOUD_AGENT_PLAYBOOK.md).

## Tests

```bash
PYTHONPATH=packages:apps/api pytest -q
```

## API

- `GET /health`
- `POST /api/scans` — async scan
- `POST /api/scans/sync` — sync scan (demo script)
- `GET /api/scans`, `GET /api/scans/{id}`, `GET /api/scans/{id}/report.md`
- OpenAPI: http://127.0.0.1:8000/docs

## Built for

Daniel Verloop — AI specialist for the Dutch public sector, co-founder of [CiviQs](https://civiqs.nl), EU AI Alliance member.
