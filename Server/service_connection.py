from auth_handler import AuthHandler
from Model.ClientRequest import ClientRequest
from database import DatabaseManager

def parse_request(data):
    """Documentation"""
    # Do our parsing of our message into something that the client understands!
    try: 
        print("parse_request: commencing")
        message = {}
        delimiter = '§'
        split_data = data.outb.decode("utf-8")
        split_data = split_data.split(delimiter)
        message["version"] = split_data[0]
        message["length"] = split_data[1]
        message["opcode"] = split_data[2]
        message["arguments"] = split_data[3:]
        print("parse_request: done and creating client request")
        return ClientRequest(data=message)
    except:
        return ValueError

# Dealing with one client <-> server relationship at a time!
# Main point of contact with main.py
def handle_client_response(sock, data):
    print("In service connection: handle_client_response")
    print(data.outb)
    # Decipher message as a Message object.
    try:
        request = parse_request(data)
        opcode = request.opcode
        arguments = request.arguments

        match opcode:                
            case "REGISTER":
                response = register(*arguments)
                print("register called & did stuff", response)
            case "LOGIN":
                response = login(*arguments)
                print(f"login: {response}")
            case "SEND_MESSAGE":
                # response = send_message(*arguments)
                response = ""
            case "DELETE_MESSAGE":
                response = delete_message(*arguments)
            case "DELETE_ACCOUNT":
                response = delete_account(*arguments)
            case "NOTIFICATION_LIMIT":
                response = update_notification_limit(*arguments)
            case _:
                response = "Nothing to do."

        print(response)
        print(f"Finished parsing request with response: {response}")
        # take response & handle it / serialize it
        response = response.encode("utf-8")
        sent = sock.send(response)
        data.outb = data.outb[sent:]
        print("response sent!")
    except:
        print(f"handling_client_reponse: error handling data {data}")


# Handle registration requests
def register(username, password, email):
    # do things here
    AuthHandler.setup_database()
    try:
        if AuthHandler.register_user(username=username, password=password, email=email) == True:
            register_response = "REGISTER_SUCCESS§Registration successful"
            return f"1§{len(register_response)}§{register_response}"
        else:
            register_response = "REGISTER_FAILED§Failed to register user"
            return f"1§{len(register_response)}§{register_response}"
    except:
        print("register: failed to authenticate user or something like that")


# Handle login requests
def login(username, password):
    # do another thing
    try:
        if AuthHandler.authenticate_user(username=username, password=password) == True:
            # If we have a successful login, we should send over the necessary data to the user.
            setup_response = setup(username)
            login_response = f"LOGIN_SUCCESS§User authenticated§{username}§{setup_response}"
            return f"1§{len(login_response)}§{login_response}"
        else:
            login_response = "LOGIN_FAILED§Unable to authenticate user"
            return f"1§{len(login_response)}§{login_response}"
    except:
        print("login: failed to authenticate user")

def setup(username):
    # Get all possible contacts!! Send them to client when the client logs in
    print("in setup")
    usernames = DatabaseManager.get_contacts()
    response = "USERS"
    for user in usernames:
        response += "§" + user

    # Check if any messages are pending

    # Consider user preferences when sending unread messages.

    return response

def delete_message():
    # could be one message or multiple
    print("to be implemented")

def delete_account():
    # remove from db & delete messages?
    print("to be implemented")

def update_notification_limit():
    # set the limit on the # of unread messages to be received at a given time
    print("to be implemented")