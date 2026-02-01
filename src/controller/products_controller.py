from fastapi import APIRouter

from configuration.settings import settings
from configuration.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/products")
async def get_products():
    """Products endpoint that logs something"""
    logger.info(
        "Products endpoint called",
        endpoint="/products",
        method="GET"
    )
    
    return {
        "message": "Products endpoint",
        "service": settings.app_name,
        "version": settings.app_version,
        "products": [
            {"id": 1, "name": "Product 1", "price": 99.99},
            {"id": 2, "name": "Product 2", "price": 149.99}
        ]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy"}
