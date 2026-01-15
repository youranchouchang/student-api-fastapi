from fastapi import FastAPI, Request  # 新增：导入 Request
from fastapi.responses import JSONResponse  # 新增：导入 JSONResponse
from routers import students, groups
from config.database import engine, Base
from dotenv import load_dotenv
import os

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="学生信息管理 API",
    description="实现学生/群组的增删改查、学生群组转移等功能（新增年龄校验+统一返回格式）",  # 新增：修改描述
    version="1.1.0"  # 新增：版本号升级
)

# 新增：统一返回格式中间件
@app.middleware("http")
async def unified_response(request: Request, call_next):
    # 执行原接口逻辑
    response = await call_next(request)
    # 处理响应内容
    if response.status_code == 200:
        # 读取原响应数据
        content = await response.body()
        import json
        try:
            data = json.loads(content)
            # 构造统一格式
            unified_data = {
                "code": 200,
                "msg": "操作成功",
                "data": data
            }
            return JSONResponse(content=unified_data, status_code=200)
        except:
            # 非 JSON 响应（如根路径的字符串），直接返回
            return response
    # 异常响应保持原样
    return response

# 注册路由
app.include_router(students.router)
app.include_router(groups.router)

@app.get("/")
def root():
    return {"message": "欢迎使用学生信息管理 API，访问 /docs 查看接口文档（新增年龄校验）"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )