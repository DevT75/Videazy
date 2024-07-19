import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from users.route import router as user_router, token_router
from auth.route import router as auth_router
from core.security import JWTAuth
from starlette.middleware.authentication import AuthenticationMiddleware
from video.route import router as upload_router
from video.route import compressed_folder, upload_folder
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Use wildcard for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

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

app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())

@app.get("/")
async def home():
    return {"Response": "Hello World!!!"}

@app.get("/download/{filename}")
async def download_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(compressed_folder, filename)
    upload_file_name = filename.replace('compressed_', '')
    upload_file_path = os.path.join(upload_folder, upload_file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    background_tasks.add_task(delete_file, file_path)
    background_tasks.add_task(delete_file, upload_file_path)
    return FileResponse(path=file_path, filename=filename)

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted file: {file_path}")

@app.options("/upload/")
async def options_upload():
    return JSONResponse(content={"message": "OK"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)