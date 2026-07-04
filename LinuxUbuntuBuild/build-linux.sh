#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tk python3-dev
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-linux.txt
pyinstaller --clean build-linux.spec
