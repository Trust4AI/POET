import uvicorn
from fastapi import FastAPI, Request, Response

from core.settings import Settings
from routers.base_marker_router import router as base_marker_router
from routers.composite_marker_router import router as composite_marker_router
from routers.input_router import router as input_router
from routers.template_router import router as template_router

app = FastAPI()

settings = Settings()


# @app.middleware("http")
# async def db_session_middleware(request: Request, call_next):
#     response = Response("Internal server error", status_code=500)
#     try:
#         request.state.db = SessionLocal()
#         response = await call_next(request)
#     finally:
#         request.state.db.close()
#     return response

app.include_router(template_router, prefix='/templates', tags=['template'])
app.include_router(base_marker_router,
                   prefix='/base_markers', tags=['base_marker'])
app.include_router(composite_marker_router,
                   prefix='/composite_markers', tags=['composite_marker'])
app.include_router(input_router, prefix='/input', tags=['input'])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
