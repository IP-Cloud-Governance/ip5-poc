from uuid import UUID
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from azure.identity import DefaultAzureCredential
from ip5_poc.models.generated_oscal_model import Model5
from ip5_poc.models.model import AzurePolicyDefinition, MongoDBCollections, OscalPropertyIdentifier, ProjectContext
from ip5_poc.services.azure_service import get_subscription_id_from_path
from azure.mgmt.resource import PolicyClient
import logging
import re

logger = logging.getLogger(__name__)

async def get_project(project_id: UUID, db: AsyncIOMotorDatabase) -> ProjectContext:
    project = await db[MongoDBCollections.PROJECTS.value].find_one({"id": str(project_id)}, {"_id": 0})
    if project is None:
        raise HTTPException(
            status_code=404, detail=f"Project with id {str(project_id)} not found"
        )
    return ProjectContext.model_validate(project)


async def delete_project(project_id: UUID, db: AsyncIOMotorDatabase, credential: DefaultAzureCredential):
    project = await get_project(project_id=project_id, db=db)
    logging.info(f"Deleting content related to project {project.name}")

    # TODO Currently only treating azure paths
    for azure_path in project.azure_paths:
        # Deleting azure assignments and policy definitions
        policy_docs = db[MongoDBCollections.POLICY_DEFINITIONS.value].find(
            {"search_id" : str(azure_path.id)}
        )
        async for policy_doc in policy_docs:
            policy = AzurePolicyDefinition.model_validate(policy_doc)
            if not policy.assignment:
                continue
            assignment_id = policy.assignment.id
            policy_definition_id = policy.id
            logger.info(f"Try deleting policy assignment with id {assignment_id}")
            subscription_id = get_subscription_id_from_path(path=azure_path.path)
            if subscription_id is None:
                continue
            policy_client = PolicyClient(
                credential=credential, subscription_id=subscription_id
            )
            policy_client.policy_assignments.delete_by_id(
                policy_assignment_id=assignment_id
            )
            logger.info(f"Deleted policy assignment with id {assignment_id} successfully")

            logger.info(f"Extrating policy_name from {policy_definition_id}")
            match = re.search(r"\/(?P<last_segment>ip5sgcgov-[a-z0-9\-]+-[a-z0-9\-\.]+)$", policy_definition_id)
            if not match:
                logger.info(f"Policy definition id seems to be invalid ... couldn't extract policy definition name")

            policy_definition_name =  match.group("last_segment")

            logger.info(f"Trying to delete the policy definition name {policy_definition_name}")
            policy_client.policy_set_definitions.delete(
                policy_set_definition_name=policy_definition_name,
            )
            logger.info(f"Deleted policy with name {policy_definition_name} successfully")
        
    # Delete policy definitions object
    policy_docs = await db[MongoDBCollections.POLICY_DEFINITIONS.value].delete_many(
        {"search_id": str(azure_path.id)}
    )

    # Get assessent plan to delete assessment plan results
    ap = await db[MongoDBCollections.ASSESSMENT_PLANS.value].find_one(
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
        }
    )
    if ap:
        ap = Model5.model_validate(ap).assessment_plan
        logger.info(f"Assessment plan found with id {ap.uuid.root}")
        # Delete assessment plan results
        logger.info(f"Trying to delete assessment plan result for ap {ap.uuid.root}")
        await db[MongoDBCollections.ASSESSMENT_RESULTS.value].delete_many(
            {"assessment-results.import-ap.href": ap.uuid.root},
        )

        logger.info("Trying to delete assessment plan itself with id {ap.uuid.root}")
        await db[MongoDBCollections.ASSESSMENT_PLANS.value].delete_many(
            filter={
                "assessment-plan.metadata.props": {
                    "$elemMatch": {
                        "name": OscalPropertyIdentifier.CAC_PROJECT_ID.value,
                        "value": str(project_id)
                    }
                }
            }
        )
    
    logger.info(f"Trying to delete system security plan for project {project.name}")
    await db[MongoDBCollections.SYSTEM_SECURITY_PLANS.value].delete_many(
        {"system-security-plan.system-characteristics.system-ids.id": str(project_id)}
    )

    logger.info(f"Trying to delete project itself with name {project.name}")
    await db[MongoDBCollections.PROJECTS.value].delete_one(
        {"id": str(project_id)}
    )

    logger.info(f"Finished deleting content for project {project.name}")