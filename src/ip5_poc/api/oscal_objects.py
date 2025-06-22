from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ip5_poc.core.dependencies import get_az_credentials, get_db
from ip5_poc.models.generated_oscal_model import InformationType, Model, OscalCompleteOscalImplementationCommonSystemComponent, OscalCompleteOscalImplementationCommonSystemId, OscalCompleteOscalImplementationCommonSystemUser, OscalCompleteOscalMetadataLink, OscalCompleteOscalMetadataMetadata, OscalCompleteOscalMetadataProperty, OscalCompleteOscalSspAuthorizationBoundary, OscalCompleteOscalSspControlImplementation, OscalCompleteOscalSspImplementedRequirement, OscalCompleteOscalSspImportProfile, OscalCompleteOscalSspStatus, OscalCompleteOscalSspSystemCharacteristics, OscalCompleteOscalSspSystemImplementation, OscalCompleteOscalSspSystemInformation, OscalCompleteOscalSspSystemSecurityPlan, Status
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.mgmt.resource.resources.models import GenericResourceExpanded
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import AzureCloudRessource, ProjectContext
import re
from datetime import datetime, timezone
import uuid

component_definition_router = APIRouter(
    prefix="/component-definitions", tags=["OSCAL"]
)
catalog_router = APIRouter(prefix="/catalogs", tags=["OSCAL"])
ssp_router = APIRouter(prefix="/ssp", tags=["OSCAL"])


@catalog_router.get("/{catalog_id}.json", name="Get catalog with all components")
async def read_catalog(catalog_id: UUID, db: AsyncIOMotorDatabase = Depends(get_db)):
    entry = await db["catalogs"].find_one({"catalog.uuid": str(catalog_id)}, {"_id": 0})
    if entry is None:
        raise HTTPException(status_code=404, detail="Catalog not found")
    else:
        return Model.model_validate(entry).model_dump(by_alias=True, exclude_none=True)


@component_definition_router.get(
    "/{component_definition_id}.json", name="Get component definition"
)
async def read_component_definition(
    component_definition_id: UUID, db: AsyncIOMotorDatabase = Depends(get_db)
):
    entry = await db["component-definitions"].find_one(
        {"component-definition.uuid": str(component_definition_id)}, {"_id": 0}
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Component definition not found")
    else:
        return Model.model_validate(entry).model_dump(by_alias=True, exclude_none=True)

poc_context = ProjectContext(
        name = "poc-resource",
        azure_paths=[
            "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768",
            "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov"
        ]
    )

@ssp_router.post("", name = "Create system security plan by analyzing project context")
async def create_ssp(context: ProjectContext = poc_context, credential: DefaultAzureCredential=Depends(get_az_credentials), db: AsyncIOMotorDatabase = Depends(get_db)):
    # Get azure resources based on project context
    all_ressources: list[AzureCloudRessource] = _get_az_ressources(azure_paths=context.azure_paths, az_credential=credential)
    identified_components: List[OscalCompleteOscalImplementationCommonSystemComponent] = []

    for resource in all_ressources:
        print(f">> {resource.ressource.type}")
        components_definitions = await db["component-definitions"].find(
            {"component-definition.components.props.value": resource.ressource.type},
            {"_id": 0}
        ).to_list()
        if len(components_definitions) == 0:
            current_comp = OscalCompleteOscalImplementationCommonSystemComponent(
                uuid=str(uuid.uuid4()), # Retrieve here uuid from already store compnent definition
                type="service",
                # title=resource.ressource.name,
                title="title",
                # description=resource.ressource.name,
                description="descdription",
                status=Status(
                    state="state-of-resource"
                ),
                props=[
                    OscalCompleteOscalMetadataProperty(
                        name="azure-region",
                        value=resource.ressource.location
                    )
                ]
            )
            identified_components.append(current_comp)
        # else:
            # TODO add existing component defnition to array and create referenc e.g. in prop field 
            # print(components_definitions)
            # current_comp = Model.model_validate(components_definitions[0])
            # identified_components.append(current_comp)

    current_time=datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    ssp = OscalCompleteOscalSspSystemSecurityPlan(
        uuid=str(uuid.uuid4()),
        metadata=OscalCompleteOscalMetadataMetadata(
            title=context.name,
            published=current_time,
            last_modified=current_time,
            version="0.1",
            oscal_version="1.1.3"
        ),
        system_characteristics=OscalCompleteOscalSspSystemCharacteristics(
            system_name=context.name,
            system_information=OscalCompleteOscalSspSystemInformation(
                information_types=[
                    InformationType( # TODO retrieve this by using resource tag
                        uuid=str(uuid.uuid4()),
                        title="Non-sensitive data",
                        description="Demo application doesnt hold any sensitive data"
                    )
                ]
            ),
            system_ids=[
                OscalCompleteOscalImplementationCommonSystemId(
                    id=str(uuid.uuid4())
                )
            ],
            # TODO retrieve this by using project context
            description="<description>",
            status=OscalCompleteOscalSspStatus(
                state="under-development"
            ), # TODO retrieve this by using resource tag,
            authorization_boundary=OscalCompleteOscalSspAuthorizationBoundary(
                description="<authorization-boudary>"
            )
        ),
        import_profile=OscalCompleteOscalSspImportProfile(
            href="https://xyz.com"
        ),
        system_implementation=OscalCompleteOscalSspSystemImplementation(
            users=[
                OscalCompleteOscalImplementationCommonSystemUser(
                    uuid=str(uuid.uuid4()),
                    role_ids=["admin"],
                    description="Administers the AKS"
                )
            ],
            components=identified_components
        ),
        # TODO make this part dynamic
        control_implementation=OscalCompleteOscalSspControlImplementation(
            description="<description>",
            implemented_requirements=[
                OscalCompleteOscalSspImplementedRequirement(
                    uuid=str(uuid.uuid4()),
                    control_id="controlid"
                )
            ]
        )
    )

    return ssp.model_dump(by_alias=True, exclude_none=True)


def _get_az_ressources(azure_paths: list[str], az_credential: DefaultAzureCredential) -> list[AzureCloudRessource]:
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