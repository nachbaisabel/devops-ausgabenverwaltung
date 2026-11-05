from app import create_app

def test_health_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


'''
# initial test for the /api/expenses endpoint
def test_get_expenses_endpoint():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/expenses")
    assert response.status_code == 200
    assert response.json == []  # Expecting an empty list as a placeholder

'''

# to run the tests
# python -m pytest tests/test_health.py -v

# expected output:
# 1 passed
