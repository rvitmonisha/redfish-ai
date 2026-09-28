import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import initialize_database
from app.monitoring import MonitoringService
from app.routes import router


monitoring = MonitoringService(interval=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    task = asyncio.create_task(monitoring.start())

    yield

    monitoring.stop()
    await task


app = FastAPI(
    title="Redfish-AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "Redfish-AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }