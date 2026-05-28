from fastapi import APIRouter

from routes.admin_routes import router as admin_router
from routes.auth_routes import router as auth_router
from routes.chat_routes import router as chat_router
from routes.customer_routes import router as customer_router
from routes.health_routes import router as health_router
from routes.material_routes import router as material_router
from routes.notification_routes import router as notification_router
from routes.payment_routes import router as payment_router
from routes.photo_routes import router as photo_router
from routes.provider_routes import router as provider_router
from routes.request_routes import router as request_router
from routes.review_routes import router as review_router
from routes.service_routes import categorias_router, router as service_router
from routes.wallet_payment_routes import router as wallet_payment_router
from routes.warranty_routes import router as warranty_router


api_router = APIRouter()
legacy_router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/api/v1")

for router in (
    health_router,
    auth_router,
    customer_router,
    provider_router,
    categorias_router,
    service_router,
    request_router,
    photo_router,
    material_router,
    review_router,
    chat_router,
    notification_router,
    admin_router,
    payment_router,
    wallet_payment_router,
    warranty_router,
):
    legacy_router.include_router(router)
    v1_router.include_router(router)

api_router.include_router(legacy_router, include_in_schema=True)
api_router.include_router(v1_router, include_in_schema=True)
