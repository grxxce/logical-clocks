import pytest
import json
from Client.Model.ServerRequest import ServerRequest

def test_serialize_custom_protocol():
    """Test serialization with custom protocol"""
    version = "1"
    op_code = "LOGIN"
    arguments = ["testuser", "password123"]
    
    # The custom protocol creates a string like:
    # "{version}§{length}§{op_code}§{arg1}§{arg2}"
    operation_specific = op_code + "§" + "testuser" + "§" + "password123"
    expected_length = len(operation_specific)
    expected = f"{version}§{expected_length}§{operation_specific}"
    
    result = ServerRequest.serialize_to_str(version, op_code, arguments, isJSON=False)
    assert result == expected

def test_serialize_json_protocol():
    """Test serialization with JSON protocol"""
    version = "1"
    op_code = "SEND_MESSAGE"
    arguments = ["recipient", "Hello World!"]
    
    result = ServerRequest.serialize_to_str(version, op_code, arguments, isJSON=True)
    # Notice that length is computed as: len(op_code)+len(arguments)
    # Here len(op_code)==12 (for "SEND_MESSAGE") and len(arguments)==2.
    expected_dict = {
        "version": version,
        "length": len(op_code) + len(arguments),
        "opcode": op_code,
        "arguments": arguments
    }
    assert json.loads(result) == expected_dict

def test_parse_custom_protocol():
    """Test parsing with custom protocol"""
    data = "1§20§LOGIN_SUCCESS§testuser§user1,user2"
    result = ServerRequest.parse_serialized_data(data, isJSON=False)
    expected = {
        "version": "1",
        "length": "20",
        "opcode": "LOGIN_SUCCESS",
        "arguments": ["testuser", "user1,user2"]
    }
    assert result == expected

def test_parse_json_login_success():
    """Test parsing JSON login success response"""
    payload = {
        "version": "1",
        "length": 20,
        "opcode": "LOGIN_SUCCESS",
        "arguments": ["testuser", "token123", ["user1", "user2", "user3"]]
    }
    data = json.dumps(payload)
    # The login_success case flattens the third element:
    expected = {
        "version": "1",
        "length": 20,
        "opcode": "LOGIN_SUCCESS",
        "arguments": ["testuser", "token123", "user1", "user2", "user3"]
    }
    result = ServerRequest.parse_serialized_data(data, isJSON=True)
    assert result == expected

def test_parse_json_regular_message():
    """Test parsing regular JSON message"""
    payload = {
        "version": "1",
        "length": 15,
        "opcode": "MESSAGE",
        "arguments": ["sender", "Hello!"]
    }
    data = json.dumps(payload)
    result = ServerRequest.parse_serialized_data(data, isJSON=True)
    expected = {
        "version": "1",
        "length": 15,
        "opcode": "MESSAGE",
        "arguments": ["sender", "Hello!"]
    }
    assert result == expected

def test_parse_invalid_data():
    """Test that parsing invalid data returns ValueError"""
    data = "invalid_data"
    result = ServerRequest.parse_serialized_data(data, isJSON=False)
    assert result == ValueError

def test_decode_multiple_json():
    """Test decoding multiple JSON messages concatenated together"""
    message1 = {"version": "1", "opcode": "MSG1", "arguments": ["arg1"]}
    message2 = {"version": "1", "opcode": "MSG2", "arguments": ["arg2"]}
    data = json.dumps(message1) + json.dumps(message2)
    
    result = ServerRequest.decode_multiple_json(data)
    expected = [json.dumps(message1), json.dumps(message2)]
    assert result == expected

def test_serialize_custom_protocol_special_chars():
    """Test custom protocol serialization with special characters"""
    version = "1"
    op_code = "SEND_MESSAGE"
    arguments = ["user1", "Hello! How are you? 😊"]
    
    # Build the expected string
    operation_specific = op_code + "§" + arguments[0] + "§" + arguments[1]
    expected_length = len(operation_specific)
    expected = f"{version}§{expected_length}§{operation_specific}"
    
    result = ServerRequest.serialize_to_str(version, op_code, arguments, isJSON=False)
    assert result == expected

def test_parse_bytes_data():
    """Test parsing a byte string (custom protocol)"""
    data = "1§11§MESSAGE§Hello!".encode('utf-8')
    result = ServerRequest.parse_serialized_data(data, isJSON=False)
    expected = {
        "version": "1",
        "length": "11",
        "opcode": "MESSAGE",
        "arguments": ["Hello!"]
    }
    assert result == expected

def test_parse_empty_arguments():
    """Test parsing a message with empty arguments (custom protocol)"""
    data = "1§6§LOGOUT"
    result = ServerRequest.parse_serialized_data(data, isJSON=False)
    expected = {
        "version": "1",
        "length": "6",
        "opcode": "LOGOUT",
        "arguments": []
    }
    assert result == expected

if __name__ == "__main__":
    pytest.main(["-v"])