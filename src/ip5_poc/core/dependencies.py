from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from motor.motor_asyncio import AsyncIOMotorClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.core.exceptions import ClientAuthenticationError
from ip5_poc.settings import settings
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name='X-API-Key')

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized. Make sure X-API-Key is correct"
        )

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
        logger.info("Successfully log in attempt to azure")
        credential.get_token("https://management.azure.com/.default")
    except ClientAuthenticationError as e:
        logger.info("Login attempt to azure failed")
        raise HTTPException(status_code=500, detail="Azure credential authentication failed") from e
    return credential
