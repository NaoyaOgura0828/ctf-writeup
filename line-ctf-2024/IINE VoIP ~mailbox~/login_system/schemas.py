from typing import Optional

from pydantic import BaseModel, validator


class UserCreate(BaseModel):
    name: str
    
    @validator('name')
    def validate_name(cls, v):
        # Validate name length 32
        if len(v) > 32:
            raise ValueError('Name must be less than 32 characters')
        # Validate name alphanumeric
        if not v.isalnum():
            raise ValueError('Name must be alphanumeric')
        # Validte name not "mailbox"
        if v == "mailbox":
            raise ValueError('Name cannot be "mailbox"')
        return v
    
class User(BaseModel):
    name: str
    password: str