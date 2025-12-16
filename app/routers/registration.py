from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.student import Student
from ..models.course import Course
from ..models.registration import Registration
from ..schemas.student_schema import Student as StudentSchema
from ..schemas.course_schema import Course as CourseSchema

router = APIRouter(tags=["Student-Course"])

@router.post("/register")
def register_course(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    course = db.query(Course).filter(Course.id == course_id).first()

    if not student or not course:
        raise HTTPException(status_code=404, detail="Student or Course not found")

    exist = db.query(Registration).filter(
        Registration.student_id == student_id,
        Registration.course_id == course_id
    ).first()

    if exist:
        raise HTTPException(status_code=400, detail="Already registered")

    reg = Registration(student_id=student_id, course_id=course_id)
    db.add(reg)
    db.commit()

    return {"message": "Registered successfully"}

@router.get(
    "/students/{id}/courses",
    response_model=list[CourseSchema]
)
def get_courses_of_student(id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student.courses

@router.get(
    "/courses/{id}/students",
    response_model=list[StudentSchema]
)
def get_students_of_course(id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.students
