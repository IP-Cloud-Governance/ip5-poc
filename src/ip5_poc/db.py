from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
import json
from pathlib import Path
from ip5_poc.model import (
    Model,
)
from motor.motor_asyncio import AsyncIOMotorDatabase

MONGO_URL = "mongodb://user:secret@localhost:27017/"
DB_NAME = "mydatabase"

def connect() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(MONGO_URL)

async def load_json_into_db(db: AsyncIOMotorDatabase):
    """
    Load static json definition of OSCAL catalog and component-defintion into db
    """
    catalog_path = Path(__file__).parent / "data" / "raw" / "catalogs"
    for file_path in catalog_path.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                component_definition = json.load(f)
                validated_model = Model.model_validate(component_definition)
                catalog_id = validated_model.root.catalog.uuid.model_dump()
                existing = await db["catalogs"].find_one(
                    {"catalog.uuid": str(catalog_id)}
                )
                if existing is None:
                    print(f"Insert catalog ${catalog_id}")
                    await db["catalogs"].insert_one(
                        jsonable_encoder(
                            validated_model.model_dump(by_alias=True, exclude_none=True)
                        )
                    )
                else:
                    print("Catalog already present")
        except Exception as e:
            print(f"Error loading catalog from {file_path}: {e}")

    components_path = Path(__file__).parent / "data" / "raw" / "components"
    for file_path in components_path.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                component_definition = json.load(f)
                validated_model = Model.model_validate(component_definition)
                component_id = (
                    validated_model.root.component_definition.uuid.model_dump()
                )
                existing = await db["component-definitions"].find_one(
                    {"component-definition.uuid": str(component_id)}
                )
                if existing is None:
                    print(f"Insert component-definition ${component_id}")
                    await db["component-definitions"].insert_one(
                        jsonable_encoder(
                            validated_model.model_dump(by_alias=True, exclude_none=True)
                        )
                    )
                else:
                    print("Component-definition already present")
        except Exception as e:
            print(
                f"Error loading component-definition definition from {file_path}: {e}"
            )