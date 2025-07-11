from collections import defaultdict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ip5_poc.core.dependencies import get_api_key, get_az_credentials, get_db
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import PolicyClient
from azure.mgmt.resource.policy.models import (
    PolicyDefinitionReference,
    PolicySetDefinition,
)
from ip5_poc.models.generated_oscal_model import OscalCompleteOscalApAssessmentPlan, OscalCompleteOscalAssessmentCommonImportSsp, OscalCompleteOscalAssessmentCommonTask, OscalCompleteOscalMetadataProperty, Type4
from ip5_poc.models.model import (
    CacTaskType,
    CloudPlattform,
    CloudPlattformPath,
    MongoDBCollections,
    OscalPropertyIdentifier,
)
from ip5_poc.services import project_service, oscal_service
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.core.exceptions import ResourceNotFoundError
import logging
import re
import uuid

from ip5_poc.services.azure_service import get_rg_pattern

trigger_router = APIRouter(
    prefix="/triggers", tags=["Manual triggering"], dependencies=[Depends(get_api_key)]
)

logger = logging.getLogger(__name__)


class PolicySetDefinitions(BaseModel):
    searchPath: CloudPlattformPath
    cloudPaths: list[str]


@trigger_router.get(
    "/projects/{project_id}/assessment-result",
    name="Get assesment result for current state of ressources",
)
async def analyze_deployment(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return "Not implemeted yet"


@trigger_router.post(
    "/projects/{project_id}/deploy",
    name="Deploy policies according to project context information",
)
async def deploy_policies(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Collected policies of an ssp of a project and deploys them on the cloud
    """
    project = await project_service.get_project(project_id=project_id, db=db)
    # policy_set_definitions: list[tuple[CloudPlattformPath, list[str]]] = []
    policy_set_definitions: list[PolicySetDefinitions] = []
    ssp_raw = await oscal_service.get_ssp_by_project(project_id=project_id, db=db)
    ssp = ssp_raw.root.system_security_plan

    # Gather policy references from the security plan assigned to the project
    for implemented_requirement in ssp.control_implementation.implemented_requirements:
        if len(implemented_requirement.by_components) is 0:
            raise HTTPException(
                status_code=500,
                detail=f"Implemented requirement for {implemented_requirement.control_id}|{implemented_requirement.uuid} should at least contain one by-component",
            )
        # TODO make this more generic. Theoretically one requirement can be implemented by multiple components -> should be combined into single policy
        implemented_component = implemented_requirement.by_components[0]
        component = next(
            (
                c
                for c in ssp.system_implementation.components
                if implemented_component.component_uuid == c.uuid
            ),
            None,
        )
        if component is None:
            raise HTTPException(
                status_code=500,
                detail=f"No mathching component in system_implementation for {implemented_component.component_uuid}",
            )
        logger.info(component.model_dump_json())
        search_id = next(
            (
                p
                for p in component.props
                if p.name.root == OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value
            ),
            None,
        )
        plattform_type = next(
            (
                p
                for p in component.props
                if p.name.root == OscalPropertyIdentifier.CAC_PLATTFORM_TYPE.value
            ),
            None,
        )
        if plattform_type is None:
            raise HTTPException(
                status_code=500,
                detail=f"Component doesnt has an cac plattform type bound to it via {OscalPropertyIdentifier.CAC_PLATTFORM_TYPE.value}",
            )
        if search_id is None:
            raise HTTPException(
                status_code=500,
                detail=f"Component doesnt has an cac search id bound to it via {OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value}",
            )

        # TODO support different plattforms as well
        if plattform_type.value.root == CloudPlattform.AZURE.value:
            search_item = next(
                (
                    p
                    for p in project.azure_paths
                    if p.plattform.value == CloudPlattform.AZURE.value
                    and str(p.id) == search_id.value.root
                ),
                None,
            )
            if search_item is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"Search id {search_id.value.root} should be part of the project {project.id} but isnt (anymore)",
                )
            # Retrieve policies from ssp
            # TODO this check is here because there might by requirements where not policy is set -> t6.1
            if implemented_requirement.props:
                azure_policies = list(
                    filter(
                        lambda x: x.name.root
                        == OscalPropertyIdentifier.AZURE_POLICY.value,
                        implemented_requirement.props,
                    )
                )
                policy_set_definitions.append(
                    PolicySetDefinitions(
                        searchPath=search_item,
                        cloudPaths=[p.value.root for p in azure_policies],
                    )
                )
                # policy_set_definitions.append((search_item, [p.value for p in azure_policies]))

    # Merge azure policies
    azure_policies_subset = list(
        filter(
            lambda x: x.searchPath.plattform == CloudPlattform.AZURE,
            policy_set_definitions,
        )
    )
    azure_policies_subset = _merge_policy_sets(azure_policies_subset)

    # Create azure policy initiative
    for azure_policy_set in azure_policies_subset:
        match = re.fullmatch(get_rg_pattern(), azure_policy_set.searchPath.path)
        policy_client_subscription_id = match.group("subscription_id")
        policy_client = PolicyClient(
            credential=credential, subscription_id=policy_client_subscription_id
        )

        policy_definitions: list[PolicyDefinitionReference] = [
            PolicyDefinitionReference(policy_definition_id=cloud_path)
            for cloud_path in azure_policy_set.cloudPaths
        ]

        initiative_definition: PolicySetDefinition = PolicySetDefinition(
            display_name=f"ip5sgcgov project {str(project.name)} for search {str(azure_policy_set.searchPath.id)}",
            description=f"ip5sgcgov project {str(project.name)} for search {str(azure_policy_set.searchPath.id)}",
            policy_definitions=policy_definitions,
            metadata={
                "category": "ip5sgcgov-project",
                "ip5sgcgov-project-name": project.name,
                "ip5sgcgov-project-id": str(project.id),
                "ip5sgcgov-ssp-id": str(ssp.uuid.root),
                "ip5sgcgov-search-path": azure_policy_set.searchPath.path,
                "ip5sgcgov-search-path-id": azure_policy_set.searchPath.id,
            },
        )
        policy_set_definition_name = f"ip5sgcgov-{str(azure_policy_set.searchPath.id)}"
        logger.info(
            f"Try to create policy {policy_set_definition_name} for project {project.name} with id {str(project.id)}"
        )

        logger.info("Check if policy is already existing")
        try:
            policy_client.policy_definitions.get(
                policy_definition_name=policy_set_definition_name
            )
            logger.info(f"Policy for {policy_set_definition_name} exisnting")
            logger.info(f"Try UPDATING policy {policy_set_definition_name}")
        except ResourceNotFoundError:
            logger.info(f"Policy for {policy_set_definition_name} is not found")
            logger.info(f"Try CREATING policy {policy_set_definition_name}")

        result = policy_client.policy_set_definitions.create_or_update(
            policy_set_definition_name=policy_set_definition_name,
            parameters=initiative_definition,
        )

        if result:
            logger.info(f"Created/updated policy with id {result.id}")

            # Update project context with policy initiative id if not already exitsing
            await db[MongoDBCollections.PROJECTS.value].update_one(
                {
                    'id': str(project_id),
                    'azure_paths.id': str(azure_policy_set.searchPath.id)
                },
                {
                    '$addToSet': {
                        'azure_paths.$.plattform_policy_reference' : result.id
                    }
                }
            )

    # Create assessment-plan with pre-defined task for assingning policy initiatives
    updated_project = await project_service.get_project(project_id=project_id, db=db)

    # TODO create assessment plan and persist it
    # TODO run assessment plan -> create initiative assignment
    for path in updated_project.azure_paths:
        task = OscalCompleteOscalAssessmentCommonTask(
            uuid=str(uuid.uuid4()),
            description="Check ressources in scope of",
            type=Type4.action,
            props=[
                OscalCompleteOscalMetadataProperty(
                    uuid=str(uuid.uuid4()),
                    name=OscalPropertyIdentifier.CAC_TASK_TYPE,
                    value=CacTaskType.CAC_SEARCH_PATH_CHECK,
                )
            ],
            tasks=[
                # TODO 2 tasks ... one for policy iniative assginemnt, one for checking it during assessment
            ]
        )


    assessment_plan = OscalCompleteOscalApAssessmentPlan(
        uuid=str(uuid.uuid4()),
        import_ssp=OscalCompleteOscalAssessmentCommonImportSsp(
            href=str(ssp.uuid)
        ),
        tasks=[
            OscalCompleteOscalAssessmentCommonTask(
                uuid=str(uuid.uuid4()),
                description="Check ressources in scope of",
                type=Type4.action,
            )
        ]
    )

    return await project_service.get_project(project_id=project_id, db=db)


def _merge_policy_sets(
    policy_sets: list[PolicySetDefinitions],
) -> list[PolicySetDefinitions]:
    """
    Merge policy paths by same search query from which they originated
    """
    grouped = defaultdict(list)

    for policy in policy_sets:
        key = policy.searchPath.id
        grouped[key].append(policy)

    merged = []
    for key, items in grouped.items():
        # Merge cloudPaths
        all_cloud_paths: list[str] = []
        for item in items:
            all_cloud_paths.extend(item.cloudPaths)

        # Reuse one of the identical searchPaths
        merged.append(
            PolicySetDefinitions(
                searchPath=items[0].searchPath, cloudPaths=all_cloud_paths
            )
        )

    return merged
