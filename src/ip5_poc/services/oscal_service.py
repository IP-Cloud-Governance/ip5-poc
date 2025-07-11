from typing import Any, List
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
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
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import (
    AzureCloudRessource,
    MongoDBCollections,
    OscalPropertyIdentifier,
    ProjectContext,
)
from datetime import datetime, timezone
from ip5_poc.services import azure_service
import uuid
import logging

logger = logging.getLogger(__name__)


async def get_ssp(ssp_id: uuid.UUID, db: AsyncIOMotorDatabase) -> Model:
    entry = await db[MongoDBCollections.SYSTEM_SECURITY_PLANS.value].find_one(
        {"system-security-plan.uuid": str(ssp_id)}, {"_id": 0}
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="System security plan not found")
    else:
        return Model.model_validate(entry).model_dump(by_alias=True, exclude_none=True)


async def get_ssp_by_project(project_id: uuid.UUID, db: AsyncIOMotorDatabase) -> Model:
    entry = await db[MongoDBCollections.SYSTEM_SECURITY_PLANS.value].find_one(
        {"system-security-plan.system-characteristics.system-ids.id": str(project_id)},
        {"_id": 0},
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="System security plan not found")
    else:
        return Model.model_validate(entry)


async def create_ssp(
    context: ProjectContext,
    credential: DefaultAzureCredential,
    db: AsyncIOMotorDatabase,
):
    # Get azure resources based on project context
    all_ressources: list[AzureCloudRessource] = azure_service.get_az_ressources(
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
            await db[MongoDBCollections.COMPONENT_DEFINITIONS.value]
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
                        name=OscalPropertyIdentifier.AZURE_REGION,
                        value=resource.ressource.location,
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="azure-resource-type", value=resource.ressource.type
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="azure-resource-id", value=resource.ressource.id
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="cac-project-serach-id",
                        value=str(resource.search_basis.id),
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name="cac-plattform-type",
                        value=str(resource.search_basis.plattform),
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
                        name=OscalPropertyIdentifier.AZURE_REGION,
                        value=resource.ressource.location,
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name=OscalPropertyIdentifier.AZURE_RESOURCE_TYPE,
                        value=resource.ressource.type,
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name=OscalPropertyIdentifier.AZURE_RESOURCE_ID,
                        value=resource.ressource.id,
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name=OscalPropertyIdentifier.OSCAL_DERIVED_COMPONENT_DEFINITION_UUID,
                        value=str(wrapper.uuid.root),
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name=OscalPropertyIdentifier.OSCAL_DERIVED_COMPONENT_UUID,
                        value=str(predef_component.uuid.root),
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name=OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID,
                        value=str(resource.search_basis.id),
                    ),
                    OscalCompleteOscalMetadataProperty(
                        name=OscalPropertyIdentifier.CAC_PLATTFORM_TYPE,
                        value=str(resource.search_basis.plattform),
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
                            description=f"{req.control_id.root} is implemented by {resource.ressource.id}",
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
                OscalCompleteOscalImplementationCommonSystemId(id=str(context.id))
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

    await db[MongoDBCollections.SYSTEM_SECURITY_PLANS.value].insert_one(
        jsonable_encoder(ssp_model.model_dump(by_alias=True, exclude_none=True))
    )

    return ssp_model.model_dump(by_alias=True, exclude_none=True)
