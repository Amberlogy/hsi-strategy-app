# FastAPI 主程式入口

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# 導入 API 路由
# from app.api import router
# app.include_router(router)

@app.get("/ping")
async def health_check():
    """健康檢查端點"""
    return {"status": "ok", "message": "服務正常運行中"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
