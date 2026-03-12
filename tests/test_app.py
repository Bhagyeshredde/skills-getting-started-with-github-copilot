import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data between tests"""
    from src import app as app_module
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Swimming Club": {
            "description": "Swim training and friendly meets",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Workshop": {
            "description": "Hands-on classes in painting and sculpture",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": []
        },
        "Choir": {
            "description": "Vocal training and performances",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Book Club": {
            "description": "Discuss literature and share recommendations",
            "schedule": "Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Saturdays, 10:00 AM - 1:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }
    
    yield
    
    # Reset to original state after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        # Arrange
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that all activities have required fields"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_activities_contain_initial_signups(self, client):
        """Test that activities contain initial participant signups"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self, client):
        """Test signing up a student for an existing activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
    
    def test_signup_updates_activity_participants(self, client):
        """Test that signup updates the activity's participant list"""
        # Arrange
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/Swimming Club/signup?email={email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities["Swimming Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_duplicate_signup_rejected(self, client):
        """Test that duplicate signups are rejected"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_multiple_students_can_signup(self, client):
        """Test that multiple students can sign up for the same activity"""
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        client.post(f"/activities/Art Workshop/signup?email={email1}")
        client.post(f"/activities/Art Workshop/signup?email={email2}")
        response = client.get("/activities")
        
        # Assert
        participants = response.json()["Art Workshop"]["participants"]
        assert email1 in participants
        assert email2 in participants


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_from_activity(self, client):
        """Test unregistering a student from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from the activity"""
        # Arrange
        email = "emma@mergington.edu"
        
        # Act
        client.delete(f"/activities/Programming Class/signup?email={email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email not in activities["Programming Class"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_student_not_signed_up(self, client):
        """Test unregistering a student who is not signed up"""
        # Arrange
        activity_name = "Basketball Team"
        email = "noone@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_and_signup_again(self, client):
        """Test that a student can unregister and sign up again"""
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Choir"
        
        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Unregister
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        
        # Act - Sign up again
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""
    
    def test_signup_unregister_signup_workflow(self, client):
        """Test a complete signup, unregister, and signup workflow"""
        # Arrange
        email = "integration_test@mergington.edu"
        activity = "Book Club"
        
        # Act - Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        
        # Act - Verify signup
        response = client.get("/activities")
        
        # Assert
        assert email in response.json()["Book Club"]["participants"]
        
        # Act - Unregister
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        
        # Act - Verify unregister
        response = client.get("/activities")
        
        # Assert
        assert email not in response.json()["Book Club"]["participants"]
    
    def test_multiple_activity_signup(self, client):
        """Test that a student can sign up for multiple activities"""
        # Arrange
        email = "multi_student@mergington.edu"
        
        # Act
        client.post(f"/activities/Basketball Team/signup?email={email}")
        client.post(f"/activities/Art Workshop/signup?email={email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities["Basketball Team"]["participants"]
        assert email in activities["Art Workshop"]["participants"]
    
    def test_data_persists_between_requests(self, client):
        """Test that data persists between requests"""
        # Arrange
        email = "persistent_student@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/Robotics Club/signup?email={email}")
        
        # Act - Check first time
        response1 = client.get("/activities")
        
        # Assert
        assert email in response1.json()["Robotics Club"]["participants"]
        
        # Act - Check second time
        response2 = client.get("/activities")
        
        # Assert
        assert email in response2.json()["Robotics Club"]["participants"]
