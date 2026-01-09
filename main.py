from fastapi import FastAPI
from routers import students, groups
from config.database import engine, Base
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建所有数据库表（如果表不存在）
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="学生信息管理 API",
    description="实现学生/群组的增删改查、学生群组转移等功能",
    version="1.0.0"
)

# 注册路由
app.include_router(students.router)
app.include_router(groups.router)

# 根路径测试接口
@app.get("/")
def root():
    return {"message": "欢迎使用学生信息管理 API，访问 /docs 查看接口文档"}

# 启动服务（仅在直接运行 main.py 时生效）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True  # 开发模式：代码修改后自动重启
    )