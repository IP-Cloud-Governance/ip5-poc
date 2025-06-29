import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from ip5_poc.core.dependencies import get_api_key, get_az_credentials, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import CloudPlattform, CloudPlattformPath, ProjectContext, ProjectContextRequest
from ip5_poc.services.oscal_service import create_ssp, get_ssp_by_project

project_router = APIRouter(prefix="/projects", tags=["Project"], dependencies=[Depends(get_api_key)])

poc_context_request = ProjectContextRequest(
    name="poc-resource",
    azure_paths=[
        "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov-sample",
        "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov",
    ],
)


@project_router.post(
    "",
    name="Add project cloud context and create ssp",
)
async def post_project(
    project_context: ProjectContextRequest = poc_context_request,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    project = ProjectContext(
        id=uuid.uuid4(),
        name=project_context.name,
        azure_paths=[CloudPlattformPath(id=uuid.uuid4(), path=p, plattform=CloudPlattform.AZURE) for p in project_context.azure_paths],
        aws_paths=[CloudPlattformPath(id=uuid.uuid4(), path=p, plattform=CloudPlattform.AWS) for p in project_context.aws_paths]
    )
    await db["projects"].insert_one(
        jsonable_encoder(project.model_dump(by_alias=True, exclude_none=True))
    )
    await create_ssp(context=project, credential=credential, db=db)
    return project

@project_router.get("/{project_id}/ssp")
async def get_ssp_for_project(project_id: uuid.UUID,db: AsyncIOMotorDatabase = Depends(get_db)):
    project = await db["projects"].find_one(
        {"id": str(project_id)},
        {"_id":0}
    )
    if project is None:
        raise HTTPException(status_code=404, detail=f"Project with id {str(project_id)} not found")
    
    return await get_ssp_by_project(db=db, project_id=project_id)