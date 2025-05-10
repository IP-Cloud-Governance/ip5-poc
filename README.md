# ip5-poc

This project serves as poc environment for [ip5-documentation](https://github.com/IP-Cloud-Governance/ip5-project-documentation)

## Setup
This setup uses python3.13 stable version and poetry as package management tool
```bash
# Install pyhton venv
sudo apt install python3.13 python3.13-venv

# Connect to venv
source .venv/bin/activate

# Install pipx
python3 -m pip install pipx poetry

# Install poetry
pipx install poetry

# Install project dependencies
poetry update

# Start fastAPI
fastapi dev src/ip5_poc/main.py
```
