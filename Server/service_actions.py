from auth_handler import AuthHandler
from database import DatabaseManager
import logging

# Configure logging set-up. We want to log times & types of logs, as well as
# function names & the subsequent message.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)

"""
This file contains helpful functions to abstract and connect handlers with our protocols.
"""

def register(username, password, email):
    """
    Handles registration requests.

    Parameters:
            username: a string
            password: a string
            email: a string
    Returns:
            op_code: a string detailing the operation code of either success or failure
            arguments: a list of arguments to be passed
                If success, returns a message of success.
                If failure, returns the reason for the failure.
    """
    AuthHandler.setup_database()
    try:
        status, message = AuthHandler.register_user(username=username, password=password, email=email)
        if status:
            op_code = "REGISTER_SUCCESS"
            arguments = [f"Registration successful for user: {username}"]
            return op_code, arguments
        else:
            op_code = "REGISTER_FAILED"
            arguments = [f"Failed to register user due to error: {message}"]
            return op_code, arguments
    except Exception as e:
        logger.error("Failed to authenticate user with exception {e}")


def login(username, password):
    """
    Handles login requests.

    Parameters:
            username: a string
            password: a string
    Returns:
            op_code: a string detailing the operation code of either success or failure
            arguments: a list of arguments to be passed
                If success, returns a message of success, a username, and a list of users that can be messaged
                If failure, returns the reason for the failure.
    """
    try:
        status, message = AuthHandler.authenticate_user(username=username, password=password)
        if status:
            # If we have a successful login, we should send over the necessary data to the user.
            setup_response = setup(username)
            logger.info("Setup succeeded in obtaining all users and authenticating.")
            op_code = "LOGIN_SUCCESS"
            arguments = ["User authenticated", username, setup_response]
            return op_code, arguments
        else:
            op_code = "LOGIN_FAILED"
            arguments = [f"Unable to authenticate user: {message}"]
            return op_code, arguments
    except Exception as e:
        logger.error(f"Failed to authenticate user with username {username}, failed with error {e}")

def setup(username):
    """
    Handles retrieving all users that a current user can message.

    Parameters:
            username: a string
    Returns:
            a list starting with "USER" and all other usernames of available clients
    """
    # Get all clients' usernames
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