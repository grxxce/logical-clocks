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

class SerializationManager:
    # Initialize a message from serialized data.
    # def __init__(self, isJSON, version, data):
    #     # If parsed data...
    #     self.version = data["version"]
    #     self.opcode = data["opcode"]
    #     self.length = data["length"]
    #     self.arguments = data["arguments"]

    @staticmethod
    def serialize_to_str(version, op_code, arguments, isJSON=False):
        """TODO: add documentation"""
        if isJSON:
            operation_information = {
                "version": version,
                "length": len(op_code) + len(arguments),
                "opcode": op_code,
                "arguments": arguments
            }
            # Return as JSON string.
            print(operation_information)
            return json.dumps(operation_information)
        else:
            operation_specific = f"{op_code}"
            for arg in arguments:
                # If the argument is a dictionary or a list, then we must break it down.
                # This is only applicable to the sending of the list of users to the client,
                # which is denoted by the keyword "USERS".
                if isinstance(arg, list):
                    for item in arg:
                        operation_specific += f"§{item}"
                else:
                    operation_specific += f"§{arg}"
            return f"{version}§{len(operation_specific)}§{operation_specific}∞"

    # @staticmethod
    # def serialize(version, op_code, arguments):
    #     """TODO: add documentation"""
    #     operation_specific = f"{op_code}"
    #     for arg in arguments:
    #         operation_specific += f"§{arg}"
    #     return f"{version}§{len(operation_specific)}§{operation_specific}∞"


    # TODO: see if this works!
    # @staticmethod
    # def serializeJSON(version, op_code, arguments):
    #     # Serialization function using JSON.
    #     operation_information = {
    #         "version": version,
    #         "opcode": op_code,
    #         "arguments": arguments
    #     }
    #     # Return as JSON string?
    #     return json.dumps(operation_information)


    @staticmethod
    def parse_serialized_data(version, data, isJSON=False):
        # Currently in byte strings & not decoded.
        try:
            message = {}
            # Decode our data from a byte string into a normal string.
            decoded_data = data.outb.decode("utf-8")
            print("decoded data!", decoded_data)
            if isJSON:
                print("decoding JSON")
                json_obj = json.loads(decoded_data)
                print("json decoded and loaded as json", json_obj)
                message["version"] = json_obj["version"]
                message["length"] = json_obj["length"]
                message["opcode"] = json_obj["opcode"]
                message["arguments"] = json_obj["arguments"]
            else:
                print("decoding custom", )
                delimiter = '§'
                split_data = decoded_data.split(delimiter)
                print("split data", split_data)
                message["version"] = split_data[0]
                message["length"] = split_data[1]
                message["opcode"] = split_data[2]
                message["arguments"] = split_data[3:]
                print("arguments custom:", split_data[3:])
            return message
        except Exception as e:
            # Let's not given an error right away!
            print(f"This value could not be parsed! Failed with error {e}")
            return ValueError