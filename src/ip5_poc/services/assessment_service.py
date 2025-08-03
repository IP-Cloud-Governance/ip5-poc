from collections import defaultdict
from datetime import datetime, timezone
from typing import DefaultDict
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from ip5_poc.core.dependencies import get_az_credentials, get_db
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import PolicyClient
from azure.mgmt.policyinsights import PolicyInsightsClient
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource.policy.models import (
    PolicyDefinitionReference,
    PolicySetDefinition,
    PolicyAssignment,
    ParameterValuesValue
)
from azure.mgmt.policyinsights.models import QueryOptions
from ip5_poc.models.generated_oscal_model import (
    AssessmentLog,
    ControlSelection,
    Entry1,
    Model,
    Model5,
    Model6,
    OscalCompleteOscalApAssessmentPlan,
    OscalCompleteOscalArAssessmentResults,
    OscalCompleteOscalArImportAp,
    OscalCompleteOscalAssessmentCommonFinding,
    OscalCompleteOscalAssessmentCommonFindingTarget,
    OscalCompleteOscalAssessmentCommonImportSsp,
    OscalCompleteOscalAssessmentCommonReviewedControls,
    OscalCompleteOscalAssessmentCommonSelectControlById,
    OscalCompleteOscalAssessmentCommonTask,
    OscalCompleteOscalMetadataMetadata,
    OscalCompleteOscalMetadataOscalVersion,
    OscalCompleteOscalMetadataProperty,
    OscalCompleteOscalMetadataVersion,
    Status1,
    Type4,
    OscalCompleteOscalArResult,
    ControlSelection,
    OscalCompleteOscalAssessmentCommonSelectControlById
)
from ip5_poc.models.model import (
    AzurePolicyDefinition,
    AzurePolicyDefinitionAssignment,
    CacTaskType,
    CloudPlattform,
    MongoDBCollections,
    OscalControlComplianceState,
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

from ip5_poc.services.azure_service import get_rg_pattern, get_subscription_id_from_path, get_subscription_pattern


logger = logging.getLogger(__name__)


async def create_assessment(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    project = await project_service.get_project(project_id=project_id, db=db)
    assessment_plan = (
        await oscal_service.get_assessment_plan_by_project(project_id=project_id, db=db)
    ).root.assessment_plan

    assessment_log_entries: list[Entry1] = []

    include_controls: list[OscalCompleteOscalAssessmentCommonSelectControlById] = []
    findings: list[OscalCompleteOscalAssessmentCommonFinding] = []


    # Check for azure deploy tasks
    deploy_tasks = _get_tasks_of_type(
        tasks=assessment_plan.tasks,
        task_type=CacTaskType.AZURE_DEPLOY_INITIATIVE.value,
    )
    for deploy_task in deploy_tasks:
        search_id = next(
            (
                prop.value.root
                for prop in deploy_task.props
                if prop.name.root
                == OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value
            ),
            None,
        )
        policy_initative_id = next(
            (
                prop.value.root
                for prop in deploy_task.props
                if prop.name.root
                == OscalPropertyIdentifier.AZURE_POLICY_INITIATIVE.value
            ),
            None,
        )
        if search_id is None or policy_initative_id is None:
            logger.info(
                f"The taks of type {CacTaskType.AZURE_DEPLOY_INITIATIVE.value} doensn't contain a search id {search_id} or policy initiative id {policy_initative_id} and therefore skipped"
            )
            continue
        azure_path = next(
            (path for path in project.azure_paths if str(path.id) == search_id),
            None,
        )
        if azure_path is None:
            logger.info(
                f"No serach path with id {search_id} was found in project {project_id}. Application of policy {policy_initative_id} is therfore skipped"
            )

        subscription_id = get_subscription_id_from_path(path=azure_path.path)
        if subscription_id is None:
            continue
        policy_client = PolicyClient(
            credential=credential, subscription_id=subscription_id
        )
        policy_definition = await db[
            MongoDBCollections.POLICY_DEFINITIONS.value
        ].find_one({"id": policy_initative_id}, {"_id": 0})
        if policy_definition is None:
            assessment_log_entries.append(_create_assessment_log_entry(title="Policy definition not found", description=f"Policy definition with id {policy_initative_id} not found in internal and therefore skipped policy assignment based on search id {search_id}"))
            logger.info(
                f"Policy definition with id {policy_initative_id} not found in internal and therefore skipped policy assignment based on search id {search_id} "
            )
            continue
        policy_definition = AzurePolicyDefinition.model_validate(policy_definition)

        if policy_definition.assignment_ids:
            try:
                policy_client.policy_assignments.get_by_id(
                    policy_assignment_id=policy_definition.assignment_ids[0]
                )
                logger.info(f"Policy with id {policy_initative_id} HAS been assinged. Skipping policy assignment")
                continue
            except HttpResponseError:
                logger.info(f"Policy with id {policy_initative_id} has not been assinged yet")


        assignment = policy_client.policy_assignments.create(
            scope=azure_path.path,
            policy_assignment_name=f"assignment-{policy_definition.name}",
            parameters=PolicyAssignment(
                policy_definition_id=policy_initative_id,
                display_name=f"assignment-{policy_definition.name}",
                metadata=policy_definition.metadata,
            ),
        )
        assessment_log_entries.append(_create_assessment_log_entry(title="Assignt azure policy initiative", description=f"Assigned initaitve {assignment.name} to scope {assignment.scope}"))

        logger.info(
            f"Policy definition with id {policy_initative_id} has been updated with id {assignment.id}"
        )
        await db[MongoDBCollections.POLICY_DEFINITIONS.value].update_one(
            {"id": policy_initative_id},
            {"$set": {"assignment": AzurePolicyDefinitionAssignment(id=assignment.id,name=assignment.name).model_dump(exclude_unset=True)}},
        )

    check_tasks = _get_tasks_of_type(
        tasks=assessment_plan.tasks, task_type=CacTaskType.AZURE_CHECK_INITAITVE.value
    )
    reviewed_controls_id: list[str] = []
    findings: list[OscalCompleteOscalAssessmentCommonFinding] = []
    for check_task in check_tasks:
            search_id = next(
                (
                    prop.value.root
                    for prop in check_task.props
                    if prop.name.root
                    == OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value
                ),
                None,
            )
            control_id = next(
                (
                    prop.value.root
                    for prop in check_task.props
                    if prop.name.root
                    == OscalPropertyIdentifier.OSCAL_CONTROL_ID.value
                ),
                None,
            )
            component_id = next(
                (
                    prop.value.root
                    for prop in check_task.props
                    if prop.name.root
                    == OscalPropertyIdentifier.OSCAL_COMPONENT_ID.value
                ),
                None,
            )
            azure_resource_id = next(
                (
                    prop.value.root
                    for prop in check_task.props
                    if prop.name.root
                    == OscalPropertyIdentifier.AZURE_RESOURCE_ID.value
                ),
                None,
            )
            azure_policy_id = next(
                (
                    prop.value.root
                    for prop in check_task.props
                    if prop.name.root
                    == OscalPropertyIdentifier.AZURE_POLICY.value
                ),
                None,
            )
            if search_id is None or control_id is None or component_id is None or azure_resource_id is None or azure_policy_id is None:
                logger.info(
                    f"The taks of type {CacTaskType.AZURE_DEPLOY_INITIATIVE.value} doensn't contain a search id {search_id} or control id {control_id} and therefore skipped"
                )
                continue
            azure_path = next(
                (path for path in project.azure_paths if str(path.id) == search_id),
                None,
            )
            if azure_path is None:
                logger.info(
                    f"No serach path with id {search_id} was found in project {project_id}. Check of control_id {control_id} is therfore skipped"
                )
        

            rg_match = re.fullmatch(get_rg_pattern(), azure_path.path)
            subscription_match = re.fullmatch(get_subscription_pattern(), azure_path.path)
            if rg_match:
                subscription_id = rg_match.group("subscription_id")
                rg_name = rg_match.group("resource_group")
            elif subscription_match:
                subscription_id = subscription_match.group("subscription_id")
            else:
                continue

            policy_insights_client = PolicyInsightsClient(
                credential=credential, subscription_id=subscription_id
            )

            policy_definition = await db[
                MongoDBCollections.POLICY_DEFINITIONS.value
            ].find_one({"control_id": control_id, "search_id": search_id}, {"_id": 0})
            
            if policy_definition is None:
                logger.info(f"No policy definition was found with id {policy_initative_id}. Has it already been assigned?")
                continue

            policy_definition = AzurePolicyDefinition.model_validate(policy_definition)

            if policy_definition.assignment is None:
                logger.info(f"No assignment has been found for the policy initiative {policy_definition.id}")
                continue
            
            # for component in azure_components:
            logger.info(f"Check policy compliance for ressource {component_id}")

            # TODO This doesnt really makes sense .. because not every component needs to be checked for each policy
            # Luckily currenlty azure returns empty result when a policy is not assinged
            policy_compliance = policy_insights_client.policy_states.list_query_results_for_resource(
                resource_id=azure_resource_id,
                policy_states_resource="latest",
                query_options=QueryOptions(
                    filter=f"PolicyAssignmentId eq '{policy_definition.assignment.id}'"
                )
            )

            non_compliant = any(r.compliance_state == 'NonCompliant' for r in policy_compliance)
            logger.info(f"non_compliant is {non_compliant}")
            include_controls.append(
                OscalCompleteOscalAssessmentCommonSelectControlById(
                    control_id=policy_definition.control_id,
                )
            )


            # TODO check if new pocliy definition per contorl id have been created ... then check based on these policy deifnition
            reviewed_controls_id.append(control_id)
            if non_compliant:
                findings.append(
                    OscalCompleteOscalAssessmentCommonFinding(
                        uuid=str(uuid.uuid4()),
                        props=[
                            OscalCompleteOscalMetadataProperty(
                                name=OscalPropertyIdentifier.OSCAL_CONTROL_COMPLIANCE_STATE.value,
                                value=OscalControlComplianceState.NON_COMPLIANT.value
                            ),
                            OscalCompleteOscalMetadataProperty(
                                name=OscalPropertyIdentifier.OSCAL_COMPONENT_ID.value,
                                value=component_id
                            )
                        ],
                        target=OscalCompleteOscalAssessmentCommonFindingTarget(
                            target_id=f"component-{component_id}",
                            status=Status1(
                                state=OscalControlComplianceState.NON_COMPLIANT.value
                            ),
                            type=OscalPropertyIdentifier.OSCAL_COMPONENT_ID.value
                        ),
                        title=f"Control {component_id} is 'not compliant' to control_id {control_id} in reguards of policy {azure_policy_id}",
                        description=f"Control {component_id} is 'not compliant' to control_id {control_id} in reguards of policy {azure_policy_id}"
                    )
                )
                assessment_log_entries.append(_create_assessment_log_entry(title=f"Analyzed ressource {component_id} is not compliant", description=f"Ressource with id {policy_definition.assignment.id} is not compliant to policy {policy_definition.assignment.id}"))
            else:
                findings.append(
                    OscalCompleteOscalAssessmentCommonFinding(
                        uuid=str(uuid.uuid4()),
                        props=[
                            OscalCompleteOscalMetadataProperty(
                                name=OscalPropertyIdentifier.OSCAL_CONTROL_COMPLIANCE_STATE.value,
                                value=OscalControlComplianceState.COMPLIANT.value
                            ),
                            OscalCompleteOscalMetadataProperty(
                                name=OscalPropertyIdentifier.OSCAL_COMPONENT_ID.value,
                                value=component_id
                            )
                        ],
                        target=OscalCompleteOscalAssessmentCommonFindingTarget(
                            target_id=f"component-{component_id}",
                            status=Status1(
                                state=OscalControlComplianceState.COMPLIANT.value
                            ),
                            type=OscalPropertyIdentifier.OSCAL_COMPONENT_ID.value
                        ),
                        title=f"Control {component_id} is 'compliant' to control_id {control_id} in reguards of policy {azure_policy_id}",
                        description=f"Control {component_id} is 'compliant' to control_id {control_id} in reguards of policy {azure_policy_id}"
                    )
                )
                assessment_log_entries.append(_create_assessment_log_entry(title=f"Analyzed ressource {component_id} is compliant", description=f"Ressource with id {policy_definition.assignment.id} is compliant to policy {policy_definition.assignment.id}"))


            logger.info(f"Getting summary for policy definition name {policy_definition}")


    
    # TODO store the assessment result
    # assessment_results = OscalCompleteOscalArAssessmentResults()
    assessment_result = OscalCompleteOscalArResult(
        uuid=str(uuid.uuid4()),
        title=f"Assessment for project {str(project.id)}",
        description=f"Assessment for project {str(project.id)}",
        findings=findings,
        start=datetime.now(timezone.utc),
        end=datetime.now(timezone.utc),
        assessment_log=AssessmentLog(
            entries=assessment_log_entries
        ),
        reviewed_controls=OscalCompleteOscalAssessmentCommonReviewedControls(
            control_selections=[
                ControlSelection(
                    include_controls=[OscalCompleteOscalAssessmentCommonSelectControlById(control_id=c) for c in reviewed_controls_id]
                )
            ]
        )
    )

    existing_assessment_result = await db[
        MongoDBCollections.ASSESSMENT_RESULTS.value
    ].find_one({"assessment-results.import-ap.href": assessment_plan.uuid.root})
    
    if existing_assessment_result:
        logger.info(f"Assessment result already found for plan {assessment_plan.uuid.root}. Add result to existing result set")
        updated_ap = await db[
            MongoDBCollections.ASSESSMENT_RESULTS.value
        ].find_one_and_update(
            filter={"assessment-results.import-ap.href": assessment_plan.uuid.root},
            update={"$push":{"assessment-results.results":jsonable_encoder(assessment_result.model_dump(by_alias=True, exclude_none=True))}},
            projection={"_id":0},
            return_document=ReturnDocument.AFTER
        )
        return Model.model_validate(updated_ap).model_dump(by_alias=True, exclude_none=True)
    else:
        logger.info(f"No assessment result there yet, creating new assessment result for assessment plan {assessment_plan.uuid.root}")
        new_ap = Model6(
                assessment_results=OscalCompleteOscalArAssessmentResults(
                        uuid=str(uuid.uuid4()),
                        import_ap=OscalCompleteOscalArImportAp(
                            href=assessment_plan.uuid.root
                        ),
                        metadata=OscalCompleteOscalMetadataMetadata(
                            title=f"Assesment plan for project {project_id}",
                            version=OscalCompleteOscalMetadataVersion(root="1.0"),
                            oscal_version=OscalCompleteOscalMetadataOscalVersion(root="1.1.3"),
                            last_modified=datetime.now(timezone.utc),
                        ),
                        results=[
                            assessment_result
                        ]
                    )
        ).model_dump(by_alias=True, exclude_none=True)
        await db[
            MongoDBCollections.ASSESSMENT_RESULTS.value
        ].insert_one(
            jsonable_encoder(new_ap)
        )
        return new_ap

def _create_assessment_log_entry(title: str, description: str = "") -> Entry1:
    return Entry1(
        start=datetime.now(timezone.utc),
        end=datetime.now(timezone.utc),
        uuid=str(uuid.uuid4()),
        title=title,
        description=description
    )


def _get_tasks_of_type(
    tasks: list[OscalCompleteOscalAssessmentCommonTask], task_type: str
) -> list[OscalCompleteOscalAssessmentCommonTask]:
    return [
        t
        for t in tasks
        if any(
            p.name.root == OscalPropertyIdentifier.CAC_TASK_TYPE.value
            and p.value.root == task_type
            for p in t.props
        )
    ]


async def create_policies_and_assessment_plan(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Model5:
    """
    Deploys the policy in the system secruity plan of a project to the cloud plattform.
    For azure that means that a policy initiative is created in the project context
    """
    project = await project_service.get_project(project_id=project_id, db=db)
    policy_set_definitions: list[PolicySetDefinitions] = []
    ssp_raw = await oscal_service.get_ssp_by_project(project_id=project_id, db=db)
    ssp = ssp_raw.root.system_security_plan
    assessment_plan_tasks: list[OscalCompleteOscalAssessmentCommonTask] = []

    # Gather policy references from the security plan assigned to the project
    control_ids = set()
    sub_tasks: list[OscalCompleteOscalAssessmentCommonTask] = []

    for implemented_requirement in ssp.control_implementation.implemented_requirements:
        if len(implemented_requirement.by_components) is 0:
            raise HTTPException(
                status_code=500,
                detail=f"Implemented requirement for {implemented_requirement.control_id}|{implemented_requirement.uuid} should at least contain one by-component",
            )

        for implemented_component in implemented_requirement.by_components:
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


                az_resource_id = next(
                    (
                        p
                        for p in component.props
                        if p.name.root == OscalPropertyIdentifier.AZURE_RESOURCE_ID.value
                    ),
                    None,
                )
                if az_resource_id is None:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Azure resource id is not defined for component {component.title}",
                    )

                # This check is here because there might by requirements where not policy is set -> t6.1
                if implemented_requirement.props:
                    azure_policies: list[str] = [prop.value.root for prop in implemented_requirement.props if prop.name.root == OscalPropertyIdentifier.AZURE_POLICY.value]
                    control_ids.add(implemented_requirement.control_id.root)

                    for azure_policy_id in azure_policies:
                        sub_tasks.append(
                            # Task to check if the azure policy is conformat ... application is achieved trough azure policy initiative
                            OscalCompleteOscalAssessmentCommonTask(
                                uuid=str(uuid.uuid4()),
                                description=f"Ressource {az_resource_id.value.root} with component id {component.uuid.root} is conformant to control id {implemented_requirement.control_id.root}",
                                title="Policy in initaitve are conformant",
                                type=Type4.action,
                                props=[
                                    OscalCompleteOscalMetadataProperty(
                                        name=OscalPropertyIdentifier.AZURE_RESOURCE_ID.value,
                                        value=az_resource_id.value.root,
                                    ),
                                    OscalCompleteOscalMetadataProperty(
                                        name=OscalPropertyIdentifier.CAC_TASK_TYPE.value,
                                        value=CacTaskType.AZURE_CHECK_INITAITVE.value,
                                    ),
                                    OscalCompleteOscalMetadataProperty(
                                        name=OscalPropertyIdentifier.OSCAL_CONTROL_ID.value,
                                        value=implemented_requirement.control_id.root,
                                    ),
                                    OscalCompleteOscalMetadataProperty(
                                        name=OscalPropertyIdentifier.AZURE_POLICY.value,
                                        value=azure_policy_id,
                                    ),
                                    OscalCompleteOscalMetadataProperty(
                                        name=OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value,
                                        value=str(search_item.id),
                                    ),
                                    OscalCompleteOscalMetadataProperty(
                                        name=OscalPropertyIdentifier.OSCAL_COMPONENT_ID.value,
                                        value=str(component.uuid.root),
                                    )
                                ]
                            )
                        )
                    policy_set_definitions.append(
                        PolicySetDefinitions(
                            search_path=search_item,
                            contorl_id=implemented_requirement.control_id.root,
                            policy_ids=[p for p in azure_policies],
                        )
                    )

    # Merge azure policies
    azure_policies_subset = list(
        filter(
            lambda x: x.search_path.plattform == CloudPlattform.AZURE,
            policy_set_definitions,
        )
    )
    logger.info("ALL AZURE POLICIES")
    logger.info(azure_policies_subset)

    # Create azure policy initiative
    for azure_policy_set in azure_policies_subset:
        policy_client_subscription_id = get_subscription_id_from_path(
            path=azure_policy_set.search_path.path
        )

        if policy_client_subscription_id is None:
            continue

        policy_client = PolicyClient(
            credential=credential, subscription_id=policy_client_subscription_id
        )

        policy_definitions: list[PolicyDefinitionReference] = [
            PolicyDefinitionReference(policy_definition_id=policy_id)
            for policy_id in azure_policy_set.policy_ids
        ]

        initiative_definition: PolicySetDefinition = PolicySetDefinition(
            display_name=f"ip5sgcgov  {str(project.name)} for control {str(azure_policy_set.contorl_id)}",
            description=f"ip5sgcgov {str(project.name)} for search {str(azure_policy_set.contorl_id)}",
            policy_definitions=policy_definitions,
            metadata={
                "category": "ip5sgcgov-project",
                "ip5sgcgov-project-id": str(project.id),
                "ip5sgcgov-search-path-id": azure_policy_set.search_path.id,
                "ip5sgcgov-contorl-id": azure_policy_set.contorl_id
            },
        )
        policy_set_definition_name = f"ip5sgcgov-{str(azure_policy_set.search_path.id)}-{azure_policy_set.contorl_id}"
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

        logger.info(f"Insert/Update stored policy definition with id {result.id}")
        await db[MongoDBCollections.POLICY_DEFINITIONS.value].find_one_and_replace(
            filter={"id": result.id},
            replacement=AzurePolicyDefinition(
                id=result.id,
                metadata=result.metadata,
                name=result.name,
                control_id=azure_policy_set.contorl_id,
                search_id=str(azure_policy_set.search_path.id),
                plattform=CloudPlattform.AZURE,
            ).model_dump(by_alias=True, exclude_none=True),
            upsert=True,
        )

        if result:
            logger.info(f"Created/updated policy with id {result.id}")

            # Update project context with policy initiative id if not already exitsing
            await db[MongoDBCollections.PROJECTS.value].update_one(
                {
                    "id": str(project_id),
                    "azure_paths.id": str(azure_policy_set.search_path.id),
                },
                {"$addToSet": {"azure_paths.$.plattform_policy_reference": result.id}},
            )

    # Create assessment-plan with pre-defined task for assingning policy initiatives
    updated_project = await project_service.get_project(project_id=project_id, db=db)

    for path in updated_project.azure_paths:
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
                            value=CacTaskType.AZURE_DEPLOY_INITIATIVE.value,
                        ),
                        OscalCompleteOscalMetadataProperty(
                            name=OscalPropertyIdentifier.AZURE_POLICY_INITIATIVE.value,
                            # TODO make this more generic instead of using first policy initiative
                            value=policy_initiative_id,
                        ),
                        OscalCompleteOscalMetadataProperty(
                            name=OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value,
                            value=str(path.id),
                        ),
                    ],
                )
            )

    creation_date = (
        datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    )
    assessment_plan = OscalCompleteOscalApAssessmentPlan(
        uuid=str(uuid.uuid4()),
        import_ssp=OscalCompleteOscalAssessmentCommonImportSsp(href=str(ssp.uuid.root)),
        metadata=OscalCompleteOscalMetadataMetadata(
            title=f"AP for {updated_project.name}",
            published=creation_date,
            last_modified=creation_date,
            version="0.1",
            oscal_version="1.1.3",
            props=[
                OscalCompleteOscalMetadataProperty(
                    name=OscalPropertyIdentifier.CAC_PROJECT_ID.value,
                    value=str(project_id),
                )
            ],
        ),
        tasks=sub_tasks,
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
        ),
    )

    ap = await db[MongoDBCollections.ASSESSMENT_PLANS.value].find_one_and_replace(
        filter={
            "assessment-plan.metadata.props": {
                "$elemMatch": {
                    "name": OscalPropertyIdentifier.CAC_PROJECT_ID.value,
                    "value": str(project_id),
                }
            }
        },
        projection={"_id": 0},
        replacement=jsonable_encoder(
            Model5(assessment_plan=assessment_plan).model_dump(
                by_alias=True, exclude_none=True
            )
        ),
        upsert=True,
        return_document=ReturnDocument.AFTER,
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
                search_path=items[0].search_path,
                policy_ids=all_cloud_paths,
                contorl_id=items[0].contorl_id,
            )
        )

    return merged
