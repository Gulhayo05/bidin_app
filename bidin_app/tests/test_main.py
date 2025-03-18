import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app and models
from models import Base  
from main import app
from schemas import UserCreate, AutoPlateCreate, BidCreate

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Reset database before tests
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Initialize TestClient
client = TestClient(app)

TEST_USER = UserCreate(
    username="testuser",
    email="test@example.com",
    password="testpassword",
    is_staff=True,  
)

future_deadline = datetime.now() + timedelta(days=365)

TEST_PLATE = AutoPlateCreate(
    plate_number="ABC123",
    description="Test Plate",
    deadline=future_deadline,
)

TEST_BID = BidCreate(
    amount=100.0,
    plate_id=1,
)

# Helper to get access token
def get_access_token():
    register_response = client.post("/auth/register", json=TEST_USER.model_dump())
    print("Register Response:", register_response.status_code, register_response.json())
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={"username": TEST_USER.username, "password": TEST_USER.password},
    )
    print("Login Response:", login_response.status_code, login_response.json())
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    return login_response.json()["access_token"]

# Run before all tests
def setup_module(module):
    reset_db()

# 1. Test Registration
def test_register():
    reset_db()
    response = client.post("/auth/register", json=TEST_USER.model_dump())
    print("Register Response:", response.status_code, response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()

# 2. Test Login
def test_login():
    reset_db()
    client.post("/auth/register", json=TEST_USER.model_dump())
    response = client.post(
        "/auth/login",
        json={"username": TEST_USER.username, "password": TEST_USER.password},
    )
    print("Login Response:", response.status_code, response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()

# 3. Test Create Plate
def test_create_plate():
    reset_db()
    token = get_access_token()
    response = client.post(
        "/plates/",
        json=jsonable_encoder(TEST_PLATE),  # Encode datetime correctly
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["plate_number"] == TEST_PLATE.plate_number

# 4. Test List Plates
def test_list_plates():
    reset_db()
    token = get_access_token()
    
    response_create = client.post(
        "/plates/",
        json=jsonable_encoder(TEST_PLATE),  # Ensures correct encoding
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_create.status_code == 200
    
    response_list = client.get("/plates/")
    assert response_list.status_code == 200
    plates = response_list.json()
    assert isinstance(plates, list)
    assert len(plates) == 1
    
    plate = plates[0]
    # Validate response keys
    expected_keys = {"id", "plate_number", "description", "deadline", "is_active", "created_by_id"}
    assert expected_keys.issubset(plate.keys())


# 5. Test Place Bid
def test_place_bid():
    reset_db()
    token = get_access_token()
    client.post(
        "/plates/",
        json=jsonable_encoder(TEST_PLATE),  # Encode datetime correctly
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.post(
        "/bids/",
        json=TEST_BID.model_dump(),  # Safe, no datetime here
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == TEST_BID.amount

# 6. Test List User Bids
def test_list_user_bids():
    reset_db()
    token = get_access_token()
    client.post(
        "/plates/",
        json=jsonable_encoder(TEST_PLATE),  # Encode datetime correctly
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/bids/",
        json=TEST_BID.model_dump(),  # Safe, no datetime here
        headers={"Authorization": f"Bearer {token}"},
    )
    response = client.get(
        "/bids/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
