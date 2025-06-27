from uuid import UUID
from fastapi import APIRouter, Depends
from ip5_poc.core.dependencies import get_az_credentials
from azure.identity import DefaultAzureCredential

trigger_router = APIRouter(prefix="/triggers", tags=["Manual triggering"])


@trigger_router.post(
    "/ssp/{ssp_id}/deploy-policies",
    name="Deploy policies according to project context information",
)
async def deploy_policies(
    ssp_id: UUID, credential: DefaultAzureCredential = Depends(get_az_credentials)
):
    return ssp_id
