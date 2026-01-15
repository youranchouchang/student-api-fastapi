from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field  # 新增：导入 Field 用于校验
from models.student import Student
from models.group import Group
from config.database import get_db

router = APIRouter(prefix="/students", tags=["students"])

# 1. 新增：修改 StudentCreate 模型，添加年龄校验
class StudentCreate(BaseModel):
    name: str
    # 新增：年龄限制 6-25 岁，添加提示信息
    age: int = Field(..., ge=6, le=25, description="学生年龄，范围 6-25 岁")
    group_id: int | None = None

class StudentUpdate(BaseModel):
    name: str | None = None
    # 新增：更新时也校验年龄
    age: int | None = Field(None, ge=6, le=25, description="学生年龄，范围 6-25 岁")
    group_id: int | None = None

class StudentResponse(StudentCreate):
    id: int

    class Config:
        orm_mode = True

# 2. 新增：create_student 函数中补充校验提示（可选，增强用户体验）
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    if student.group_id:
        db_group = db.query(Group).filter(Group.id == student.group_id).first()
        if not db_group:
            raise HTTPException(status_code=404, detail="群组不存在")
    # 新增：手动校验年龄（兜底，与 Pydantic 校验双重保障）
    if not (6 <= student.age <= 25):
        raise HTTPException(status_code=400, detail="学生年龄必须在 6-25 岁之间")
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


# 2. 查询所有学生
@router.get("/", response_model=list[StudentResponse])
def get_all_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

# 3. 查询单个学生
@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    return db_student

# 4. 修改学生信息
@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    # 校验群组是否存在（如果修改了 group_id）
    if student.group_id:
        db_group = db.query(Group).filter(Group.id == student.group_id).first()
        if not db_group:
            raise HTTPException(status_code=404, detail="群组不存在")
    # 更新字段（只更新非 None 的值）
    for key, value in student.dict(exclude_unset=True).items():
        setattr(db_student, key, value)
    db.commit()
    db.refresh(db_student)
    return db_student

# 5. 删除学生
@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(db_student)
    db.commit()
    return {"message": "学生删除成功"}

# 6. 转移学生到指定群组
@router.post("/{student_id}/transfer/{group_id}")
def transfer_student(student_id: int, group_id: int, db: Session = Depends(get_db)):
    # 校验学生和群组是否存在
    db_student = db.query(Student).filter(Student.id == student_id).first()
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if not db_group:
        raise HTTPException(status_code=404, detail="群组不存在")
    # 转移群组
    db_student.group_id = group_id
    db.commit()
    db.refresh(db_student)
    return {"message": f"学生 {db_student.name} 已转移到群组 {db_group.name}", "student": db_student}