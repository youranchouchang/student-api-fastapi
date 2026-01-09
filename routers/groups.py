from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.group import Group
from models.student import Student
from config.database import get_db

router = APIRouter(prefix="/groups", tags=["groups"])

# Pydantic 模型
class GroupCreate(BaseModel):
    name: str

class GroupUpdate(BaseModel):
    name: str | None = None

class GroupResponse(GroupCreate):
    id: int

    class Config:
        orm_mode = True

# 1. 创建群组
@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    # 校验群组名是否重复
    db_group = db.query(Group).filter(Group.name == group.name).first()
    if db_group:
        raise HTTPException(status_code=400, detail="群组名已存在")
    new_group = Group(**group.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

# 2. 查询所有群组
@router.get("/", response_model=list[GroupResponse])
def get_all_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()

# 3. 查询单个群组（包含该群组的所有学生）
@router.get("/{group_id}")
def get_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="群组不存在")
    # 查询该群组的所有学生
    students = db.query(Student).filter(Student.group_id == group_id).all()
    return {
        "group": db_group,
        "student_count": len(students),
        "students": students
    }

# 4. 修改群组名
@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group: GroupUpdate, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="群组不存在")
    # 校验新群组名是否重复（如果修改了名称）
    if group.name and group.name != db_group.name:
        existing_group = db.query(Group).filter(Group.name == group.name).first()
        if existing_group:
            raise HTTPException(status_code=400, detail="群组名已存在")
    # 更新名称
    if group.name:
        db_group.name = group.name
    db.commit()
    db.refresh(db_group)
    return db_group

# 5. 删除群组
@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="群组不存在")
    # 可选：删除群组前，清空该群组下所有学生的 group_id
    db.query(Student).filter(Student.group_id == group_id).update({Student.group_id: None})
    # 删除群组
    db.delete(db_group)
    db.commit()
    return {"message": "群组删除成功"}