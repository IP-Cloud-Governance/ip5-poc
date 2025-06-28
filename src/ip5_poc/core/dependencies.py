from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError


def get_db(requests: Request) -> AsyncIOMotorClient:
    return requests.app.state.db


def get_az_credentials() -> DefaultAzureCredential:
    credential = DefaultAzureCredential()
    try:
        # Force an authentication attempt (Azure Resource Manager scope)
        credential.get_token("https://management.azure.com/.default")
    except ClientAuthenticationError as e:
        raise HTTPException(status_code=401, detail="Azure credential authentication failed") from e
    return credential
