from auth_handler import AuthHandler
from Model.ClientRequest import ClientRequest


# Dealing with one client <-> server relationship at a time!
# Main point of contact with main.py
def handle_client_response(sock, data):
    print("In service connection: handle_client_response")
    print(data.outb)
    # # Decipher message as a Message object.
    # response = ClientRequest(str(data.outb))
    # print(response)


# Handle registration requests


# Handle login requests


# Handle message received 


# Handle sending message