from pydantic import BaseModel

class Course(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True