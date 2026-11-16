#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 src/benchmark.py --sizes 100 1000 5000 10000 --repeats 5 --out results/benchmark.csv
