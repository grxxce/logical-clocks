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
        # Let's not given an error right away!
        print("This value could not be parsed!")
        return ValueError


# Handle registration requests
# NOT THE PROBLEM
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
            login_response = f"LOGIN_SUCCESS§{username}§{setup_response}"
            return f"1§{len(login_response)}§{login_response}"
        else:
            login_response = "LOGIN_FAILED§Unable to authenticate user"
            return f"1§{len(login_response)}§{login_response}"
    except:
        print("login: failed to authenticate user")

def setup(username):
    # Get all possible contacts + the user's settings. Send them to client when the client logs in
    try:
        print("in setup")
        usernames = DatabaseManager.get_contacts()
        settings = DatabaseManager.get_settings(username)
        response = str(settings) + "§" 
        print("response AFTER SETTINGS", response)

        for user in usernames:
            response += user + "§"
        
        print("response AFTER People", response)
        return response
    except Exception as e:
        print(f"SETUP FAIL: {str(e)}")
        return False

def save_settings(username, settings):
    # Update the user's settings in the database
    print("calling update settings")
    DatabaseManager.save_settings(username, settings)
    return "SETTINGS_SAVED§Settings saved"

def get_settings(username):
    # Get the user's settings from the database
    print("calling get settings")
    settings = DatabaseManager.get_settings(username)
    return "GET_SETTINGS_SUCCESS§" + str(settings)

def delete_message():
    # could be one message or multiple
    print("to be implemented")
    response = "DELETE_MESSAGE_SUCCESS§Message deleted"

def delete_account(username):
    # remove from db & delete messages?
    DatabaseManager.delete_account(username)
    print("deleted account")
    delete_response = "DELETE_ACCOUNT_SUCCESS§Account deleted"
    return f"1§{len(delete_response)}§{delete_response}"

def update_notification_limit():
    # set the limit on the # of unread messages to be received at a given time
    print("to be implemented")