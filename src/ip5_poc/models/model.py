from enum import Enum
from pydantic import BaseModel
from azure.mgmt.resource.resources.models import GenericResourceExpanded
from pydantic import BaseModel, SerializationInfo, field_serializer


class ProjectContext(BaseModel):
    name: str
    aws_paths: list[str] = []
    azure_paths: list[str] = []

class CloudPlattform(Enum):
    AWS='aws'
    AZURE='azure'

class CloudRessource(BaseModel):
    plattform: CloudPlattform

class AzureCloudRessource(CloudRessource):
    plattform: CloudPlattform = CloudPlattform.AZURE
    ressource: GenericResourceExpanded

    @field_serializer('ressource')
    def handle_ressource(self, v: GenericResourceExpanded):
        return v.as_dict()

    class Config:
        arbitrary_types_allowed = True