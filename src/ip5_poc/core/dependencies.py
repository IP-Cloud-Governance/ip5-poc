from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from ip5_poc.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_db(requests: Request) -> AsyncIOMotorClient:
    return requests.app.state.db

def get_az_credentials() -> DefaultAzureCredential:
    if settings.is_sp_auth_possible():
        credential = ClientSecretCredential(
            tenant_id=settings.az_tenant_id,
            client_id=settings.az_client_id,
            client_secret=settings.az_client_secret
        )
    else:
        credential = DefaultAzureCredential()
    try:
        # Force an authentication attempt (Azure Resource Manager scope)
        logger.info("Azure: Successfully log in attempt")
        credential.get_token("https://management.azure.com/.default")
    except ClientAuthenticationError as e:
        logger.info("Azure: Login attempt fail")
        raise HTTPException(status_code=401, detail="Azure credential authentication failed") from e
    return credential
