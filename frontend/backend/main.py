# FastAPI 主程式入口

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.indicators_routes import router as indicators_router
from app.api.strategy_routes import router as strategy_router
from app.api.trading_routes import router as trading_router
from app.users.routes import router as users_router

# 建立 FastAPI 應用
app = FastAPI(
    title="HSI Strategy API",
    description="恒生指數策略應用的後端 API",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該指定確切的前端來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康檢查路由
@app.get("/ping", tags=["Health"])
async def health_check():
    """健康檢查端點"""
    return {"status": "ok"}

# 掛載指標路由器
app.include_router(indicators_router, prefix="/api/indicators")

# 掛載策略路由器
app.include_router(strategy_router, prefix="/api/strategy")

# 掛載交易路由器
app.include_router(trading_router, prefix="/api/trade")

# 掛載使用者路由器
app.include_router(users_router, prefix="/api/users")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
