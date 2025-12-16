from sqlalchemy import Column, Integer, ForeignKey
from ..database import Base

class Registration(Base):
    __tablename__ = "registrations"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
