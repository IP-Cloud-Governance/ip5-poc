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

poc_context = ProjectContext(
        name = "poc-resource",
        azure_paths=[
            "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768",
            "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov"
        ]
    )


trigger_router = APIRouter(prefix="/triggers", tags = ["Manual triggering"])

@trigger_router.post("/policy-deployment", name = "Deploy policies according to project context information")
async def deploy_policies(context: ProjectContext = poc_context, credential: DefaultAzureCredential=Depends(get_az_credentials)):
    all_ressources: list[AzureCloudRessource] = get_az_ressources(azure_paths=context.azure_paths, az_credential=credential)

    # Retrive here azure ressources

    # TODO continue here mapping azure ressourcey by using 'type' to policies

    return all_ressources

def get_az_ressources(azure_paths: list[str], az_credential: DefaultAzureCredential) -> list[AzureCloudRessource]:
    """
    Retrieve ressources based on project configuration
    """
    all_ressources: list[GenericResourceExpanded] = []

    # Retrieve ressources of subscription
    subscription_pattern = r"^/subscriptions/(?P<subscription_id>[0-9a-fA-F-]{36})$"
    rg_pattern = r"^/subscriptions/(?P<subscription_id>[0-9a-fA-F-]{36})/resourceGroups/(?P<resource_group>[^/]+)$"

    # Lookup ressources from azure
    for path in azure_paths:
        subscription_match = re.fullmatch(subscription_pattern, path)
        rg_match = re.fullmatch(rg_pattern, path)
        print(f"search in azure for {path}")
        if subscription_match:
            # Retrieve ressources of subscription
            subscription_id = subscription_match.group("subscription_id")
            client = ResourceManagementClient(az_credential, subscription_id)
            all_ressources += client.resources.list()
        elif rg_match:
            # Retrieve groups of of subscription
            subscription_id = rg_match.group("subscription_id")
            rg_name = rg_match.group("resource_group")
            client = ResourceManagementClient(az_credential, subscription_id)
            all_ressources += client.resources.list_by_resource_group(rg_name)

    all_ressources.sort(key=lambda x: x.id)
    
    # Unique resources / without duplicates
    unique_list = list({res.id: res for res in all_ressources}.values())
    return list(map(lambda r: AzureCloudRessource(ressource=r),unique_list))