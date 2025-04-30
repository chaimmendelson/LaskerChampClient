from pydantic import BaseModel, Field
from ..models.user import MAX_USERNAME_L, MAX_PASSWORD_L, EMAIL_L


class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=MAX_USERNAME_L)
    password: str = Field(..., min_length=8, max_length=MAX_PASSWORD_L)
    email_address: str = Field(..., max_length=EMAIL_L, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')

class LoginRequest(BaseModel):
    email_address: str = Field(..., min_length=3, max_length=MAX_USERNAME_L)
    password: str = Field(..., min_length=8, max_length=MAX_PASSWORD_L)
