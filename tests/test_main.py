import pytest
from app.main import app, db
import json
import jsonschema
import pathlib

@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:" 
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

def test_version(client):
    response = client.get("/api/version")
    assert response.status_code == 200
    assert "version" in response.get_json()
    
def test_post_items_empty(client):
    response = client.post("/api/items", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "name required"}
    
def test_post_items(client):
    response = client.post("/api/items", json={"name": "test"})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data
    assert data["name"] == "test"
    
def test_get_items(client):
    schema = json.loads(pathlib.Path("tests/items.schema.json").read_text())
    response = client.get("/api/items")
    assert response.status_code == 200
    jsonschema.validate(instance=response.get_json(), schema=schema)
    
def test_404_not_found(client):
    response = client.get("/api/this_route_does_not_exist")
    assert response.status_code == 404