from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.student import Student
from models.group import Group
from config.database import get_db

# 创建路由实例（前缀 /students，标签用于文档分类）
router = APIRouter(prefix="/students", tags=["students"])

# Pydantic 模型（数据验证/返回格式）
class StudentCreate(BaseModel):
    name: str
    age: int
    group_id: int | None = None

class StudentUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    group_id: int | None = None

class StudentResponse(StudentCreate):
    id: int

    class Config:
        orm_mode = True  # 支持从 ORM 对象转换为 Pydantic 模型

# 1. 创建学生
@router.post("/", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    # 校验群组是否存在（如果指定了 group_id）
    if student.group_id:
        db_group = db.query(Group).filter(Group.id == student.group_id).first()
        if not db_group:
            raise HTTPException(status_code=404, detail="群组不存在")
    # 创建学生对象
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