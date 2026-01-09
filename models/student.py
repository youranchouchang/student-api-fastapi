from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Student(Base):
    __tablename__ = "students"  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)  # 主键
    name = Column(String, index=True, nullable=False)   # 学生姓名（非空）
    age = Column(Integer, nullable=False)               # 年龄（非空）
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # 关联群组

    # 关联群组模型（反向查询）
    group = relationship("Group", back_populates="students")