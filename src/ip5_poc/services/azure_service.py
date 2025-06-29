from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from ip5_poc.models.model import AzureCloudRessource, CloudPlattformPath
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
