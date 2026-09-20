from fastapi import Depends,HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select,or_
from datetime import timedelta
from app.model import User
from app.database import get_db
from app.schemas import UserRegister, UserRoles, UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from app.config import settings
from app.utils.security import verify_password, create_access_token, hash_password, get_current_user

router = APIRouter(prefix="/api/v1/auth",tags=["auth"])

@router.post("/register",response_model=UserResponse,status_code=201)
def register(form_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exist in db
    user = db.scalar(select(User).where(
                        or_(User.username == form_data.username,
                            User.email == form_data.email,
                            User.phone == form_data.phone
                        )))

    if user:
        if user.username == form_data.username:
            raise HTTPException(
                status_code=409,
                detail="Username already exists."
            )

        if user.email == form_data.email:
            raise HTTPException(
                status_code=409,
                detail="Email already exists."
            )

        if user.phone == form_data.phone:
            raise HTTPException(
                status_code=409,
                detail="Mobile number already exists."
            )
    
    # Try to register User
    try:
        new_user = User(
            username = form_data.username,
            password_hash = hash_password(form_data.password),
            role = UserRoles.CUSTOMER,
            first_name = form_data.firstname,
            last_name = form_data.lastname,
            email = form_data.email,
            phone = form_data.phone
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username,email, or mobile number already exists."
        )

    except Exception:
        db.rollback()
        raise

    return UserResponse(
         user_id=new_user.user_id,
         username=new_user.username
    )

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.scalar(select(User).where(User.username == form_data.username))

    if not user or not verify_password(form_data.password,user.password_hash):
        raise HTTPException(status_code=401,detail="Incorrect Username or Password.")

    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=timedelta(settings.access_token_expire_minutes)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "username": current_user.username,
        "firstname": current_user.first_name,
        "lastname": current_user.last_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "available_balance": current_user.available_balance
    }


