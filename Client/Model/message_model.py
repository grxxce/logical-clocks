from uuid import uuid4
# UUID is imported so that we can have universally unique identifiers for each message
# UUID has a couple conventions, we've opted to use UUID4 as our version (todo: explain why!)

class Message:
    # Initialize a message from serialized data.
    def __init__(self, data):
        self.parse_message(data)

    def parse_message(data):
        # Do our parsing of our message into something that the client understands!
        print("Parsing data:", data)

    # def __init__(self, sender, recipient, message):
    #     self.uuid = uuid4()
    #     self.sender = sender
    #     self.recipient = recipient
    #     self.message = message

    def serialize():
        # Our serialization function, should return the properly formatted message to be sent over the socket
        print("Serializing")

    def serializeJSON():
        # Serialization function using JSON.
        print("Serializing as JSON")

