from fastapi import APIRouter, FastAPI
from oscal_pydantic.document import Document
import oscal_pydantic.catalog as catalog
import oscal_pydantic.core.common as common
from ip5_poc.data import catalog as bv_catalog
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException

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