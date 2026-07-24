from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the To-Do API", "version": "1.0.0"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_task():
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "description": "This is a test task"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert "id" in data

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_delete_task():
    # First create a task
    create_response = client.post(
        "/tasks",
        json={"title": "Task to delete", "description": "Will be deleted"}
    )
    task_id = create_response.json()["id"]

    # Delete the task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    # Verify deletion
    get_response = client.get("/tasks")
    tasks = get_response.json()
    assert not any(t["id"] == task_id for t in tasks)
