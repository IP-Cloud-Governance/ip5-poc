from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
from azure.identity import DefaultAzureCredential

def get_db(requests: Request) -> AsyncIOMotorClient:
    return requests.app.state.db

def get_az_credentials() -> DefaultAzureCredential:
    return DefaultAzureCredential()