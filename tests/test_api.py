import pytest

from models.Task import TaskResponse


@pytest.fixture
async def test_task(async_client):
    print("\n--- [SETUP] Create task before test ---")
    response = await async_client.post(
        "/tasks",
        json={
            "title": "Test task",
            "description": "Created only for tests",
            "priority": 1,
            "user_id": 1
        }
    )
    assert response.status_code == 201
    task_data = response.json()

    # give task for using
    yield task_data

    print("\n--- [TEARDOWN] Delete task after test ---")
    response = await async_client.delete(f"/tasks/{task_data['id']}")
    assert response.status_code == 204


@pytest.mark.anyio
async def test_post_and_delete(async_client):
    create_response = await async_client.post(
        "/tasks",
        json={
            "title": "Testing create",
            "description": "This task tests creating and deliting",
            "is_completed": False,
            "priority": 1,
            "user_id": 1
        }
    )
    assert create_response.status_code == 201

    task_data = create_response.json()
    assert task_data["title"] == "Testing create"
    assert task_data["description"] == "This task tests creating and deliting"
    assert task_data["priority"] == 1
    assert task_data["is_completed"] is False
    assert task_data["user_id"] == 1

    task_id = task_data["id"]
    delete_response = await async_client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    

@pytest.mark.anyio
async def test_get_tasks(async_client):
    response = await async_client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_get_task_by_id(async_client, test_task):
    task_id = test_task["id"]
    response = await async_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

    task_model = TaskResponse.model_validate(response.json())
    assert task_model.id == task_id


@pytest.mark.anyio
async def test_get_nonexistent_task(async_client):
    response = await async_client.get("/tasks/999999")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # wrong priority (Expect exception 422)
        (
            {"title": "Task", "priority": "max", "user_id": 1},
            422
        ),
        # wrong title (Expect exception 422)
        (
            {"title": 3, "priority": 1, "user_id": 1},
            422
        ),
        # wrong user_id (Expect exception 422)
        (
            {"title": "Task", "priority": "max", "user_id": ""},
            422
        ),
        # missing necessary attribute title
        (
            {"priority": 5, "user_id": 1},
            422
        ),
        # missing necessary attribute priority
        (
            {"title": "Task", "user_id": 1},
            422
        ),
        # missing necessary attribute user_id
        (
            {"title": "Task", "priority": 5},
            422
        ),
        # task with nonexistent user id (Expect 404)
        (
            {"title": "Task", "priority": 1, "user_id": 999999},
            404
        )
    ]
)
@pytest.mark.anyio
async def test_create_task_validation_errors(async_client, payload, expected_status):
    response = await async_client.post("/tasks", json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "patch_data",
    [
        {"title": "New title"},
        {"description": "New description"},
        {"priority": 3},
        {"user_id": 2},
        {"is_completed": True}
    ]
)
@pytest.mark.anyio
async def test_patch_task(
    async_client, 
    test_task,
    patch_data
):
    task_id = test_task["id"]
    patch_response = await async_client.patch(f"/tasks/{task_id}", json=patch_data)
    assert patch_response.status_code == 200

    response_data = patch_response.json()

    for key, value in patch_data.items():
        assert response_data[key] == value


@pytest.mark.anyio
async def test_delete_nonexistent_task(async_client):
    response = await async_client.delete("/tasks/999999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_patch_nonexistent_task(async_client):
    response = await async_client.patch(
        "/tasks/999999",
        json={"is_completed": True}
    )
    assert response.status_code == 404
