from fastapi import FastAPI

from api.system import router as system_router
from api.upload import router as upload_router
from api.raw_data import router as raw_router
from api.cycle import router as cycle_router

app = FastAPI(
    title="Research Data Copilot",
    version="0.1"
)

app.include_router(
    system_router,
    tags=["System"]
)

app.include_router(
    upload_router,
    tags=["Upload"]
)

app.include_router(
    raw_router,
    tags=["Raw Data"]
)

app.include_router(
    cycle_router,
    tags=["Cycle Analysis"]
)