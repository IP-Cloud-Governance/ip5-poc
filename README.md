# ip5-poc

This project serves as poc environment for [ip5-documentation](https://github.com/IP-Cloud-Governance/ip5-project-documentation)


## :rocket: Deployment

The swagger-api of the app is deployed here [https://ip5-poc-webapp.azurewebsites.net/docs](https://ip5-poc-webapp.azurewebsites.net/docs).

The generated document can be viewed in the [OSCAL viewer](https://viewer.oscal.io/) by copying [si001.json](https://ip5-poc-webapp.azurewebsites.net/catalogs/si001.json)

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

# If needed: Regenerate pydantic model based on latest json schema definition from OSCAL NIST
# Current used one is 1.1.3 https://pages.nist.gov/OSCAL-Reference/models/v1.1.3/complete/json-outline/
datamodel-codegen --input src/ip5_poc/data/raw/oscal_complete_schema_v1.1.3.json --input-file-type jsonschema --output src/ip5_poc/model.py --output-model-type pydantic_v2.BaseModel --allow-population-by-field-name
```

## Database
Connect to local db by using mongo db vs code extension and the connection string `mongodb://user:secret@localhost:27017/` make sure that you run `docker compose up` before to setup mongo db locally. To reset db run `docker compose down --volumes`