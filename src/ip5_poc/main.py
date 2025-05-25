from fastapi import APIRouter, FastAPI
from oscal_pydantic.document import Document
import oscal_pydantic.catalog as catalog
import oscal_pydantic.core.common as common
from ip5_poc.data import catalog as bv_catalog
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import json
from pathlib import Path

app = FastAPI(
    title="ip5-poc OSCAL",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://viewer.oscal.io"],  # or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

catalog_router = APIRouter(prefix="/catalogs", tags=["Catalogs"])
catalogs: Dict[str, Document] = dict()
catalogs['si001'] = bv_catalog.get_si001_catalog()

@catalog_router.get("/{catalog_name}.json", name="Get catalog with all components")
def read_catalog(catalog_name: str):
    if catalog_name in catalogs:
        return catalogs[catalog_name].model_dump(by_alias=True, exclude_none=True)
    else:
        raise HTTPException(status_code=404, detail="Catalog not found")
    
app.include_router(catalog_router)

component_definition_router = APIRouter(prefix="/component-definitions", tags=["Component Definitions"])
component_definitions: Dict[str, dict] = dict()

# Load component definitions from JSON files in the 'raw' directory
component_definitions_path = Path(__file__).parent / "data" / "raw"
for file_path in component_definitions_path.glob("*.json"):
    try:
        with open(file_path, "r") as f:
            component_definition = json.load(f)
            component_definitions[file_path.stem] = component_definition
    except Exception as e:
        print(f"Error loading component definition from {file_path}: {e}")

@component_definition_router.get("/{component_definition_name}.json", name="Get component definition")
def read_component_definition(component_definition_name: str):
    if component_definition_name in component_definitions:
        return component_definitions[component_definition_name]
    else:
        raise HTTPException(status_code=404, detail="Component Definition not found")

app.include_router(component_definition_router)