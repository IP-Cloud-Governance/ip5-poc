# ip5-poc

This project serves as poc environment for [ip5-documentation](https://github.com/IP-Cloud-Governance/ip5-project-documentation)


## :rocket: Deployment

The swagger-api of the app is deployed here [https://ip5-poc-f2a4adeqemfff2at.westeurope-01.azurewebsites.net/docs](https://ip5-poc-f2a4adeqemfff2at.westeurope-01.azurewebsites.net/docs).

The generated document can be viewed in the [OSCAL viewer](https://viewer.oscal.io/) by copying [https://ip5-poc-f2a4adeqemfff2at.westeurope-01.azurewebsites.net/catalogs/si001.json](https://ip5-poc-f2a4adeqemfff2at.westeurope-01.azurewebsites.net/catalogs/si001.json)

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