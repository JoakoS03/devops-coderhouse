from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="To-Do API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app)

# In-memory storage
tasks = []
task_id_counter = 1

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class Task(TaskCreate):
    id: int
@app.get("/")
def read_root():
    return {"message": "Welcome to the To-Do API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    global task_id_counter
    # Use dict() for pydantic v1 compatibility or model_dump() for v2
    task_data = task.dict() if hasattr(task, "dict") else task.model_dump()
    new_task = Task(id=task_id_counter, **task_data)
    tasks.append(new_task)
    task_id_counter += 1
    return new_task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            del tasks[i]
            return
    raise HTTPException(status_code=404, detail="Task not found")
