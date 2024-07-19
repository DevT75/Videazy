import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from users.route import router as user_router,token_router
from auth.route import router as auth_router
from core.security import JWTAuth
from starlette.middleware.authentication import AuthenticationMiddleware
from video.route import router as upload_router
from video.route import compressed_folder,upload_folder
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

FRONTEND_URL = "https://videazy.vercel.app"

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "https://videazy.vercel.app",
    "https://videazy-devt75s-projects.vercel.app",
    "https://videazy-aifji3oem-devt75s-projects.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://videazy.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

import logging

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"Received request: {request.method} {request.url}")
    logging.info(f"Headers: {request.headers}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    logging.info(f"Response headers: {response.headers}")
    return response

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(token_router)
app.include_router(upload_router)

app.add_middleware(AuthenticationMiddleware,backend=JWTAuth())

@app.get("/")
async def home():
    return {"Response" : "Hello World!!!"}

@app.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(compressed_folder, filename)
    upload_file_name = filename.replace('compressed_','')
    upload_file_path = os.path.join(upload_folder, upload_file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    background_tasks.add_task(delete_file, file_path)
    background_tasks.add_task(delete_file, upload_file_path)
    response = FileResponse(path=file_path, filename=filename)
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")

@app.options("/upload/")
async def options_upload():
    response = JSONResponse(content={"message": "OK"})
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_URL
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port,reload=True)