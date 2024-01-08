from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from exception import UnicornException

from routers.resume.main import resumeRouter

app = FastAPI()

app.include_router(resumeRouter)


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(exc))