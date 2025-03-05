import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import grpc
from collections import defaultdict
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import proto files
from proto import service_pb2
from proto import service_pb2_grpc

# Import the MessageServer class
from Server.main import MessageServer

class TestMessageServer(unittest.TestCase):
    def setUp(self):
        # Create a server instance for testing
        self.server = MessageServer()
        
        # Mock the context
        self.context = MagicMock()
        
        # Initialize server state for testing
        self.server.active_clients = {}
        self.server.message_queue = defaultdict(list)
        self.server.pending_messages = defaultdict(list)
    
    def test_init(self):
        """Test that the server initializes with the correct state."""
        server = MessageServer()
        self.assertEqual(server.active_clients, {})
        self.assertIsInstance(server.pending_messages, defaultdict)
        self.assertIsInstance(server.message_queue, defaultdict)
    
    def test_send_message_to_active_client(self):
        """Test sending a message to an active client."""
        # Create a message
        request = service_pb2.Message(
            sender="user1",
            recipient="user2",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        
        # Set up an active client with a mock context that is active
        mock_context = MagicMock()
        mock_context.is_active.return_value = True
        self.server.active_clients = {"user2": mock_context}
        
        # Send the message
        response = self.server.SendMessage(request, self.context)
        
        # Assert the response is correct
        self.assertEqual(response.status, service_pb2.MessageResponse.MessageStatus.SUCCESS)
        
        # Assert the message was added to the queue
        self.assertEqual(len(self.server.message_queue["user2"]), 1)
        self.assertEqual(self.server.message_queue["user2"][0].sender, "user1")
        self.assertEqual(self.server.message_queue["user2"][0].message, "Hello!")
    
    def test_send_message_to_inactive_client(self):
        """Test sending a message to an inactive client."""
        # Create a message
        request = service_pb2.Message(
            sender="user1",
            recipient="user3",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        
        # No active clients
        self.server.active_clients = {}
        
        # Send the message
        response = self.server.SendMessage(request, self.context)
        
        # Assert the response is correct
        self.assertEqual(response.status, service_pb2.MessageResponse.MessageStatus.SUCCESS)
        
        # Assert the message was added to pending messages
        self.assertEqual(len(self.server.pending_messages["user3"]), 1)
        self.assertEqual(self.server.pending_messages["user3"][0].sender, "user1")
        self.assertEqual(self.server.pending_messages["user3"][0].message, "Hello!")
    
    def test_send_message_to_disconnected_client(self):
        """Test sending a message to a client that appears active but has disconnected."""
        # Create a message
        request = service_pb2.Message(
            sender="user1",
            recipient="user2",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        
        # Set up a client that appears active but has disconnected
        mock_context = MagicMock()
        mock_context.is_active.return_value = False
        self.server.active_clients = {"user2": mock_context}
        
        # Send the message
        response = self.server.SendMessage(request, self.context)
        
        # Assert the response is correct
        self.assertEqual(response.status, service_pb2.MessageResponse.MessageStatus.SUCCESS)
        
        # Assert the client was removed from active clients
        self.assertEqual(len(self.server.active_clients), 0)
        
        # Assert the message was added to pending messages
        self.assertEqual(len(self.server.pending_messages["user2"]), 1)
        self.assertEqual(self.server.pending_messages["user2"][0].sender, "user1")
        self.assertEqual(self.server.pending_messages["user2"][0].message, "Hello!")
    
    def test_send_message_error_handling(self):
        """Test error handling in SendMessage."""
        # Create a message
        request = service_pb2.Message(
            sender="user1",
            recipient="user2",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        
        # Mock an exception when checking if client is active
        mock_context = MagicMock()
        mock_context.is_active.side_effect = Exception("Test exception")
        self.server.active_clients = {"user2": mock_context}
        
        # Send the message
        response = self.server.SendMessage(request, self.context)
        
        # Assert the response indicates failure
        self.assertEqual(response.status, service_pb2.MessageResponse.MessageStatus.FAILURE)
    
    def test_get_pending_message_success(self):
        """Test retrieving pending messages successfully."""
        # Create a request
        request = service_pb2.PendingMessageRequest(username="testuser")
        
        # Add some pending messages
        message1 = service_pb2.Message(
            sender="user1",
            recipient="testuser",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        
        message2 = service_pb2.Message(
            sender="user2",
            recipient="testuser",
            message="Hi there!",
            timestamp="2023-01-01 12:01:00"
        )
        
        self.server.pending_messages["testuser"] = [message1, message2]
        
        # Get the generator
        response_generator = self.server.GetPendingMessage(request, self.context)
        
        # Convert generator to list
        responses = list(response_generator)
        
        # Assert the responses are correct
        self.assertEqual(len(responses), 2)
        self.assertEqual(responses[0].status, service_pb2.PendingMessageResponse.PendingMessageStatus.SUCCESS)
        self.assertEqual(responses[0].message.sender, "user1")
        self.assertEqual(responses[0].message.message, "Hello!")
        self.assertEqual(responses[1].status, service_pb2.PendingMessageResponse.PendingMessageStatus.SUCCESS)
        self.assertEqual(responses[1].message.sender, "user2")
        self.assertEqual(responses[1].message.message, "Hi there!")
        
        # Assert the pending messages were cleared
        self.assertEqual(len(self.server.pending_messages["testuser"]), 0)
    
    def test_monitor_messages_new_client(self):
        """Test monitoring messages for a new client."""
        # Create a request
        request = service_pb2.MonitorMessagesRequest(username="testuser")
        
        # Set up the context to simulate client disconnection after some time
        self.context.is_active.side_effect = [True, True, False]
        
        # Add a message to the queue that will be sent
        test_message = service_pb2.Message(
            sender="user1",
            recipient="testuser",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        self.server.message_queue["testuser"].append(test_message)
        
        # Call MonitorMessages
        response_generator = self.server.MonitorMessages(request, self.context)
        
        # Get the first response
        response = next(response_generator)
        
        # Assert the client was added to active clients
        self.assertIn("testuser", self.server.active_clients)
        self.assertEqual(self.server.active_clients["testuser"], self.context)
        
        # Assert the message was sent
        self.assertEqual(response.sender, "user1")
        self.assertEqual(response.message, "Hello!")
        
        # Try to get another response, which should raise StopIteration due to client disconnection
        with self.assertRaises(StopIteration):
            next(response_generator)
        
        # Assert the client was removed from active clients
        self.assertNotIn("testuser", self.server.active_clients)
    
    def test_monitor_messages_existing_client(self):
        """Test monitoring messages for a client that already has an active connection."""
        # Create a request
        request = service_pb2.MonitorMessagesRequest(username="testuser")
        
        # Set up an existing client
        existing_context = MagicMock()
        self.server.active_clients["testuser"] = existing_context
        
        # Set up the new context to simulate client disconnection after some time
        self.context.is_active.side_effect = [True, False]
        
        # Call MonitorMessages
        response_generator = self.server.MonitorMessages(request, self.context)
        
        # Try to get a response, which should raise StopIteration due to client disconnection
        with self.assertRaises(StopIteration):
            next(response_generator)
        
        # Assert the client was updated in active clients
        self.assertEqual(self.server.active_clients["testuser"], self.context)
    
    def test_monitor_messages_exception_handling(self):
        """Test exception handling in MonitorMessages."""
        # Create a request
        request = service_pb2.MonitorMessagesRequest(username="testuser")
        
        # Set up the context to raise an exception
        self.context.is_active.side_effect = Exception("Test exception")
        
        # Add a message to the queue
        test_message = service_pb2.Message(
            sender="user1",
            recipient="testuser",
            message="Hello!",
            timestamp="2023-01-01 12:00:00"
        )
        self.server.message_queue["testuser"].append(test_message)
        
        # Call MonitorMessages
        response_generator = self.server.MonitorMessages(request, self.context)
        
        # Try to get a response, which should raise StopIteration due to the exception
        with self.assertRaises(StopIteration):
            next(response_generator)
        
        # Assert the client was removed from active clients in the finally block
        self.assertNotIn("testuser", self.server.active_clients)

if __name__ == "__main__":
    unittest.main()