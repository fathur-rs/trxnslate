from pydantic import BaseModel, field_validator, Field, ConfigDict
import re
from enum import Enum
from ..utilities import make_response_util

class UserType(str, Enum):
    user = "user"
    admin = "admin"

class Register(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=12)
    user_type: UserType = Field(default=UserType.user)

    
    @field_validator('username')
    def check_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v
    
    @field_validator('password')
    def check_password_length(cls, v):
        # Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$', v):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character")
        return v
    
class Login(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1)
    user_type: UserType = Field(default=UserType.user)
    
    @field_validator('username')
    def check_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v
    
    @field_validator('user_type')
    def check_user_type(cls, v):
        if v not in ['user', 'admin']:
            raise ValueError("User type must be 'user' or 'admin'")
        return v
    