# demo-payment-service

A small FastAPI payment service, fully instrumented with OpenTelemetry, used as
the target application for [incident-triage-agent](https://github.com/gautamamber/incident-triage-agent).
It exists to be broken on purpose — each bug scenario is a real git commit or
config change the agent has to detect and diagnose.

## What it does

- `POST /payments` — creates a payment, calls the `fraud-mock` dependency for approval
- `GET /payments/{id}` — looks up one payment
- `GET /customers/{id}/payments` — lists a customer's payments
- `POST /payments/{id}/refund` — refunds a payment
- `GET /health` — health check

All requests, DB queries, and outbound calls emit OpenTelemetry traces/logs/metrics
to a local OTel Collector (see the agent repo's `docker-compose.yml`).

## Structure

```
app/
├── main.py           # FastAPI app, telemetry wiring, global exception handler
├── api/payments.py    # the 4 endpoints
├── db.py               # SQLAlchemy models + engine
├── config.py            # settings
└── telemetry.py           # OpenTelemetry SDK setup
fraud_mock/main.py    # tiny dependency service, configurable latency/failure rate
scripts/seed.py         # bulk-seeds rows for the missing-index scenario
```

## Running it

Not run standalone — started as part of the agent repo's Docker Compose stack.
See that repo's README for setup.

## Bug scenarios

Known bugs live as separate git branches (`bug/S01-...`, `bug/S03-...`) or as
saved patches in the agent repo's `eval/patches/`, applied on demand by the
evaluation harness. `main` is always the clean, correct version.
