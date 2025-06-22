from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ip5_poc.core.dependencies import get_az_credentials, get_db
from ip5_poc.models.generated_oscal_model import Model
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import GenericResourceExpanded
from ip5_poc.models.model import AzureCloudRessource, ProjectContext
import re

trigger_router = APIRouter(prefix="/triggers", tags = ["Manual triggering"])

@trigger_router.post("/ssp/{ssp_id}/deploy-policies", name = "Deploy policies according to project context information")
async def deploy_policies(ssp_id: UUID, credential: DefaultAzureCredential=Depends(get_az_credentials)):
    return ssp_id