from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.database import Base

class Group(Base):
    __tablename__ = "groups"  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)  # 主键
    name = Column(String, unique=True, index=True, nullable=False)  # 群组名（唯一、非空）

    # 关联学生模型（反向查询）
    students = relationship("Student", back_populates="group")