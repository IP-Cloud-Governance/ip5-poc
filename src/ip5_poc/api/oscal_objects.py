from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from ip5_poc.core.dependencies import get_az_credentials, get_db
from ip5_poc.models.generated_oscal_model import (
    InformationType,
    Model,
    Model3,
    Model4,
    OscalCompleteOscalImplementationCommonSystemComponent,
    OscalCompleteOscalImplementationCommonSystemId,
    OscalCompleteOscalImplementationCommonSystemUser,
    OscalCompleteOscalMetadataMetadata,
    OscalCompleteOscalMetadataProperty,
    OscalCompleteOscalSspAuthorizationBoundary,
    OscalCompleteOscalSspByComponent,
    OscalCompleteOscalSspControlImplementation,
    OscalCompleteOscalSspImplementedRequirement,
    OscalCompleteOscalSspImportProfile,
    OscalCompleteOscalSspStatus,
    OscalCompleteOscalSspSystemCharacteristics,
    OscalCompleteOscalSspSystemImplementation,
    OscalCompleteOscalSspSystemInformation,
    OscalCompleteOscalSspSystemSecurityPlan,
    Status,
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.mgmt.resource.resources.models import GenericResourceExpanded
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import AzureCloudRessource, ProjectContext
import re
from datetime import datetime, timezone
import uuid
import logging


logger = logging.getLogger(__name__)

component_definition_router = APIRouter(prefix="/component-definitions", tags=["OSCAL"])
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
    name="poc-resource",
    azure_paths=[
        "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768",
        "/subscriptions/55093e67-09be-455b-bee4-802b5ba38768/resourceGroups/ip5-scggov",
    ],
)


@ssp_router.get("/{ssp_id}.json", name="Get System Security Plan")
async def read_ssp(ssp_id: UUID, db: AsyncIOMotorDatabase = Depends(get_db)):
    entry = await db["ssps"].find_one(
        {"system-security-plan.uuid": str(ssp_id)}, {"_id": 0}
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="System security plan not found")
    else:
        return Model.model_validate(entry).model_dump(by_alias=True, exclude_none=True)


@ssp_router.post("", name="Create system security plan by analyzing project context")
async def create_ssp(
    context: ProjectContext = poc_context,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # Get azure resources based on project context
    all_ressources: list[AzureCloudRessource] = _get_az_ressources(
        azure_paths=context.azure_paths, az_credential=credential
    )
    identified_components: List[
        OscalCompleteOscalImplementationCommonSystemComponent
    ] = []
    implemented_requirements: List[OscalCompleteOscalSspImplementedRequirement] = []

    logger.info("Anaylzing azure resources")

    for resource in all_ressources:
        logger.info(f"{resource.ressource.type}")
        components_definitions: list[Any] = (
            await db["component-definitions"]
            .find(
                {
                    "component-definition.components.props.value": resource.ressource.type
                },
                {"_id": 0},
            )
            .to_list()
        )
        if len(components_definitions) == 0:
            current_comp = OscalCompleteOscalImplementationCommonSystemComponent(
                uuid=str(
                    uuid.uuid4()
                ),  # Retrieve here uuid from already store compnent definition
                type="service",
                title=resource.ressource.name,
                description=resource.ressource.name,
                status=Status(state="state-of-resource"),
                props=[
                    OscalCompleteOscalMetadataProperty(
                        name="azure-region", value=resource.ressource.location
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="azure-resource-type", value=resource.ressource.type
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="azure-resource-id", value=resource.ressource.id
                    ),
                ],
            )
            identified_components.append(current_comp)
        else:
            # TODO make this more generic
            wrapper = Model3.model_validate(
                components_definitions[0]
            ).component_definition
            predef_component = next(
                (
                    comp
                    for comp in wrapper.components
                    if (
                        prop
                        for prop in comp.props
                        if prop.value == resource.ressource.type
                    )
                ),
                None,
            )

            # Define actual component
            current_comp = OscalCompleteOscalImplementationCommonSystemComponent(
                uuid=str(uuid.uuid4()),
                type="service",
                title=predef_component.title,
                description=predef_component.description,
                status=Status(state="state-of-resource"),
                props=[
                    OscalCompleteOscalMetadataProperty(
                        name="azure-region", value=resource.ressource.location
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="azure-resource-type", value=resource.ressource.type
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="azure-resource-id", value=resource.ressource.id
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="oscal-derived-component-definition-uuid",
                        value=str(wrapper.uuid),
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="oscal-derived-component-uuid",
                        value=str(predef_component.uuid),
                    ),
                ],
            )
            identified_components.append(current_comp)

            # Define implementation of actual component
            # TODO make this more generic
            implementation = predef_component.control_implementations[0]

            for req in implementation.implemented_requirements:
                implemented_req = OscalCompleteOscalSspImplementedRequirement(
                    uuid=str(uuid.uuid4()),
                    control_id=req.control_id,
                    props=req.props,
                    by_components=[
                        OscalCompleteOscalSspByComponent(
                            component_uuid=current_comp.uuid,
                            uuid=str(uuid.uuid4()),
                            description=f"{req.control_id} is implemented by {resource.ressource.id}",
                        )
                    ],
                )
                implemented_requirements.append(implemented_req)

    current_time = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    ssp_id = uuid.uuid4()
    ssp = OscalCompleteOscalSspSystemSecurityPlan(
        uuid=str(ssp_id),
        metadata=OscalCompleteOscalMetadataMetadata(
            title=context.name,
            published=current_time,
            last_modified=current_time,
            version="0.1",
            oscal_version="1.1.3",
        ),
        system_characteristics=OscalCompleteOscalSspSystemCharacteristics(
            system_name=context.name,
            system_information=OscalCompleteOscalSspSystemInformation(
                information_types=[
                    InformationType(  # TODO retrieve this by using resource tag
                        uuid=str(uuid.uuid4()),
                        title="Non-sensitive data",
                        description="Demo application doesnt hold any sensitive data",
                    )
                ]
            ),
            system_ids=[
                OscalCompleteOscalImplementationCommonSystemId(id=str(uuid.uuid4()))
            ],
            # TODO retrieve this by using project context
            description="<description>",
            status=OscalCompleteOscalSspStatus(
                state="under-development"
            ),  # TODO retrieve this by using resource tag,
            authorization_boundary=OscalCompleteOscalSspAuthorizationBoundary(
                description="<authorization-boudary>"
            ),
        ),
        import_profile=OscalCompleteOscalSspImportProfile(href="https://xyz.com"),
        system_implementation=OscalCompleteOscalSspSystemImplementation(
            users=[
                OscalCompleteOscalImplementationCommonSystemUser(
                    uuid=str(uuid.uuid4()),
                    role_ids=["admin"],
                    description="Administers the AKS",
                )
            ],
            components=identified_components,
        ),
        # TODO make this part dynamic
        control_implementation=OscalCompleteOscalSspControlImplementation(
            description=f"Controls implemented by project {context.name}",
            implemented_requirements=(
                implemented_requirements
                if implemented_requirements
                else [
                    OscalCompleteOscalSspImplementedRequirement(
                        uuid=str(uuid.uuid4()), control_id="default"
                    )
                ]
            ),
        ),
    )

    ssp_model = Model4(system_security_plan=ssp)

    await db["ssps"].insert_one(
        jsonable_encoder(ssp_model.model_dump(by_alias=True, exclude_none=True))
    )

    return ssp_model.model_dump(by_alias=True, exclude_none=True)


def _get_az_ressources(
    azure_paths: list[str], az_credential: DefaultAzureCredential
) -> list[AzureCloudRessource]:
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
        logger.info(f"search in azure for {path}")
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
    return list(map(lambda r: AzureCloudRessource(ressource=r), unique_list))
