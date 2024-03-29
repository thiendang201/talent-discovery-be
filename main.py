from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from exception import UnicornException

from routers.resume.main import resumeRouter
from routers.folder.main import folderRouter
from routers.user.main import userRouter

app = FastAPI()

origins = ["http://localhost:3000"]

app.router.prefix = "/api"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumeRouter)
app.include_router(folderRouter)
app.include_router(userRouter)


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(exc))
