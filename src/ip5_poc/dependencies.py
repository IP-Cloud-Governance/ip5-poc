from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient


def get_db(requests: Request) -> AsyncIOMotorClient:
    return requests.app.state.db