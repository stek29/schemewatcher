#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

docker build -t extract-tandroid .

python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
