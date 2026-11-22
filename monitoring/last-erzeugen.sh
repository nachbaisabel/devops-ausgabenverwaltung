#!/usr/bin/env bash
# Generate synthetic HTTP load against the Expenses API so that Prometheus has
# something to measure: a stream of successful requests plus a few deliberate
# 404s, so the request-rate and error-rate panels actually move.
#
# Usage:
#   ./last-erzeugen.sh                         # 200 iterations against localhost:8000
#   ./last-erzeugen.sh http://localhost:8000   # explicit base URL
#   ./last-erzeugen.sh http://localhost:8000 500   # base URL and iteration count
#
# Stop early with Ctrl+C.
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"
ITERATIONS="${2:-200}"

echo "Generating load against ${BASE_URL} for ${ITERATIONS} iterations..."

for i in $(seq 1 "${ITERATIONS}"); do
  # Normal traffic: list expenses, hit the liveness probe, create a expense.
  curl -s -o /dev/null "${BASE_URL}/api/expenses"
  curl -s -o /dev/null "${BASE_URL}/health"
  curl -s -o /dev/null -X POST \
    -H "Content-Type: application/json" \
    -d '{"title":"Load test expense","amount":"1.00","date":"2026-11-21","category":"Other"}' \
    "${BASE_URL}/api/expenses"

  # Every 5th iteration: request a expense id that does not exist -> 404 (client error).
  if (( i % 5 == 0 )); then
    curl -s -o /dev/null "${BASE_URL}/api/expenses/999999"
  fi

  # Every 10th iteration: hit an unknown route -> 404 (client error).
  if (( i % 10 == 0 )); then
    curl -s -o /dev/null "${BASE_URL}/does-not-exist"
  fi

  # Small pause so the load is spread over time instead of a single burst.
  sleep 0.1
done

echo "Done. Give Prometheus one or two scrape intervals (~15-30s) to catch up."
