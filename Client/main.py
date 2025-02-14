import socket
from UI.signup import LoginUI
from UI.chat import ChatUI
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import argparse
import logging

# Our Model Helpers
from Model.ServerRequest import ServerRequest

# Configure logging set-up. We want to log times & types of logs, as well as
# function names & the subsequent message.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)

# TODO: make these command line arguments!
version = 1
isJSON = False


class Client:
    """
    The Client class instantiates the client-facing user interface and contains
    functionalities for managing the connection between the client and server.

    This file contains three main sections, denoted by "MARK"s:
        1. Creation of UI
        2. Sending requests to the server
        3. Handling server responses to requests
    """

    def __init__(self, host, port):
        """
        Creates the user interface and necessary threads that the client will run on.
        Initializes necessary data about the server to aid in connection logistics.

        Parameters:
                host: the IP address of the server, inputted into the command line
                port: the port on the host to connect to, inputted into the command line
        """
        self.host = host
        self.port = port
        self.connectedWithServer = False
        self.socketConnection = None
        self.running = True

        #todo: replace with real thing later
        self.message_history_limit = 50
        
        # Create root window
        self.root = tk.Tk()
        
        # Create login UI
        self.show_login_ui()

        # Start the socket connection in a separate thread
        self.socket_thread = threading.Thread(target=self.establishServerConnection)
        # Thread will close when the main program exits
        self.socket_thread.daemon = True  
        self.socket_thread.start()

    # MARK: User Interface Functionalities
    def show_login_ui(self):
        """Show the login UI."""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.ui = LoginUI(
            root=self.root,
            login_callback=self._handle_login,
            register_callback=self._handle_register
        )

    def show_chat_ui(self, username, all_users):
        """
        Switch the UI to the chat UI.

        Parameters:
                username: a string of the username of the current user
                all_users: a list of users that the current user can message
        """
        for widget in self.root.winfo_children():
            widget.destroy()
            
        callbacks = {
            'send_message': self._handle_chat_message,
            'get_inbox': self._handle_get_inbox,
            'save_settings': self._handle_save_settings,
            'delete_account': self._handle_delete_account
        }
        
        self.current_username = username
        self.all_users = all_users
        self.chat_ui = ChatUI(
            root=self.root,
            callbacks=callbacks,
            username=username,
            all_users=all_users 
        )

    # MARK: Handling Requests to the Server
    def _handle_chat_message(self, recipient, message):
        """
        Handle sending chat messages.

        Parameters:
                recipient: a string of the username of the desired recipient of a message
                message: a string that will be sent
        """
        OP_CODE = "SEND_MESSAGE"
        chat_message = ServerRequest.serialize_to_str(version, OP_CODE, [self.current_username, recipient, message], isJSON)
        self.send_request(chat_message)
        logger.info(f"Client sent request to server to deliver message to {recipient} with message {message}.")

    
    def _handle_get_inbox(self):
        """Handle inbox refresh requests and return unread messages."""
        logger.info("Handling inbox refresh request.")
        unread_messages = {}
        
        # Check chat histories for unread messages
        if hasattr(self, 'chat_ui'):
            for username, messages in self.chat_ui.chat_histories.items():
                # Get user's message history limit
                history_limit = 50  # Default could be 50
                
                # Get unread messages (messages beyond the history limit)
                if len(messages) > history_limit:
                    unread_messages[username] = messages[history_limit:]
                    # Trim chat history to limit
                    self.chat_ui.chat_histories[username] = messages[:history_limit]
        
        print(hasattr(self, 'chat_ui'), unread_messages)
        return list(unread_messages.keys())  # Return users with unread messages

    def _handle_login(self, username, password):
        """
        Callback for login button. 
        Sends a login request to the server.

        Parameters:
                username: a string 
                password: a string 
        """
        OP_CODE = "LOGIN"
        login_request = ServerRequest.serialize_to_str(version, OP_CODE, [username, password], isJSON)
        self.send_request(login_request)
        logger.info(f"Client {username} sent login request to server.")

    def _handle_register(self, username, password, email):
        """
        Callback for register button.
        Sends a register request to the server.

        Parameters:
                username: a string 
                password: a string 
                email: a string
        """
        OP_CODE = "REGISTER"
        register_request = ServerRequest.serialize_to_str(version, OP_CODE, [username, password, email], isJSON)
        self.send_request(register_request)
        logger.info(f"Client {username} sent register request to server.")
    
    def _handle_save_settings(self, settings):
        """
        Callback for the user saving settings on limiting the number of unread messages.
        Sends a request to the server to update the notification limit.

        Parameters:
                settings: a dictionary with account setting information
        """
        OP_CODE = "NOTIFICATION_LIMIT"
        settings_request = ServerRequest.serialize_to_str(version, OP_CODE, [self.current_username, settings['message_history_limit']], isJSON)
        self.send_request(settings_request)
        logger.info(f"Client sent request to server to update notification limit.")

    def _handle_delete_account(self):
        """Handle account deletion"""
        OP_CODE = "DELETE_ACCOUNT"
        delete_account_request = ServerRequest.serialize_to_str(version, OP_CODE, [self.current_username], isJSON)
        self.send_request(delete_account_request)
        logger.info(f"Client sent request to have account deleted.")
        # Close the chat window and return to login
        # self.root.destroy()

    def _handle_delete_message(self, message_uuid, sender, recipient):
        """Handle the deletion of messages on both a sender & recipients' devices.
           Send a message to the server asking to delete one or more messages from both clients."""
        op_code = "DELETE_MESSAGE"
        delete_message_request = ServerRequest.serialize_to_str(version, op_code, [message_uuid, sender, recipient], isJSON)
        self.send_request(delete_message_request)
        logger.info(f"Client sent request to have message to {recipient} deleted.")

    # MARK: Handling Server Connection & Responses
    def establishServerConnection(self):
        """
        Create a socket connection with the server through its host IP and port.
        Monitor the socket connection for read and write events, and handle
        responses accordingly by passing to the proper handler.
        """
        try: 
            logger.info(f"Starting socket connection with host {self.host} on port {self.port}.")
            self.socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.host, self.port)

            # Connect to the server
            self.socketConnection.connect(server_address)
            self.socketConnection.setblocking(False)
            logger.info("Successfully connected to the server.")

            # Handle data from and to the server
            self.connectedWithServer = True
            while self.running:
                try:
                    # If data has been sent to the client, retrieve it and decode it
                    # from a byte string into a string.
                    data = self.socketConnection.recv(1024)
                    if data:
                        decoded_data = data.decode('utf-8')
                        self.handle_server_response(decoded_data)
                except socket.error:
                    # TODO: check if this is okay because it looks like hundreds of warnings
                    continue
        
        except Exception as e:
            logger.error(f"An error occurred with the socket: {e}")
        
        finally:
            # If the client closes or disconnects, then close the socket connection.
            if self.socketConnection:
                self.socketConnection.close()


    def handle_server_response(self, data):
        """
        Handle different types of server responses.
        Delegate to appropriate handlers & requests.

        Parameters:
                data: an unparsed string of either our custom protocol or a JSON protocol.
        """
        # Handle JSON and our custom protocol separately.
        if isJSON:
            # Break down the messages into an array if there are multiple.
            decoded_data = ServerRequest.decode_multiple_json(data)
            # Deserialize each object to convert it into the proper data type.
            messages = [ServerRequest.parse_serialized_data(msg, isJSON) for msg in decoded_data]
            logger.info(f"Parsed JSON response into the following messages from server: {messages}")
        else:
            messages = [ServerRequest.parse_serialized_data(msg, isJSON) for msg in data.split('∞') if msg.strip()]
            logger.info(f"Parsed custom protocol into the following messages from server: {messages}")

        # If there are multiple messages in one response from the server, such as
        # in the case of multiple new unread messages, handle each individually.
        for message in messages:
            arguments = message["arguments"]

            # If the user has completed a successful login, handle it first.
            if message["opcode"] == "LOGIN_SUCCESS":
                username = arguments[1]
                all_users = arguments[3:]
                logger.info(f"Sucessfully logged in as: {username}. Available users: {all_users}")

                # self.root.after(0, lambda: self.show_chat_ui(username, all_users))
                # Create chat UI synchronously
                self.show_chat_ui(username, all_users)
                # Let the UI update
                self.root.update()
                break  # Exit after handling login
            elif message["opcode"] == "LOGIN_FAILED":
                error_message = arguments[0]
                logger.info(f"Login rejected with error message: {error_message}")
                messagebox.showinfo(f"Login Rejected", f"Unable to verify account - {error_message}")
            
            # Handle registration of new users.
            elif message["opcode"] == "REGISTER_SUCCESS":
                logger.info(f"Registration succeeded.")
                messagebox.showinfo("Registration Succeeded.", "Please proceed to login.")
            elif message["opcode"] == "REGISTER_FAILED":
                error_message = arguments[0]
                logger.info(f"Registration failed with error message: {error_message}")
                messagebox.showinfo("Registration Failed", f"{error_message}")


        # Handle responses from the server.
        for message in messages: 
            op_code = message["opcode"]
            arguments = message["arguments"]
        
            if op_code == "SEND_MESSAGE":
                # TODO: I think we can delete username here?
                username = arguments[0]
                # Display chat message
                if hasattr(self, 'chat_ui'):
                    self.root.after(0, lambda: self.chat_ui.display_message(arguments[1], arguments[2]))
            
            elif op_code == "DELETE_ACCOUNT_SUCCESS":
                messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
                self.show_login_ui()

            elif op_code == "DELETE_MESSAGE":
                # TODO: complete
                # Here we need to determine which message in the UI to delete.
                # message_uuid = parts[3]
                # sender = parts[4]
                # recipient = parts[5]
                print("to be implemented")

            elif op_code == "NEW_MESSAGE":
                    logger.info(f"Received new message: {message}")
                    # Update the UI to display the new message.
                    if hasattr(self, 'chat_ui'):
                        sender = arguments[0]
                        message = arguments[2]
                        self.root.after(0, lambda s=sender, m=message: 
                            self.chat_ui.display_message(s, m))
                    else:
                        logger.warning("Message received before chat UI was ready")
            
            elif op_code == "RECEIVE_MESSAGE":
                logger.info(f"Received message with details: {arguments}")
                if hasattr(self, 'chat_ui'):
                    sender = arguments[0]
                    message = arguments[2]
                    self.root.after(0, lambda s=sender, m=message: 
                        self.chat_ui.display_message(s, m))

    # MARK: Sending Requests & Management
    def send_request(self, message):
        """
        Handle the sending of requests from the client to the server
        via the socket.

        Parameters:
                message: a serialized string ready to be sent over the wire
        """
        try:
            if not self.connectedWithServer:
                self.establishServerConnection()
            
            # If established successfully, then send request
            self.socketConnection.send(message.encode('utf-8'))
            logger.info(f"Sent request to server: {message.encode()}")
        except Exception as e:
            logger.error(f"Failed to send request to server for request {message}. Failed with error {e}")

    def run(self):
        """Start the application."""
        try:
            self.root.mainloop()
        finally:
            # Cleanup when window is closed
            self.running = False
            if self.socketConnection:
                self.socketConnection.close()

# MARK: Run the client & handle command-line arguments.
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Client')

    # Add arguments
    parser.add_argument(
        '--host',
        default='localhost',
        help='Server hostname or IP (default: localhost)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Server port (default: 5001)'
    )
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    # Create and run client
    try:
        client = Client(host=args.host, port=args.port)
        client.run()
    except Exception as e:
        print(f"Error starting client: {e}")