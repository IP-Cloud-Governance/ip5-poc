from uuid import UUID
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from ip5_poc.models.model import MongoDBCollections, ProjectContext


async def get_project(project_id: UUID, db: AsyncIOMotorDatabase) -> ProjectContext:
    project = await db[MongoDBCollections.PROJECTS.value].find_one({"id": str(project_id)}, {"_id": 0})
    if project is None:
        raise HTTPException(
            status_code=404, detail=f"Project with id {str(project_id)} not found"
        )
    return ProjectContext.model_validate(project)
