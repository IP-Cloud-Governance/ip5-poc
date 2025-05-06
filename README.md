# ip5-poc

This project servces

## Setup
This setup uses python3.13 stable version and poetry as package management tool
```bash
# Install pyhton venv
sudo apt install python3.13 python3.13-venv

# Connect to venv
source .venv/bin/activate

# Install pipx
python3 -m pip install --user pipx

# Install poetry
pipx install poetry

# Install project dependencies
poetry update

# Start fastAPI
fastapi dev src/ip5_poc/main.py
```