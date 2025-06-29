from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ip5_poc.core.dependencies import get_api_key, get_db
from ip5_poc.models.generated_oscal_model import (
    Model,
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from ip5_poc.models.model import ProjectContextRequest
import logging
import ip5_poc.services.oscal_service as oscal_service


logger = logging.getLogger(__name__)

component_definition_router = APIRouter(prefix="/component-definitions", tags=["OSCAL"], dependencies=[Depends(get_api_key)])
catalog_router = APIRouter(prefix="/catalogs", tags=["OSCAL"], dependencies=[Depends(get_api_key)])
ssp_router = APIRouter(prefix="/system-security-plans", tags=["OSCAL"], dependencies=[Depends(get_api_key)])


@catalog_router.get("/{catalog_id}.json", name="Get catalog with all components")
async def read_catalog(catalog_id: UUID, db: AsyncIOMotorDatabase = Depends(get_db)):
    entry = await db["catalogs"].find_one({"catalog.uuid": str(catalog_id)}, {"_id": 0})
    if entry is None:
        raise HTTPException(status_code=404, detail="Catalog not found")
    else:
        return Model.model_validate(entry).model_dump(by_alias=True, exclude_none=True)


@component_definition_router.get(
    "/{component_definition_id}.json", name="Get component definition"
)
async def read_component_definition(
    component_definition_id: UUID, db: AsyncIOMotorDatabase = Depends(get_db)
):
    entry = await db["component-definitions"].find_one(
        {"component-definition.uuid": str(component_definition_id)}, {"_id": 0}
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Component definition not found")
    else:
        return Model.model_validate(entry).model_dump(by_alias=True, exclude_none=True)


poc_context = ProjectContextRequest(
    name="poc-resource",
    azure_paths=[
        "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768",
        "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov",
    ],
)


@ssp_router.get("/{ssp_id}.json", name="Get System Security Plan")
async def read_ssp(ssp_id: UUID, db: AsyncIOMotorDatabase = Depends(get_db)):
    return await oscal_service.get_ssp(db=db, ssp_id=ssp_id)
