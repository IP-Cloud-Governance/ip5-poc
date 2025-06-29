from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ip5_poc.core.dependencies import get_api_key, get_az_credentials, get_db
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import PolicyClient
from ip5_poc.models.model import CloudPlattform, CloudPlattformPath, OscalPropertyIdentifier
from ip5_poc.services import project_service,oscal_service
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

trigger_router = APIRouter(prefix="/triggers", tags=["Manual triggering"], dependencies=[Depends(get_api_key)])

logger = logging.getLogger(__name__)


@trigger_router.post(
    "/projects/{project_id}/deploy",
    name="Deploy policies according to project context information",
)
async def deploy_policies(
    project_id: UUID,
    credential: DefaultAzureCredential = Depends(get_az_credentials),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    project = await project_service.get_project(project_id=project_id, db=db)
    policy_set_definitions: list[tuple[CloudPlattformPath, list[str]]] = []
    ssp_raw = await oscal_service.get_ssp_by_project(project_id=project_id, db=db)
    ssp = ssp_raw.root.system_security_plan
    
    # Gather policy references from the security plan assigned to the project
    for implemented_requirement in ssp.control_implementation.implemented_requirements:
        if len(implemented_requirement.by_components) is 0:
            raise HTTPException(status_code=500, detail=f"Implemented requirement for {implemented_requirement.control_id}|{implemented_requirement.uuid} should at least contain one by-component")
        # TODO make this more generic. Theoretically one requirement can be implemented by multiple components -> should be combined into single policy
        implemented_component = implemented_requirement.by_components[0]
        component = next((c for c in ssp.system_implementation.components if implemented_component.component_uuid == c.uuid), None)
        if component is None:
            raise HTTPException(status_code=500, detail=f"No mathching component in system_implementation for {implemented_component.component_uuid}")
        logger.info(component.model_dump_json())
        search_id = next((p for p in component.props if p.name.root == OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value), None)
        plattform_type = next((p for p in component.props if p.name.root == OscalPropertyIdentifier.CAC_PLATTFORM_TYPE.value), None)
        if plattform_type is None:
            raise HTTPException(status_code=500, detail=f"Component doesnt has an cac plattform type bound to it via {OscalPropertyIdentifier.CAC_PLATTFORM_TYPE.value}")
        if search_id is None:
            raise HTTPException(status_code=500, detail=f"Component doesnt has an cac search id bound to it via {OscalPropertyIdentifier.CAC_PROJECT_SEARCH_ID.value}")

        # TODO support different plattforms as well
        if plattform_type.value.root == CloudPlattform.AZURE.value:
            search_item = next((p for p in project.azure_paths if p.plattform.value == CloudPlattform.AZURE.value and str(p.id) == search_id.value.root), None)
            if search_item is None:
                raise HTTPException(status_code=500, detail=f"Search id {search_id.value.root} should be part of the project {project.id} but isnt (anymore)")
            # Retrieve policies from ssp
            # TODO this check is here because there might by requirements where not policy is set -> t6.1
            if implemented_requirement.props:
                azure_policies = list(filter(lambda x: x.name.root == OscalPropertyIdentifier.AZURE_POLICY.value, implemented_requirement.props))
                policy_set_definitions.append((search_item, [p.value for p in azure_policies]))
            

    # Merge azure policies
    azure_policies_subset = list(filter(lambda x: x[0].plattform == CloudPlattform.AZURE, policy_set_definitions))

    # TODO CONTINUE HERE with merging policies of azure_policies_subset together to get one search path and all policies
    # then create a initiaite and deploy it for the scope set in the serach path
    return list(filter(lambda x: x[0].plattform == CloudPlattform.AZURE, policy_set_definitions))