#!/bin/bash

# Navigate to script directory
cd "$(dirname "$0")"

# Export environment variables from .env (filter out comments and empty lines)
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Set GCP credentials path
export GOOGLE_APPLICATION_CREDENTIALS="../../gcp-credentials.json"

# Run the generation script
python3 generate_metrics_test_deck.py
