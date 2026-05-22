from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="任务管理系统")

# ========== 数据模型 ==========

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    role: Optional[str] = Field("member", pattern="^(admin|member)$")

class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    owner_id: int = Field(..., gt=0)

class CreateTaskRequest(BaseModel):
    project_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    assignee_id: Optional[int] = Field(None, gt=0)
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$")

class UpdateTaskStatusRequest(BaseModel):
    new_status: str = Field(..., pattern="^(todo|in_progress|done)$")

class AssignTaskRequest(BaseModel):
    assignee_id: int = Field(..., gt=0)

# ========== 状态流转规则 ==========

STATUS_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["done"],
    "done": []
}

# ========== 模拟数据库 ==========

users_db = {}
projects_db = {}
tasks_db = {}
user_id_counter = 1
project_id_counter = 1
task_id_counter = 1

# ========== 用户接口 ==========

@app.post("/users", status_code=201)
def create_user(request: CreateUserRequest):
    global user_id_counter
    user = {
        "id": user_id_counter,
        "username": request.username,
        "role": request.role,
        "created_at": datetime.now().isoformat()
    }
    users_db[user_id_counter] = user
    user_id_counter += 1
    return user

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f"用户 {user_id} 不存在")
    return users_db[user_id]

# ========== 项目接口 ==========

@app.post("/projects", status_code=201)
def create_project(request: CreateProjectRequest):
    global project_id_counter
    if request.owner_id not in users_db:
        raise HTTPException(status_code=404, detail=f"用户 {request.owner_id} 不存在")
    project = {
        "id": project_id_counter,
        "name": request.name,
        "owner_id": request.owner_id,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
    projects_db[project_id_counter] = project
    project_id_counter += 1
    return project

@app.get("/projects/{project_id}")
def get_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    return projects_db[project_id]

@app.patch("/projects/{project_id}/archive")
def archive_project(project_id: int, user_id: int = Query(..., gt=0)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    if projects_db[project_id]["owner_id"] != user_id:
        raise HTTPException(status_code=403, detail="只有项目创建者才能归档项目")
    if projects_db[project_id]["status"] == "archived":
        raise HTTPException(status_code=400, detail="项目已归档")
    projects_db[project_id]["status"] = "archived"
    return {"project_id": project_id, "status": "archived", "message": "项目已归档"}

# ========== 任务接口 ==========

@app.post("/tasks", status_code=201)
def create_task(request: CreateTaskRequest):
    global task_id_counter
    if request.project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"项目 {request.project_id} 不存在")
    if projects_db[request.project_id]["status"] == "archived":
        raise HTTPException(status_code=400, detail="项目已归档，不能创建任务")
    if request.assignee_id and request.assignee_id not in users_db:
        raise HTTPException(status_code=404, detail=f"用户 {request.assignee_id} 不存在")
    task = {
        "id": task_id_counter,
        "project_id": request.project_id,
        "title": request.title,
        "description": request.description,
        "assignee_id": request.assignee_id,
        "priority": request.priority,
        "status": "todo",
        "created_at": datetime.now().isoformat()
    }
    tasks_db[task_id_counter] = task
    task_id_counter += 1
    return task

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    return tasks_db[task_id]

@app.get("/projects/{project_id}/tasks")
def list_project_tasks(
    project_id: int,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail=f"项目 {project_id} 不存在")
    result = [t for t in tasks_db.values() if t["project_id"] == project_id]
    if status:
        result = [t for t in result if t["status"] == status]
    if priority:
        result = [t for t in result if t["priority"] == priority]
    if assignee_id:
        result = [t for t in result if t["assignee_id"] == assignee_id]
    total = len(result)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "tasks": result[start:end]
    }

@app.patch("/tasks/{task_id}/status")
def update_task_status(task_id: int, request: UpdateTaskStatusRequest):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    task = tasks_db[task_id]
    old_status = task["status"]
    new_status = request.new_status
    if new_status not in STATUS_TRANSITIONS[old_status]:
        raise HTTPException(
            status_code=400,
            detail=f"不允许从 {old_status} 流转到 {new_status}"
        )
    task["status"] = new_status
    return {
        "task_id": task_id,
        "old_status": old_status,
        "new_status": new_status,
        "message": "状态更新成功"
    }

@app.patch("/tasks/{task_id}/assign")
def assign_task(task_id: int, request: AssignTaskRequest):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")
    if request.assignee_id not in users_db:
        raise HTTPException(status_code=404, detail=f"用户 {request.assignee_id} 不存在")
    task = tasks_db[task_id]
    if task["status"] == "done":
        raise HTTPException(status_code=400, detail="任务已完成，不能重新指派")
    old_assignee = task["assignee_id"]
    task["assignee_id"] = request.assignee_id
    return {
        "task_id": task_id,
        "old_assignee_id": old_assignee,
        "new_assignee_id": request.assignee_id,
        "message": "任务指派成功"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)