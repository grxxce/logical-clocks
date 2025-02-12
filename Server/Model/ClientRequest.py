# from uuid import uuid4
# UUID is imported so that we can have universally unique identifiers for each message
# UUID has a couple conventions, we've opted to use UUID4 as our version (todo: explain why!)

# Messages will have the following structure, adhered to by the client & the server.
# Depending on the use of JSON or the use of Strings!

# Default (using the §)
# VERSION§OP_CODE§LENGTH§ARGUMENTS
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
#   1§REGISTER§29§{username}§{password}§{email}

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

def parse_message(data):
    # Do our parsing of our message into something that the client understands!
    print("Parsing data:", data)
    message = {}
    delimiter = '§'
    # try:
    split_data = data.split(delimiter)
    message["version"] = split_data[0]
    message["opcode"] = split_data[1]
    message["length"] = split_data[2]
    message["arguments"] = split_data[3:]
    return message
    # except:
    #     return IndexError

class ClientRequest:
    # Initialize a message from serialized data.
    def __init__(self, data):
        parsed_info = parse_message(data)
        # if parsed_info:
        self.version = parsed_info["version"]
        self.opcode = parsed_info["opcode"]
        self.length = parsed_info["length"]
        self.arguments = parsed_info["arguments"]

    @staticmethod
    def serialize():
        # Our serialization function, should return the properly formatted message to be sent over the socket
        print("Serializing")

    @staticmethod
    def serializeJSON():
        # Serialization function using JSON.
        print("Serializing as JSON")
