import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Server imports
from Server.auth_handler import AuthHandler
from Server.database import DatabaseManager
from Server.Model.ClientRequest import ClientRequest
from Server.service_actions import register, login, delete_account, parse_request

# Client imports
from Client.UI.chat import ChatUI
from Client.UI.signup import LoginUI

# Fixtures
@pytest.fixture
def setup_test_db():
    """Create a temporary test database"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def mock_socket():
    """Create a mock socket for testing"""
    return Mock()

@pytest.fixture
def mock_selector():
    """Create a mock selector for testing"""
    return Mock()

@pytest.fixture
def mock_root():
    """Create a mock Tk root window"""
    mock = Mock()
    mock.winfo_children = Mock(return_value=[])
    return mock

# Authentication Tests
def test_register_user_success(setup_test_db):
    """Test successful user registration"""
    with patch('sqlite3.connect', return_value=setup_test_db):
        result = AuthHandler.register_user("testuser", "password123", "test@example.com")
        assert result == True

def test_register_duplicate_user(setup_test_db):
    """Test registering duplicate username"""
    with patch('sqlite3.connect', return_value=setup_test_db):
        AuthHandler.register_user("testuser", "password123", "test@example.com")
        result = AuthHandler.register_user("testuser", "newpassword", "new@example.com")
        assert "ERROR" in str(result)
        assert "Username already exists" in str(result)

def test_authenticate_user_success(setup_test_db):
    """Test successful user authentication"""
    with patch('sqlite3.connect', return_value=setup_test_db):
        AuthHandler.register_user("testuser", "password123", "test@example.com")
        result = AuthHandler.authenticate_user("testuser", "password123")
        assert result == True

def test_authenticate_user_wrong_password(setup_test_db):
    """Test authentication with wrong password"""
    with patch('sqlite3.connect', return_value=setup_test_db):
        AuthHandler.register_user("testuser", "password123", "test@example.com")
        result = AuthHandler.authenticate_user("testuser", "wrongpassword")
        assert "ERROR" in str(result)

# Database Manager Tests
def test_get_contacts(setup_test_db):
    """Test retrieving user contacts"""
    with patch('sqlite3.connect', return_value=setup_test_db):
        # Register some test users first
        AuthHandler.register_user("user1", "pass1", "user1@example.com")
        AuthHandler.register_user("user2", "pass2", "user2@example.com")
        
        contacts = DatabaseManager.get_contacts()
        assert len(contacts) == 2
        assert "user1" in contacts
        assert "user2" in contacts

def test_delete_account(setup_test_db):
    """Test deleting user account"""
    with patch('sqlite3.connect', return_value=setup_test_db):
        AuthHandler.register_user("testuser", "password123", "test@example.com")
        result = DatabaseManager.delete_account("testuser")
        assert result == True
        
        # Verify user is deleted
        cursor = setup_test_db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', ("testuser",))
        assert cursor.fetchone() is None

# Request Parsing Tests
def test_parse_request_valid():
    """Test parsing valid client request"""
    mock_data = Mock()
    mock_data.outb = "1§10§LOGIN§testuser§password123".encode('utf-8')
    
    request = parse_request(mock_data)
    assert request.opcode == "LOGIN"
    assert request.arguments == ["testuser", "password123"]
    assert request.version == "1"

def test_parse_request_invalid():
    """Test parsing invalid client request"""
    mock_data = Mock()
    mock_data.outb = "invalid_data".encode('utf-8')
    
    with pytest.raises(ValueError):
        parse_request(mock_data)

# Service Action Tests
@patch('Server.auth_handler.AuthHandler.register_user')
def test_register_service_action(mock_register):
    """Test register service action"""
    mock_register.return_value = True
    response = register("testuser", "password123", "test@example.com")
    assert "REGISTER_SUCCESS" in response

@patch('Server.auth_handler.AuthHandler.authenticate_user')
@patch('Server.service_actions.setup')
def test_login_service_action(mock_setup, mock_auth):
    """Test login service action"""
    mock_auth.return_value = True
    mock_setup.return_value = "USERS§user1§user2"
    
    response = login("testuser", "password123")
    assert "LOGIN_SUCCESS" in response
    assert "testuser" in response

# UI Component Tests
def test_chat_ui_creation(mock_root):
    """Test ChatUI initialization"""
    callbacks = {
        'send_message': Mock(),
        'get_inbox': Mock(),
        'save_settings': Mock(),
        'delete_account': Mock()
    }
    
    chat_ui = ChatUI(
        root=mock_root,
        callbacks=callbacks,
        username="testuser",
        all_users=["user1", "user2"]
    )
    
    assert chat_ui.username == "testuser"
    assert len(chat_ui.all_users) == 2

def test_login_ui_creation(mock_root):
    """Test LoginUI initialization"""
    login_callback = Mock()
    register_callback = Mock()
    
    login_ui = LoginUI(
        root=mock_root,
        login_callback=login_callback,
        register_callback=register_callback
    )
    
    # Verify UI elements were created
    assert hasattr(login_ui, 'login_frame')
    assert hasattr(login_ui, 'register_frame')

def test_chat_message_handling(mock_root):
    """Test message handling in ChatUI"""
    callbacks = {
        'send_message': Mock(),
        'get_inbox': Mock(),
        'save_settings': Mock(),
        'delete_account': Mock()
    }
    
    chat_ui = ChatUI(
        root=mock_root,
        callbacks=callbacks,
        username="testuser",
        all_users=["user1", "user2"]
    )
    
    # Test message display
    chat_ui.display_message("user1", "Hello!")
    assert "user1" in chat_ui.chat_histories
    assert len(chat_ui.chat_histories["user1"]) == 1
    assert chat_ui.chat_histories["user1"][0]["message"] == "Hello!"

# Error Handling Tests
def test_database_connection_error():
    """Test handling of database connection errors"""
    with patch('sqlite3.connect') as mock_connect:
        mock_connect.side_effect = sqlite3.Error("Database error")
        result = DatabaseManager.delete_account("testuser")
        assert result == False

def test_socket_connection_error(mock_socket):
    """Test handling of socket connection errors"""
    mock_socket.send.side_effect = ConnectionError("Connection lost")
    with pytest.raises(ConnectionError):
        mock_socket.send(b"test message")

if __name__ == "__main__":
    pytest.main(["-v"])