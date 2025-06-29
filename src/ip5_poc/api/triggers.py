from uuid import UUID
from fastapi import APIRouter, Depends
from ip5_poc.core.dependencies import get_az_credentials, get_db
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import PolicyClient
from ip5_poc.services import project_service,oscal_service
from motor.motor_asyncio import AsyncIOMotorDatabase

trigger_router = APIRouter(prefix="/triggers", tags=["Manual triggering"])


@trigger_router.post(
    "/projects/{project_id}/deploy",
    name="Deploy policies according to project context information",
)
async def deploy_policies(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    project = await project_service.get_project(project_id=project_id, db=db)
    policy_set_definitions: dict[str, str]
    ssp = await oscal_service.get_ssp_by_project(project_id=project_id, db=db)
    
    for requirement in ssp.root.system_security_plan.control_implementation.implemented_requirements:
        return None