from fastapi import APIRouter,status,Depends,Request
from core.db import get_db
from sqlalchemy.orm import Session
from users.schemas import CreateUserRequest
from users.services import create_user_account
from core.security import oauth2_scheme
from users.response import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

token_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(oauth2_scheme)]
)

@router.get("/")
async def check():
    return {"message":"Done!!"}

@router.post('',status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserRequest, db: Session = Depends(get_db)):
    await create_user_account(data = data,db = db)
    return {"Message":"User was successfully created!!"}

@token_router.post("/me",status_code=status.HTTP_200_OK,response_model=UserResponse)
def get_user_detail(request: Request):
    return request.user