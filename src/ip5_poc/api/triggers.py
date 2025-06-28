from uuid import UUID
from fastapi import APIRouter, Depends
from ip5_poc.core.dependencies import get_az_credentials
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import PolicyClient

trigger_router = APIRouter(prefix="/triggers", tags=["Manual triggering"])


@trigger_router.post(
    "/projects/{project_id}/deploy",
    name="Deploy policies according to project context information",
)
async def deploy_policies(
    project_id: UUID, credential: DefaultAzureCredential = Depends(get_az_credentials)
):
    policy_client = PolicyClient(credential)
    return project_id
