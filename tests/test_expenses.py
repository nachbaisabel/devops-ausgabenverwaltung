import pytest

# fixed test data
@pytest.fixture
def expense_data():
    return {
        "title": "groceries",
        "amount": "14.50",
        "date": "2026-08-15",
        "category": "Food",
        "description": "dinner",
    }


# 1) empty expenses list
def test_empty_expenses_list(client):
    response = client.get("/api/expenses")
    assert response.status_code == 200
    assert response.get_json() == []

# 2) create an expense
def test_create_expense(client, expense_data):
    response = client.post("/api/expenses", json=expense_data)
    assert response.status_code == 201
    body = response.get_json()

    assert body["title"] == "groceries"
    assert body["amount"] == "14.50"
    assert body["date"] == "2026-08-15"
    assert body["category"] == "Food"
    assert body["description"] == "dinner"
    assert isinstance(body["id"], int)

# 3) get the expense by id
def test_get_single_expense(client, expense_data):
    response = client.post("/api/expenses", json=expense_data)
    assert response.status_code == 201
    created = response.get_json()

    response = client.get("/api/expenses")
    assert response.status_code == 200
    assert response.get_json() == [created]

# 4) unique id is assigned to the expense
def test_unique_expense_ids(client, expense_data):
    first = client.post("/api/expenses", json=expense_data)
    second = client.post("/api/expenses", json=expense_data)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.get_json()["id"] != second.get_json()["id"]
    assert len(client.get("/api/expenses").get_json()) == 2

# 5) description is optional and defaults to an empty string
def test_description_is_optional(client, expense_data):
    expense_data.pop("description")
    response = client.post("/api/expenses", json=expense_data)

    assert response.status_code == 201
    assert response.get_json()["description"] == ""

# 6) update the expense
def test_update_expense(client, expense_data):
    created = client.post("/api/expenses", json=expense_data).get_json()

    expense_data["amount"] = "9.80"
    response = client.put(f"/api/expenses/{created['id']}", json=expense_data)

    expected = {**expense_data, "id": created["id"]}
    assert response.status_code == 200
    assert response.get_json() == expected
    assert client.get("/api/expenses").get_json() == [expected]

# 7) update a non-existing expense returns 404
def test_update_unknown_expense(client, expense_data):
    response = client.put("/api/expenses/999", json=expense_data)
    assert response.status_code == 404

# 8) delete the expense
def test_delete_expense(client, expense_data):
    created = client.post("/api/expenses", json=expense_data).get_json()
    assert client.delete(f"/api/expenses/{created['id']}").status_code == 200

    response = client.get("/api/expenses")
    assert response.status_code == 200
    assert response.get_json() == []

# 9) delete a non-exisiting expense returns 404
def test_delete_unknown_expense(client, expense_data):
    response = client.delete("/api/expenses/999")
    assert response.status_code == 404


# 10) incorrect data input to expenses
def test_incorrect_data_input(client, expense_data):
    expense_data["category"] = "that's wrong"
    response = client.post("/api/expenses", json=expense_data)
    assert response.status_code == 400

# 11&12) incorrect body-request
def test_invalid_json(client):
    response = client.post(
        "/api/expenses",
        data='{"title":',
        content_type="application/json",
    )
    assert response.status_code == 400

def test_body_must_be_object(client):
    response = client.post("/api/expenses", json=["wrong"])
    assert response.status_code == 400

# 13) no update after incorrect put request
def test_no_update_after_invalid_request(client, expense_data):
    created = client.post("/api/expenses", json=expense_data).get_json()

    expense_data["amount"] = "13.5643"
    response = client.put(f"/api/expenses/{created['id']}", json=expense_data)

    assert response.status_code == 400
    assert client.get("/api/expenses").get_json() == [created]


# to run the tests
# python -m pytest tests/test_expenses.py -v


# expected output:
# 13 passed
