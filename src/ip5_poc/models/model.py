from enum import Enum, StrEnum
from uuid import UUID
import uuid
from pydantic import BaseModel, ConfigDict
from azure.mgmt.resource.resources.models import GenericResourceExpanded
from pydantic import BaseModel, SerializationInfo, field_serializer

class CloudPlattform(StrEnum):
    AWS='aws'
    AZURE='azure'

class CloudPlattformPath(BaseModel):
    id: UUID
    path: str
    plattform: CloudPlattform
    plattform_policy_reference: list[str] = []

    # model_config = ConfigDict(use_enum_values=True)

class ProjectContextRequest(BaseModel):
    name: str
    aws_paths: list[str] = []
    azure_paths: list[str] = []

class ProjectContext(BaseModel):
    id: UUID
    name: str
    aws_paths: list[CloudPlattformPath] = []
    azure_paths: list[CloudPlattformPath] = []
    model_config = ConfigDict(frozen=True)

class CloudRessource(BaseModel):
    plattform: CloudPlattform

    model_config = ConfigDict(use_enum_values=True)

class AzureCloudRessource(CloudRessource):
    plattform: CloudPlattform = CloudPlattform.AZURE
    ressource: GenericResourceExpanded
    search_basis: CloudPlattformPath

    @field_serializer('ressource')
    def handle_ressource(self, v: GenericResourceExpanded):
        return v.as_dict()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # class Config:
    #     arbitrary_types_allowed = True

class MongoDBCollections(Enum):
    CATALOGS='catalogs'
    COMPONENT_DEFINITIONS='component-definitions'
    PROJECTS='projects'
    SYSTEM_SECURITY_PLANS='ssps'

class OscalPropertyIdentifier(Enum):
    AZURE_REGION='azure-region'
    AZURE_POLICY='azure-policy'
    AZURE_RESOURCE_TYPE='azure-resource-type'
    AZURE_RESOURCE_ID='azure-resource-id'
    OSCAL_DERIVED_COMPONENT_DEFINITION_UUID='oscal-derived-component-definition-uuid'
    OSCAL_DERIVED_COMPONENT_UUID='oscal-derived-component-uuid'
    CAC_PROJECT_ID='cac-project-id'
    CAC_PROJECT_SEARCH_ID='cac-project-serach-id'
    CAC_PROJECT_TYPE='cac-plattform-type'
    CAC_PLATTFORM_TYPE='cac-plattform-type'