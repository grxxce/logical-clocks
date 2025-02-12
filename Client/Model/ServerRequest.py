import json

class ServerRequest:
    # Initialize a message from serialized data.
    def __init__(self, data):
        self.data = data

    @staticmethod
    def serialize(version, op_code, arguments):
        """TODO: add documentation"""
        operation_specific = f"{op_code}"
        for arg in arguments:
            operation_specific += f"§{arg}"
        return f"{version}§{len(operation_specific)}§{operation_specific}"

    # TODO: see if this works!
    @staticmethod
    def serializeJSON(version, op_code, arguments):
        # Serialization function using JSON.
        operation_information = {
            "version": version,
            "opcode": op_code,
            "arguments": arguments
        }
        # Return as JSON string.
        return json.dumps(operation_information)
