from contextlib import asynccontextmanager
from uuid import UUID
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from pydantic import BaseModel
from ip5_poc.db import connect, load_json_into_db
from ip5_poc.dependencies import get_db
from ip5_poc.generated_oscal_model import (
    Model,
)
from motor.motor_asyncio import AsyncIOMotorDatabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    mongo_client = connect()
    app.state.db = mongo_client["ip5poc"]
    await load_json_into_db(app.state.db)

    yield  # App runs here

    # Clean up
    mongo_client.close()
    print("MongoDB connection closed")


# General setup of fast api
app = FastAPI(title="ip5-poc OSCAL", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://viewer.oscal.io"
    ],  # or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
catalog_router = APIRouter(prefix="/catalogs", tags=["Catalogs"])
component_definition_router = APIRouter(
    prefix="/component-definitions", tags=["Component Definitions"]
)
trigger_router = APIRouter(prefix="/triggers", tags = ["Manual triggering"])

class ProjectContext(BaseModel):
    name: str
    aws_paths: list[str] = []
    azure_paths: list[str] = []

# Endpoints
@trigger_router.post("/policy-deployment", name = "Deploy policies according to project context information")
async def deploy_policies():

    # Static project context which would normally be posted by a project responsible
    poc_context = ProjectContext(
        name = "poc-resource",
        azure_paths=[
            "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov"
        ]
    )

    return "asdf"

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


# Router inclusions
app.include_router(catalog_router)
app.include_router(component_definition_router)
app.include_router(trigger_router)