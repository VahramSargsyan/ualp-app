#!/usr/bin/env bash
set -euo pipefail
node tests/scoring_core.test.js
node tests/public_payload.test.js
node tests/selection_validation.test.js
