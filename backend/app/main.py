from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .core.database import engine, Base
from .routers import phenotype, meetings, reports, upload

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="太空育种基因轨迹纪要系统 API",
    description="面向太空育种实验记录会议的基因轨迹纪要全栈系统",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(phenotype.router)
app.include_router(meetings.router)
app.include_router(reports.router)
app.include_router(upload.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "太空育种基因轨迹纪要系统运行正常"}


@app.get("/")
async def root():
    return {
        "name": "太空育种基因轨迹纪要系统",
        "version": "1.0.0",
        "docs": "/docs",
        "api_endpoints": {
            "表型数据": "/api/phenotype",
            "会议管理": "/api/meetings",
            "报告管理": "/api/reports",
            "文件上传": "/api/upload/audio",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
