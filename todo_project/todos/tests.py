# todos/tests.py

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Endpoints
        self.register_url = "/api/register"  # Direct URL for register
        self.login_url = "/api/login"        # Direct URL for login
        self.todos_url = "/api/todos"        # Direct URL for todos

    def test_register_successful(self):
        """Test user registration with valid data"""
        data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

    def test_register_invalid_data(self):
        """Test user registration with invalid data"""
        data = {"username": "", "email": "invalidemail", "password": ""}
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)  # Check for specific errors
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_login_successful(self):
        """Test login with valid credentials"""
        # Create user in test database
        get_user_model().objects.create_user(username="testuser", password="password123")
        
        data = {"username": "testuser", "password": "password123"}
        response = self.client.post(self.login_url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"username": "invaliduser", "password": "wrongpassword"}
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_todo_crud_authenticated(self):
        """Test CRUD operations on todos with authenticated user"""
        # Create user and login
        get_user_model().objects.create_user(username="testuser", password="password123")
        login_response = self.client.post(
            self.login_url, {"username": "testuser", "password": "password123"}, format="json"
        )
        access_token = login_response.cookies.get("access_token").value
        refresh_token = login_response.cookies.get("refresh_token").value
        
        # Set cookies for authentication
        self.client.cookies["access_token"] = access_token
        self.client.cookies["refresh_token"] = refresh_token

        # Create todos
        todo_data1 = {"title": "Test Todo 1", "completed": False}
        todo_data2 = {"title": "Test Todo 2", "completed": False}
        create_response1 = self.client.post(self.todos_url, todo_data1, format="json")
        create_response2 = self.client.post(self.todos_url, todo_data2, format="json")
        self.assertEqual(create_response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response2.status_code, status.HTTP_201_CREATED)

        # Retrieve all todos
        retrieve_response = self.client.get(self.todos_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(retrieve_response.data), 2)

        # Retrieve a single todo
        todo_id = create_response1.data["id"]
        single_todo_response = self.client.get(f"{self.todos_url}/{todo_id}")
        self.assertEqual(single_todo_response.status_code, status.HTTP_200_OK)
        self.assertEqual(single_todo_response.data["id"], todo_id)
        self.assertEqual(single_todo_response.data["title"], 'Test Todo 1')

        # Update todo
        update_data = {"title": "Updated Todo", "completed": True}
        update_response = self.client.patch(
            f"{self.todos_url}/{todo_id}", update_data, format="json"
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["title"], "Updated Todo")

        # Delete todo
        delete_response = self.client.delete(f"{self.todos_url}/{todo_id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure todo no longer exists
        get_deleted_response = self.client.get(f"{self.todos_url}/{todo_id}")
        self.assertEqual(get_deleted_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_todo_crud_unauthenticated(self):
        """Test CRUD operations on todos without authentication"""
        todo_data = {"title": "Test Todo", "completed": False}

        # Attempt to create a todo without authentication
        create_response = self.client.post(self.todos_url, todo_data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Attempt to retrieve todos without authentication
        retrieve_response = self.client.get(self.todos_url)
        self.assertEqual(retrieve_response.status_code, status.HTTP_401_UNAUTHORIZED)
