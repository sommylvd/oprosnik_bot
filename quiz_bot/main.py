from app.api.route_enterprise import router as enterprise_router
from app.db import init_db
from fastapi import FastAPI
import uvicorn

from app import on_startup, on_shutdown

app = FastAPI(on_startup=[on_startup, init_db],
               on_shutdown=[on_shutdown])

app.include_router(enterprise_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)