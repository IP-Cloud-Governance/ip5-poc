from collections import defaultdict
from datetime import datetime, timezone
from typing import DefaultDict
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from ip5_poc.core.dependencies import get_az_credentials, get_db
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import PolicyClient
from azure.mgmt.resource.policy.models import (
    PolicyDefinitionReference,
    PolicySetDefinition,
)
from ip5_poc.models.generated_oscal_model import ControlSelection, Model5, OscalCompleteOscalApAssessmentPlan, OscalCompleteOscalAssessmentCommonImportSsp, OscalCompleteOscalAssessmentCommonReviewedControls, OscalCompleteOscalAssessmentCommonSelectControlById, OscalCompleteOscalAssessmentCommonTask, OscalCompleteOscalMetadataMetadata, OscalCompleteOscalMetadataProperty, Type4
from ip5_poc.models.model import (
    CacTaskType,
    CloudPlattform,
    MongoDBCollections,
    OscalPropertyIdentifier,
    PolicySetDefinitions,
)
from ip5_poc.services import project_service, oscal_service
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.core.exceptions import ResourceNotFoundError
from pymongo import ReturnDocument
import logging
import re
import uuid

from ip5_poc.services.azure_service import get_rg_pattern


logger = logging.getLogger(__name__)


async def create_policies_and_assessment_plan(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Model5:
    """
    Collected policies of an ssp of a project and deploys them on the cloud
    """
    project = await project_service.get_project(project_id=project_id, db=db)
    policy_set_definitions: list[PolicySetDefinitions] = []
    ssp_raw = await oscal_service.get_ssp_by_project(project_id=project_id, db=db)
    ssp = ssp_raw.root.system_security_plan

    # Gather policy references from the security plan assigned to the project
    control_ids = set()
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
                control_ids.add(implemented_requirement.control_id.root)
                policy_set_definitions.append(
                    PolicySetDefinitions(
                        search_path=search_item,
                        contorl_id=implemented_requirement.control_id.root,
                        policy_ids=[p.value.root for p in azure_policies],
                    )
                )
                # policy_set_definitions.append((search_item, [p.value for p in azure_policies]))

    # Merge azure policies
    azure_policies_subset = list(
        filter(
            lambda x: x.search_path.plattform == CloudPlattform.AZURE,
            policy_set_definitions,
        )
    )
    azure_policies_subset = _merge_policy_sets(azure_policies_subset)

    # Create azure policy initiative
    for azure_policy_set in azure_policies_subset:
        match = re.fullmatch(get_rg_pattern(), azure_policy_set.search_path.path)
        policy_client_subscription_id = match.group("subscription_id")
        policy_client = PolicyClient(
            credential=credential, subscription_id=policy_client_subscription_id
        )

        policy_definitions: list[PolicyDefinitionReference] = [
            PolicyDefinitionReference(policy_definition_id=policy_id)
            for policy_id in azure_policy_set.policy_ids
        ]

        initiative_definition: PolicySetDefinition = PolicySetDefinition(
            display_name=f"ip5sgcgov project {str(project.name)} for search {str(azure_policy_set.search_path.id)}",
            description=f"ip5sgcgov project {str(project.name)} for search {str(azure_policy_set.search_path.id)}",
            policy_definitions=policy_definitions,
            metadata={
                "category": "ip5sgcgov-project",
                "ip5sgcgov-project-name": project.name,
                "ip5sgcgov-project-id": str(project.id),
                "ip5sgcgov-ssp-id": str(ssp.uuid.root),
                "ip5sgcgov-search-path": azure_policy_set.search_path.path,
                "ip5sgcgov-search-path-id": azure_policy_set.search_path.id,
            },
        )
        policy_set_definition_name = f"ip5sgcgov-{str(azure_policy_set.search_path.id)}"
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
                    'azure_paths.id': str(azure_policy_set.search_path.id)
                },
                {
                    '$addToSet': {
                        'azure_paths.$.plattform_policy_reference' : result.id
                    }
                }
            )

    # Create assessment-plan with pre-defined task for assingning policy initiatives
    updated_project = await project_service.get_project(project_id=project_id, db=db)
    assessment_plan_tasks: list[OscalCompleteOscalAssessmentCommonTask] = []
    # TODO create assessment plan and persist it
    # TODO run assessment plan -> create initiative assignment
    for path in updated_project.azure_paths:
        sub_tasks: list[OscalCompleteOscalAssessmentCommonTask] = []
        for policy_initiative_id in path.plattform_policy_reference:
            sub_tasks.append(
                OscalCompleteOscalAssessmentCommonTask(
                    uuid=str(uuid.uuid4()),
                    description="Policy iniative is assigned to project context",
                    title="Policy initiative assinged",
                    type=Type4.action,
                    props=[
                        OscalCompleteOscalMetadataProperty(
                            name=OscalPropertyIdentifier.CAC_TASK_TYPE.value,
                            value=CacTaskType.AZURE_DEPLOY_INITIATIVE.value
                        ),
                        OscalCompleteOscalMetadataProperty(
                            name=OscalPropertyIdentifier.AZURE_POLICY_INITIATIVE.value,
                            # TODO make this more generic instead of using first policy initiative
                            value=policy_initiative_id
                        )
                    ]
                )
            )
            sub_tasks.append(
                OscalCompleteOscalAssessmentCommonTask(
                    uuid=str(uuid.uuid4()),
                    description="Policy iniative is assigned to project context",
                    title="Policy in initaitve are conformant",
                    type=Type4.action,
                    props=[
                        OscalCompleteOscalMetadataProperty(
                            name=OscalPropertyIdentifier.CAC_TASK_TYPE.value,
                            value=CacTaskType.AZURE_CHECK_INITAITVE.value
                        ),
                        OscalCompleteOscalMetadataProperty(
                            name=OscalPropertyIdentifier.AZURE_POLICY_INITIATIVE.value,
                            # TODO make this more generic instead of using first policy initiative
                            value=policy_initiative_id
                        )
                    ]
                )
            )

            
        policy_initiative_task = OscalCompleteOscalAssessmentCommonTask(
            uuid=str(uuid.uuid4()),
            title=f"Ressources in {path.path} are check",
            description=f"Policy for ressourcen in {path.path} need to be compliant",
            type=Type4.action,
            props=[
                OscalCompleteOscalMetadataProperty(
                    uuid=str(uuid.uuid4()),
                    name=OscalPropertyIdentifier.CAC_TASK_TYPE.value,
                    value=CacTaskType.CAC_SEARCH_PATH_CHECK.value,
                )
            ],
            tasks=sub_tasks
        )
        assessment_plan_tasks.append(policy_initiative_task)


    creation_date = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    assessment_plan = OscalCompleteOscalApAssessmentPlan(
        uuid=str(uuid.uuid4()),
        import_ssp=OscalCompleteOscalAssessmentCommonImportSsp(
            href=str(ssp.uuid)
        ),
        metadata=OscalCompleteOscalMetadataMetadata(
            title=f"AP for {updated_project.name}",
            published=creation_date,
            last_modified=creation_date,
            version="0.1",
            oscal_version="1.1.3",
            props=[
                OscalCompleteOscalMetadataProperty(
                    name=OscalPropertyIdentifier.CAC_PROJECT_ID.value,
                    value=str(project_id)
                )
            ]
        ),
        tasks=assessment_plan_tasks,
        reviewed_controls=OscalCompleteOscalAssessmentCommonReviewedControls(
            control_selections=[
                ControlSelection(
                    include_controls=[
                        OscalCompleteOscalAssessmentCommonSelectControlById(
                            control_id=id
                        )
                        for id in control_ids
                    ]
                )
            ]
        )
    )

    ap = await db[MongoDBCollections.ASSESSMENT_PLANS.value].find_one_and_replace(
        filter={
            "assessment-plan.metadata.props": {
                "$elemMatch": {
                    "name": OscalPropertyIdentifier.CAC_PROJECT_ID.value,
                    "value": str(project_id)
                }
            }
        },
        projection={
            "_id":0
        },
        replacement=jsonable_encoder(Model5(assessment_plan=assessment_plan).model_dump(by_alias=True, exclude_none=True)),
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return Model5.model_validate(ap)

def _merge_policy_sets(
    policy_sets: list[PolicySetDefinitions],
) -> list[PolicySetDefinitions]:
    """
    Merge policy paths by same search query from which they originated
    """
    grouped: DefaultDict[str, list[PolicySetDefinitions]] = defaultdict(list)

    for policy in policy_sets:
        key = policy.search_path.id
        grouped[key].append(policy)

    merged = []
    for key, items in grouped.items():
        # Merge cloudPaths
        all_cloud_paths: list[str] = []
        for item in items:
            all_cloud_paths.extend(item.policy_ids)

        # Reuse one of the identical searchPaths
        merged.append(
            PolicySetDefinitions(
                search_path=items[0].search_path, policy_ids=all_cloud_paths, contorl_id=items[0].contorl_id
            )
        )

    return merged
