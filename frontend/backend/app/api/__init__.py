from fastapi import APIRouter
from .indicators_routes import router as indicators_router

# 創建主 API 路由器
router = APIRouter()

# 加入指標路由
router.include_router(indicators_router, prefix="/indicators", tags=["Indicators"])

# 將來可以在這裡添加其他路由模組
# from .other_module import router as other_router
# router.include_router(other_router, prefix="/other", tags=["Other"])
