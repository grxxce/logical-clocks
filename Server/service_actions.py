from auth_handler import AuthHandler
from database import DatabaseManager

# Handle registration requests
def register(username, password, email):
    # do things here
    AuthHandler.setup_database()
    try:
        if AuthHandler.register_user(username=username, password=password, email=email) == True:
            op_code = "REGISTER_SUCCESS"
            arguments = [f"Registration successful for user: {username}"]
            return op_code, arguments
        else:
            op_code = "REGISTER_FAILED"
            arguments = ["Failed to register user"]
            return op_code, arguments
    except:
        print("register: failed to authenticate user or something like that")


# Handle login requests
def login(username, password):
    # do another thing
    try:
        if AuthHandler.authenticate_user(username=username, password=password) == True:
            # If we have a successful login, we should send over the necessary data to the user.
            setup_response = setup(username)
            print("setup success!")
            op_code = "LOGIN_SUCCESS"
            arguments = ["User authenticated", username, setup_response]
            return op_code, arguments
        else:
            op_code = "LOGIN_FAILED"
            arguments = ["Unable to authenticate user"]
            return op_code, arguments
    except:
        print("login: failed to authenticate user")

# TODO: COME BACK AND CHECK ON THIS!
def setup(username):
    # Get all possible contacts!! Send them to client when the client logs in
    # print("in setup")
    # usernames = DatabaseManager.get_contacts()
    # response = "USERS"
    # for user in usernames:
    #     response += "§" + user
    usernames = DatabaseManager.get_contacts()
    response = ["USERS"]
    for user in usernames:
        response.append(user)
    return response

def delete_message():
    # could be one message or multiple
    print("to be implemented")
    response = "DELETE_MESSAGE_SUCCESS§Message deleted"

def delete_account(username):
    # # remove from db & delete messages?
    # DatabaseManager.delete_account(username)
    # print("deleted account")
    # delete_response = "DELETE_ACCOUNT_SUCCESS§Account deleted"
    # return f"1§{len(delete_response)}§{delete_response}"
    DatabaseManager.delete_account(username)
    op_code = "DELETE_ACCOUNT_SUCCESS"
    arguments = ["Account deleted"]
    return op_code, arguments

def update_notification_limit():
    # set the limit on the # of unread messages to be received at a given time
    print("to be implemented")