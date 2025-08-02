from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ip5_poc.core.dependencies import get_api_key, get_az_credentials, get_db
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import (
    CloudPlattformPath,
)
from ip5_poc.services import assessment_service
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging


trigger_router = APIRouter(
    prefix="/triggers", tags=["Manual triggering"], dependencies=[Depends(get_api_key)]
)

logger = logging.getLogger(__name__)


class PolicySetDefinitions(BaseModel):
    search_path: CloudPlattformPath
    policy_ids: list[str]
    contorl_id: str


@trigger_router.post(
    "/projects/{project_id}/assessment-results",
    name="Perform an assessment and create an result based on the latest assessment plan",
)
async def analyze_deployment(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    await assessment_service.create_assessment(
        credential=credential,
        db=db,
        project_id=project_id
    )


@trigger_router.post(
    "/projects/{project_id}/assessment-plan",
    name="Create assessment plan for system-security-plan of project",
)
async def deploy_policies(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Collected policies of an ssp of a project and deploys them on the cloud
    """
    res = await assessment_service.create_policies_and_assessment_plan(
        db=db, credential=credential, project_id=project_id
    )
    return res.model_dump(by_alias=True, exclude_none=True)
