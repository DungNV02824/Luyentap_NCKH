from pydantic import BaseModel

class Student(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
