from fastapi import APIRouter

from app.api.v1.endpoints import planner, foods, payments, clients, subscription

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}

api_router.include_router(planner.router, prefix="/planner", tags=["planner"])
api_router.include_router(foods.router, prefix="/foods", tags=["foods"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(subscription.router, prefix="/subscription", tags=["subscription"])
