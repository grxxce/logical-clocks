import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tkinter as tk
from datetime import datetime

# Mock tkinter before imports
mock_tk = MagicMock()
mock_ttk = MagicMock()
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from Client.main import Client
from Client.UI.chat import ChatUI
from Client.UI.login import LoginUI

@pytest.fixture
def mock_socket():
    return Mock()

@pytest.fixture
def mock_root():
    root = Mock()
    root.winfo_children.return_value = []
    root.after = Mock()
    root.update = Mock()
    root.destroy = Mock()
    return root

@pytest.fixture
def client():
    with patch('socket.socket') as mock_socket:
        client = Client('localhost', 8000)
        client.socket = mock_socket
        return client

@pytest.fixture
def chat_ui(mock_root):
    callbacks = {
        'send_message': Mock(),
        'get_inbox': Mock(),
        'save_settings': Mock(),
        'delete_message': Mock()
    }
    return ChatUI(mock_root, callbacks, "testuser", ["user1", "user2"])

# Client Tests
def test_client_initialization(client):
    """Test client initialization"""
    assert client.host == 'localhost'
    assert client.port == 8000
    assert client.version == "1"
    assert hasattr(client, 'socket')

def test_client_connect(client):
    """Test client connection"""
    client.connect()
    client.socket.connect.assert_called_once_with(('localhost', 8000))

def test_client_send_request(client):
    """Test sending request"""
    request = "TEST_REQUEST"
    client.send_request(request)
    client.socket.send.assert_called_once_with(request.encode('utf-8'))

def test_client_handle_login_success(client):
    """Test handling login success"""
    response = "1§20§LOGIN_SUCCESS§testuser§user1,user2"
    with patch('tkinter.messagebox.showinfo') as mock_showinfo:
        client.handle_server_response(response)
        mock_showinfo.assert_called_once()
        assert client.current_username == "testuser"

def test_client_handle_login_failure(client):
    """Test handling login failure"""
    response = "1§20§LOGIN_FAILED§Invalid credentials"
    with patch('tkinter.messagebox.showerror') as mock_showerror:
        client.handle_server_response(response)
        mock_showerror.assert_called_once()

# ChatUI Tests
def test_chat_ui_initialization(chat_ui):
    """Test ChatUI initialization"""
    assert chat_ui.username == "testuser"
    assert len(chat_ui.all_users) == 2
    assert chat_ui.selected_recipient is None
    assert isinstance(chat_ui.chat_histories, dict)

def test_chat_ui_display_message(chat_ui):
    """Test message display"""
    chat_ui.selected_recipient = "user1"
    chat_ui.chat_display = Mock()
    
    # Test received message
    chat_ui.display_message("user1", "Hello!")
    assert "user1" in chat_ui.chat_histories
    assert len(chat_ui.chat_histories["user1"]) == 1
    assert chat_ui.chat_histories["user1"][0]["message"] == "Hello!"

def test_chat_ui_send_message(chat_ui):
    """Test sending message"""
    chat_ui.selected_recipient = "user1"
    chat_ui.message_input = Mock()
    chat_ui.message_input.get.return_value = "Hello!"
    chat_ui.send_message_callback = Mock()
    
    chat_ui._handle_send()
    chat_ui.send_message_callback.assert_called_once()

def test_chat_ui_settings(chat_ui):
    """Test settings handling"""
    # Test settings update
    chat_ui.settings.set(100)
    assert chat_ui.settings.get() == 100
    
    # Test invalid settings
    chat_ui.settings.set(300)  # Outside valid range
    assert chat_ui.settings.get() == 50  # Should reset to default

def test_chat_ui_delete_message(chat_ui):
    """Test message deletion"""
    chat_ui.selected_recipient = "user1"
    message = {
        'sender': 'testuser',
        'message': 'Hello!',
        'timestamp': datetime.now().strftime('%H:%M')
    }
    
    # Add message to history
    chat_ui.chat_histories["user1"] = [message]
    
    # Setup delete callback
    chat_ui.delete_message_callback = Mock()
    
    # Simulate message deletion
    chat_ui.selected_message = message
    chat_ui._delete_selected_message()
    
    # Verify message was deleted
    assert len(chat_ui.chat_histories["user1"]) == 0
    chat_ui.delete_message_callback.assert_called_once()

def test_chat_ui_refresh_inbox(chat_ui):
    """Test inbox refresh"""
    # Add some test messages
    chat_ui.new_messages = {
        "user1": [{
            'sender': 'user1',
            'message': 'Hello!',
            'timestamp': datetime.now().strftime('%H:%M')
        }]
    }
    
    chat_ui.inbox_list = Mock()
    chat_ui._refresh_inbox()
    
    # Verify inbox was updated
    chat_ui.inbox_list.delete.assert_called_once_with(0, tk.END)
    assert chat_ui.inbox_list.insert.called

def test_chat_ui_search(chat_ui):
    """Test user search"""
    chat_ui.search_var = Mock()
    chat_ui.search_var.get.return_value = "user"
    chat_ui.search_results = Mock()
    
    chat_ui._handle_search()
    
    # Verify search results were updated
    chat_ui.search_results.delete.assert_called_once_with(0, tk.END)
    assert chat_ui.search_results.insert.called

# Run tests
if __name__ == "__main__":
    pytest.main(["-v"])