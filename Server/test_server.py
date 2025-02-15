import pytest
from unittest.mock import Mock
import json
from Server.Model.SerializationManager import SerializationManager

class TestSerializationManager:
    """Test cases for the SerializationManager class."""

    def test_serialize_custom_protocol_simple(self):
        """Test serialization with custom protocol for simple arguments."""
        version = "1"
        op_code = "LOGIN"
        arguments = ["testuser", "password123"]
        # operation_specific = "LOGIN§testuser§password123"
        # Its length: 5 ("LOGIN") + 1 + 8 ("testuser") + 1 + 11 ("password123") = 26.
        expected = "1§26§LOGIN§testuser§password123∞"
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=False)
        assert result == expected

    def test_serialize_custom_protocol_with_list(self):
        """Test serialization with custom protocol for list arguments."""
        version = "1"
        op_code = "USERS"
        arguments = [["user1", "user2", "user3"]]
        # operation_specific = "USERS§user1§user2§user3"
        # Length: 5 (len("USERS")) + 3*6 (for each "§userX") = 5 + 18 = 23.
        expected = "1§23§USERS§user1§user2§user3∞"
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=False)
        assert result == expected

    def test_serialize_json_protocol(self):
        """Test serialization with JSON protocol."""
        version = "1"
        op_code = "LOGIN"
        arguments = ["testuser", "password123"]
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=True)
        # In JSON mode, length = len(op_code) + len(arguments) = 5 + 2 = 7.
        expected_dict = {
            "version": version,
            "length": 7,
            "opcode": op_code,
            "arguments": arguments
        }
        assert json.loads(result) == expected_dict

    def test_parse_custom_protocol(self):
        """Test parsing with custom protocol."""
        version = "1"
        # Use a sample string from our serializer:
        # "1§26§LOGIN§testuser§password123∞"
        mock_data = Mock()
        mock_data.outb = "1§26§LOGIN§testuser§password123∞".encode('utf-8')
        result = SerializationManager.parse_serialized_data(version, mock_data, isJSON=False)
        # Splitting by '§' yields: ["1", "26", "LOGIN", "testuser", "password123∞"]
        expected = {
            "version": "1",
            "length": "26",
            "opcode": "LOGIN",
            "arguments": ["testuser", "password123∞"]
        }
        assert result == expected

    def test_parse_json_protocol(self):
        """Test parsing with JSON protocol."""
        version = "1"
        mock_data = Mock()
        json_data = {
            "version": "1",
            "length": 7,
            "opcode": "LOGIN",
            "arguments": ["testuser", "password123"]
        }
        mock_data.outb = json.dumps(json_data).encode('utf-8')
        result = SerializationManager.parse_serialized_data(version, mock_data, isJSON=True)
        assert result == json_data

    def test_parse_invalid_data(self):
        """Test parsing invalid data."""
        version = "1"
        mock_data = Mock()
        mock_data.outb = "invalid_data".encode('utf-8')
        result = SerializationManager.parse_serialized_data(version, mock_data, isJSON=False)
        assert result == ValueError

    def test_serialize_custom_protocol_special_chars(self):
        """Test serialization with special characters."""
        version = "1"
        op_code = "MESSAGE"
        arguments = ["user1", "Hello! How are you? 😊"]
        # operation_specific = "MESSAGE§user1§Hello! How are you? 😊"
        # Length calculation: 7 (MESSAGE) + 6 ("§user1") + 22 ("§Hello! How are you? 😊") = 35.
        expected = "1§35§MESSAGE§user1§Hello! How are you? 😊∞"
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=False)
        assert result == expected

    def test_parse_custom_protocol_empty_args(self):
        """Test parsing with empty arguments (custom protocol with trailing delimiter)."""
        version = "1"
        mock_data = Mock()
        # Note: string ends with a delimiter. Splitting returns an empty string as the last argument.
        mock_data.outb = "1§6§LOGOUT§".encode('utf-8')
        result = SerializationManager.parse_serialized_data(version, mock_data, isJSON=False)
        expected = {
            "version": "1",
            "length": "6",
            "opcode": "LOGOUT",
            "arguments": [""]
        }
        assert result == expected

    def test_serialize_json_protocol_complex(self):
        """Test JSON serialization with complex data."""
        version = "1"
        op_code = "UPDATE"
        arguments = [{"user": "testuser", "status": "online", "last_seen": "12:34"}]
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=True)
        # Here, length = len("UPDATE") + len(arguments) = 6 + 1 = 7.
        expected_dict = {
            "version": version,
            "length": 7,
            "opcode": op_code,
            "arguments": arguments
        }
        assert json.loads(result) == expected_dict

    # --- Additional Tests ---

    def test_serialize_custom_protocol_empty_arguments(self):
        """Test custom protocol serialization when arguments list is empty."""
        version = "1"
        op_code = "PING"
        arguments = []
        # With no arguments, operation_specific becomes simply "PING" (length 4).
        expected = "1§4§PING∞"
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=False)
        assert result == expected

    def test_serialize_json_protocol_empty_arguments(self):
        """Test JSON protocol serialization when arguments list is empty."""
        version = "1"
        op_code = "PING"
        arguments = []
        # In JSON mode, length = len("PING") + 0 = 4.
        result = SerializationManager.serialize_to_str(version, op_code, arguments, isJSON=True)
        expected_dict = {
            "version": version,
            "length": 4,
            "opcode": op_code,
            "arguments": arguments
        }
        assert json.loads(result) == expected_dict

    def test_parse_json_malformed_data(self):
        """Test parsing with JSON protocol when provided data is malformed."""
        version = "1"
        mock_data = Mock()
        # Malformed JSON (missing closing bracket)
        malformed = '{"version": "1", "length": 7, "opcode": "LOGIN", "arguments": ["testuser", "password123"'
        mock_data.outb = malformed.encode('utf-8')
        result = SerializationManager.parse_serialized_data(version, mock_data, isJSON=True)
        assert result == ValueError

if __name__ == "__main__":
    pytest.main(["-v"])