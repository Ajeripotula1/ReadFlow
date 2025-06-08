from fastapi import APIRouter, status, HTTPException

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
@router.get("/users", response_model=UserList, status_code=staus.HTTP)