import pytest 
from fastapi.testclient import TestClient

import io 
from main import app 

client = TestClient(app)

#-------TEST 1: Health Check---------------------------------------

def test_root_endpoint(): 
    """The root endpoint should return 200 and a message."""

    response = client.get("/")
    assert response.status_code == 200

    assert "message" in response.json()

#-------TEST 2: Valid CSV upload------------------------------------
def test_analyse_valid_csv():
    """A valid CSV should return 200 with statistics"""

    csv_content = b"name,age,salary\nAlice,29,72000\nBob,34,85000\nCarol, 27, 61000"

    fake_file = io.BytesIO(csv_content)

    response = client.post(
        "/analyse", 
        files={"file": ("test.csv", fake_file, "test/csv")}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["shape"]["rows"] == 3
    assert data["shape"]["columns"] == 3
    assert "age" in data["numeric_statistics"]
    assert "salary" in data["numeric_statistics"]
    assert "name" in data["categorical_statistics"]

#--------TEST 3: Non-CSV file rejection ------------------------------

def test_rejection_non_csv(): 
    """Uploading a non-CSV file should return 400."""

    fake_file = io.BytesIO(b"this is not a csv")

    response = client.post(
        "/analyse", 
        files = {"file": ("data.txt", fake_file, "text/plain")}
    )

    assert response.status_code == 400

    assert "Only .csv" in response.json()["detail"]

#------------TEST 4: Null Detection---------------------------------
def test_null_detection(): 
    """Nulls in CSV should be correctly counted."""

    csv_content = b"name,age\nAlice,29\nBob,\nCarol, 27"

    fake_file = io.BytesIO(csv_content)

    response = client.post(
        "/analyse", 
        files={"file": ("nulls.csv", fake_file, "text/csv")}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["columns"]["age"]["null_count"] == 1

    assert data["data_quality"]["total_nulls"] == 1

    
# ── Test 5: Statistics accuracy ───────────────────────────────────────────────

def test_numeric_statistics_accuracy():
    """Mean and min/max should be computed correctly."""

    csv_content = b"value\n10\n20\n30"
    # Mean = 20, min = 10, max = 30 — easy to verify manually

    fake_file = io.BytesIO(csv_content)

    response = client.post(
        "/analyse",
        files={"file": ("numbers.csv", fake_file, "text/csv")}
    )

    assert response.status_code == 200

    stats = response.json()["numeric_statistics"]["value"]
    assert stats["mean"] == 20.0
    assert stats["min"] == 10.0
    assert stats["max"] == 30.0
    assert stats["median"] == 20.0