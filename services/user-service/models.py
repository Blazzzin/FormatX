from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

def object_id_str(obj_id):
    return str(obj_id) if isinstance(obj_id, ObjectId) else obj_id

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    password: str
    created_at: Optional[str] = None

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at
        }