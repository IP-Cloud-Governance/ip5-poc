from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ip5_poc.db import connect, load_json_into_db
from ip5_poc.api.oscal_objects import (
    catalog_router,
    component_definition_router
    )
from ip5_poc.api.triggers import trigger_router

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

# Router inclusions
app.include_router(catalog_router)
app.include_router(component_definition_router)
app.include_router(trigger_router)