from fastapi import FastAPI
from users.route import router as user_router,token_router
from auth.route import router as auth_router
from core.security import JWTAuth
from starlette.middleware.authentication import AuthenticationMiddleware
from video.route import router as upload_router

app = FastAPI()
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(token_router)
app.include_router(upload_router)

app.add_middleware(AuthenticationMiddleware,backend=JWTAuth())

@app.get("/")
async def home():
    return {"Response" : "Hello World!!!"}