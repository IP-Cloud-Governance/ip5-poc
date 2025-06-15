from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ip5_poc.core.dependencies import get_db
from ip5_poc.models.generated_oscal_model import Model
from motor.motor_asyncio import AsyncIOMotorDatabase

component_definition_router = APIRouter(
    prefix="/component-definitions", tags=["Component Definitions"]
)
catalog_router = APIRouter(prefix="/catalogs", tags=["Catalogs"])


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
