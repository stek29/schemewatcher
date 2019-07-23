#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

source "./env.sh"
venv/bin/python checker.py
