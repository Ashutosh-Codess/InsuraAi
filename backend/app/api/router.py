from fastapi import APIRouter

from app.api.v1 import auth, claims, customers, health, policies

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(policies.router, tags=["policies"])
api_router.include_router(claims.router, tags=["claims"])

# Temporarily disabled for Render Free deployment
# api_router.include_router(copilot.router, tags=["copilot"])