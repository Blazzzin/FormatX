from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime


class File(BaseModel):
    id: Optional[str] = None 
    user_id: Optional[str] = None
    filename: str
    s3_url: str
    file_size: Optional[int] = None
    uploaded_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "filename": self.filename,
            "s3_url": self.s3_url,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at
        }