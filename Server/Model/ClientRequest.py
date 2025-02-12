# from uuid import uuid4
# UUID is imported so that we can have universally unique identifiers for each message
# UUID has a couple conventions, we've opted to use UUID4 as our version (todo: explain why!)

# Messages will have the following structure, adhered to by the client & the server.
# Depending on the use of JSON or the use of Strings!

# Default (using the §)
# VERSION§LENGTH§OP_CODE§ARGUMENTS
#       VERSION will be an integer
#       OP_CODE will be a string that matches one of the following:
#               REGISTER
#               LOGIN
#               SEND
#               DELETE_MESSAGE
#               DELETE_ACCOUNT
#       LENGTH will be an integer detailing the # of bytes that should be read in the message.
#       ARGUMENTS will be the arguments to the function that the OP_CODE points to.
# Example:
#   1§29§REGISTER§§{username}§{password}§{email}

# REGISTER
# ARGUMENTS:
#       username
#       password
#       email

# LOGIN
# ARGUMENTS:
#       username
#       password

# SEND
# ARGUMENTS:
#       uuid
#       sender
#       recipient
#       message

# DELETE_MESSAGE
# ARGUMENTS:
#       uuid

# DELETE_ACCOUNT
# ARGUMENTS:
#       username

import json

class ClientRequest:
    # Initialize a message from serialized data.
    def __init__(self, data):
        # if parsed_info:
        self.version = data["version"]
        self.opcode = data["opcode"]
        self.length = data["length"]
        self.arguments = data["arguments"]

    @staticmethod
    def serialize(version, op_code, arguments):
        """TODO: add documentation"""
        operation_specific = f"{op_code}"
        for arg in arguments:
            operation_specific += f"§{arg}"
        return f"{version}§{len(operation_specific)}§{operation_specific}∞"

    # TODO: see if this works!
    @staticmethod
    def serializeJSON(version, op_code, arguments):
        # Serialization function using JSON.
        operation_information = {
            "version": version,
            "opcode": op_code,
            "arguments": arguments
        }
        # Return as JSON string?
        return json.dumps(operation_information)
