from typing import Iterable
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import (
    AzureCloudRessource,
    AzurePolicyDefinition,
    CloudPlattformPath,
)
from azure.mgmt.policyinsights import PolicyInsightsClient
from azure.mgmt.policyinsights.models import QueryOptions
from azure.mgmt.policyinsights.models import PolicyStatesQueryResults
from azure.mgmt.resource.policy.models import (
    PolicySetDefinition,
    PolicyAssignment,
)
from azure.mgmt.resource import PolicyClient
import re
import logging

logger = logging.getLogger(__name__)


def get_subscription_pattern() -> str:
    return r"^/subscriptions/(?P<subscription_id>[0-9a-fA-F-]{36})$"


def get_rg_pattern() -> str:
    return r"^/subscriptions/(?P<subscription_id>[0-9a-fA-F-]{36})/resourceGroups/(?P<resource_group>[^/]+)$"


def get_az_ressources(
    azure_paths: list[CloudPlattformPath], az_credential: DefaultAzureCredential
) -> list[AzureCloudRessource]:
    """
    Retrieve ressources based on project configuration
    """
    all_ressources: list[AzureCloudRessource] = []

    # Retrieve ressources of subscription
    subscription_pattern = get_subscription_pattern()
    rg_pattern = get_rg_pattern()

    # Lookup ressources from azure
    for path in azure_paths:
        subscription_match = re.fullmatch(subscription_pattern, path.path)
        rg_match = re.fullmatch(rg_pattern, path.path)
        logger.info(f"search in azure for {path.path}")
        if subscription_match:
            # Retrieve ressources of subscription
            subscription_id = subscription_match.group("subscription_id")
            client = ResourceManagementClient(az_credential, subscription_id)
            all_ressources += [
                AzureCloudRessource(ressource=r, search_basis=path)
                for r in client.resources.list()
            ]
        elif rg_match:
            # Retrieve groups of of subscription
            subscription_id = rg_match.group("subscription_id")
            rg_name = rg_match.group("resource_group")
            client = ResourceManagementClient(az_credential, subscription_id)
            all_ressources += [
                AzureCloudRessource(ressource=r, search_basis=path)
                for r in client.resources.list_by_resource_group(rg_name)
            ]

    all_ressources.sort(key=lambda x: x.ressource.id)

    # Unique resources / without duplicates
    return list({res.ressource.id: res for res in all_ressources}.values())


def get_subscription_id_from_path(path: str) -> str | None:
    rg_match = re.fullmatch(get_rg_pattern(), path)
    subscription_match = re.fullmatch(get_subscription_pattern(), path)
    if rg_match:
        return rg_match.group("subscription_id")
    elif subscription_match:
        return subscription_match.group("subscription_id")
    else:
        logger.info(f"No azure subscription id was found in the path {path}")
        return None


def get_policy_results_for_project(
    az_credential: DefaultAzureCredential,
    policy_definition: AzurePolicyDefinition,
    azure_resource_id: str,
    subscription_id: str,
) -> Iterable[PolicyStatesQueryResults]:
    policy_insights_client = PolicyInsightsClient(
        credential=az_credential, subscription_id=subscription_id
    )
    return policy_insights_client.policy_states.list_query_results_for_resource(
        resource_id=azure_resource_id,
        policy_states_resource="latest",
        query_options=QueryOptions(
            filter=f"PolicyAssignmentId eq '{policy_definition.assignment.id}'"
        ),
    )


def get_assignment_by_id(
    az_credential: DefaultAzureCredential,
    subscription_id: str,
    policy_definition: AzurePolicyDefinition,
):
    policy_client = PolicyClient(
        credential=az_credential, subscription_id=subscription_id
    )
    return policy_client.policy_assignments.get_by_id(
        policy_assignment_id=policy_definition.assignment_ids[0]
    )


def create_policy_assignment(
    az_credential: DefaultAzureCredential,
    subscription_id: str,
    policy_definition: AzurePolicyDefinition,
    policy_initative_id: str,
    azure_path: CloudPlattformPath,
) -> PolicyAssignment:
    policy_client = PolicyClient(
        credential=az_credential, subscription_id=subscription_id
    )
    return policy_client.policy_assignments.create(
        scope=azure_path.path,
        policy_assignment_name=f"assignment-{policy_definition.name}",
        parameters=PolicyAssignment(
            policy_definition_id=policy_initative_id,
            display_name=f"assignment-{policy_definition.name}",
            metadata=policy_definition.metadata,
        ),
    )


def create_policy(
    az_credential: DefaultAzureCredential,
    subscription_id: str,
    initiative_definition: PolicySetDefinition,
    policy_set_definition_name: str,
):
    policy_client = PolicyClient(
        credential=az_credential, subscription_id=subscription_id
    )
    return policy_client.policy_set_definitions.create_or_update(
        policy_set_definition_name=policy_set_definition_name,
        parameters=initiative_definition,
    )


def get_policy(
    az_credential: DefaultAzureCredential,
    subscription_id: str,
    policy_set_definition_name: str,
):
    policy_client = PolicyClient(
        credential=az_credential, subscription_id=subscription_id
    )
    return policy_client.policy_definitions.get(
        policy_definition_name=policy_set_definition_name
    )
