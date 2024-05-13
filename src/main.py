import uvicorn
from fastapi import FastAPI, Request, Response

from core.settings import Settings
from routers.placeholder_router import router as base_marker_router
from routers.input_router import router as input_router
from routers.template_router import router as template_router

PREFIX = '/api/v1'

app = FastAPI(openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs", redoc_url="/api/v1/redoc")

settings = Settings()


app.include_router(template_router, prefix=PREFIX+'/templates', tags=['template'])
app.include_router(base_marker_router, prefix=PREFIX+'/placeholders', tags=['placeholders'])
app.include_router(input_router, prefix=PREFIX+'/input', tags=['input'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
