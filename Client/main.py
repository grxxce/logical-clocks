import socket
from UI.signup import LoginUI
from UI.chat import ChatUI
import tkinter as tk
from tkinter import ttk, messagebox
import re
import threading
import argparse
from Model.ServerRequest import ServerRequest
import json

# Add config file for versioning too!
version = 1
jsonSelected = False

class Client:
    def __init__(self,host, port):
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

        # Start socket connection in separate thread
        self.socket_thread = threading.Thread(target=self.establishServerConnection)
        self.socket_thread.daemon = True  # Thread will close when main program exits
        self.socket_thread.start()
    
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
        """Switch to chat UI."""
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
    
    
    def _handle_chat_message(self, recipient, message):
        """Handle sending chat messages."""
        print("handle_chat_message calling send_request")
        OP_CODE = "SEND_MESSAGE"
        if jsonSelected:
            chat_message = ServerRequest.serializeJSON(version, OP_CODE, [self.current_username, recipient, message])
        else:
            chat_message = ServerRequest.serialize(version, OP_CODE, [self.current_username, recipient, message])
        print("chat_message", chat_message)
        self.send_request(chat_message)

    
    def _handle_get_inbox(self):
        """Handle inbox refresh requests and return unread messages."""
        print("handle_get_inbox calling send_request")
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
        """Callback for login button."""
        OP_CODE = "LOGIN"
        if jsonSelected:
            message = ServerRequest.serializeJSON(version, OP_CODE, [username, password])
        else:
            message = ServerRequest.serialize(version, OP_CODE, [username, password])
        self.send_request(message)
        print("login message sent")

    def _handle_register(self, username, password, email):
        """Callback for register button."""
        OP_CODE = "REGISTER"
        if jsonSelected:
            message = ServerRequest.serializeJSON(version, OP_CODE, [username, password, email])
        else:
            message = ServerRequest.serialize(version, OP_CODE, [username, password, email])
        print("handle_register calling send_request")
        self.send_request(message)
    
    def _handle_save_settings(self, settings):
        """Handle saving user settings"""
        OP_CODE = "SETTINGS"
        if jsonSelected:
            settings_request = ServerRequest.serializeJSON(version, OP_CODE, [self.current_username, settings['message_history_limit']])
        else:
            settings_request = ServerRequest.serialize(version, OP_CODE, [self.current_username, settings['message_history_limit']])
        print("handle_save_settings calling send_request")
        self.send_request(settings_request)

    # MARK: Deletion
    def _handle_delete_account(self):
        """Handle account deletion"""
        OP_CODE = "DELETE_ACCOUNT"
        if jsonSelected:
            message = ServerRequest.serializeJSON(version, OP_CODE, [self.current_username])
        else:
            message = ServerRequest.serialize(version, OP_CODE, [self.current_username])
        self.send_request(message)
        # Close the chat window and return to login
        # self.root.destroy()

    def _handle_delete_message(self, message_uuid, sender, recipient):
        """Handle the deletion of messages on both a sender & recipients' devices.
           Send a message to the server asking to delete one or more messages from both clients."""
        op_code = "DELETE_MESSAGE"
        if jsonSelected:
            delete_request = ServerRequest.serializeJSON(version, op_code, [message_uuid, sender, recipient])
        else:
            delete_request = ServerRequest.serialize(version, op_code, [message_uuid, sender, recipient])
        self.send_request(delete_request)

    def establishServerConnection(self):
        try: 
            print("Starting socket connection")
            self.socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.host, self.port)
            print("server address: ", server_address)

            # Connect to the server
            self.socketConnection.connect(server_address)
            print("Connected to the server")
            self.socketConnection.setblocking(False)
            # Send data to the server
            self.connectedWithServer = True
            while self.running:
                try:
                    data = self.socketConnection.recv(1024)
                    if data:
                        decoded_data = data.decode('utf-8')
                        print('Received', repr(decoded_data))
                        if jsonSelected:
                            self.handle_server_responseJSON(decoded_data)
                        else:
                            self.handle_server_response(decoded_data)
                except socket.error:
                    continue
        
        except Exception as e:
            print(f"Socket error: {e}")
        
        finally:
            if self.socketConnection:
                self.socketConnection.close()

    def handle_server_responseJSON(self, data):
        """Handle different types of server responses."""
        print("JSON data", data)
        messages = json.loads(data)

        for message in messages:
            version = message["version"]
            op_code = message["opcode"]
            arguments = message["arguments"]
            if op_code == "LOGIN_SUCCESS":
                username = arguments[0]
                all_users = arguments[2:]  # Get users list
                print(f"Logged in as: {username}")
                print(f"Available users: {all_users}")
                
                # self.root.after(0, lambda: self.show_chat_ui(username, all_users))
                # Create chat UI synchronously
                self.show_chat_ui(username, all_users)
                # Let the UI update
                self.root.update()
                break  # Exit after handling login
            
        for message in messages:   
            op_code = message["opcode"] 
            arguments = message["arguments"]
            if op_code == "SEND_MESSAGE":
                # Display chat message
                if hasattr(self, 'chat_ui'):
                    self.root.after(0, lambda: self.chat_ui.display_message(message['version'], op_code))
            
            elif op_code == "DELETE_ACCOUNT_SUCCESS":
                messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
                self.show_login_ui()

            elif op_code == "DELETE_MESSAGE":
                # Here we need to determine which message in the UI to delete.
                # message_uuid = parts[3]
                # sender = parts[4]
                # recipient = parts[5]
                tbd = 0

            elif op_code == "NEW_MESSAGE":
                    print("Received new message:", message)
                    print("Has chat UI:", hasattr(self, 'chat_ui'))
                    
                    if hasattr(self, 'chat_ui'):
                        sender = arguments[0]
                        message = arguments[2]
                        self.root.after(0, lambda s=sender, m=message: 
                            self.chat_ui.display_message(s, m))
                    else:
                        print("Warning: Message received before chat UI was ready")
            
            elif op_code == "RECEIVE_MESSAGE":
                print("Received message:", message)
                if hasattr(self, 'chat_ui'):
                    sender = arguments[0]
                    message = arguments[2]
                    self.root.after(0, lambda s=sender, m=message: 
                        self.chat_ui.display_message(s, m))

    def handle_server_response(self, data):
        """Handle different types of server responses."""
        messages = [msg for msg in data.split('∞') if msg.strip()]

        for message in messages:
            parts = message.split('§')
            if parts[2] == "LOGIN_SUCCESS":
                username = parts[4]
                all_users = parts[6:]  # Get users list
                print(f"Logged in as: {username}")
                print(f"Available users: {all_users}")
                
                # self.root.after(0, lambda: self.show_chat_ui(username, all_users))
                # Create chat UI synchronously
                self.show_chat_ui(username, all_users)
                # Let the UI update
                self.root.update()
                break  # Exit after handling login
            
        print("messages", messages)
        for message in messages:    
            parts = message.split('§')
        
            if parts[2] == "SEND_MESSAGE":
                # Display chat message
                if hasattr(self, 'chat_ui'):
                    self.root.after(0, lambda: self.chat_ui.display_message(parts[1], parts[2]))
            
            elif parts[2] == "DELETE_ACCOUNT_SUCCESS":
                messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
                self.show_login_ui()

            elif parts[2] == "DELETE_MESSAGE":
                # Here we need to determine which message in the UI to delete.
                message_uuid = parts[3]
                sender = parts[4]
                recipient = parts[5]

            elif parts[2] == "NEW_MESSAGE":
                    print("Received new message:", parts)
                    print("Has chat UI:", hasattr(self, 'chat_ui'))
                    
                    if hasattr(self, 'chat_ui'):
                        sender = parts[3]
                        message = parts[5]
                        self.root.after(0, lambda s=sender, m=message: 
                            self.chat_ui.display_message(s, m))
                    else:
                        print("Warning: Message received before chat UI was ready")
            
            elif parts[2] == "RECEIVE_MESSAGE":
                print("Received message:", parts)
                if hasattr(self, 'chat_ui'):
                    sender = parts[3]
                    message = parts[5]
                    self.root.after(0, lambda s=sender, m=message: 
                        self.chat_ui.display_message(s, m))
        
    # Socket Connections & Management
    def send_request(self, message):
        try:
            if not self.connectedWithServer:
                self.establishServerConnection()
            
            # If established successfully, then send request
            print("sending_request sending: ", message.encode())
            # self.socketConnection.send(message.encode('utf-8'))
            self.socketConnection.send(message.encode('utf-8'))
        
        except:
            print("Exception in send_request")

    def run(self):
        """Start the application."""
        try:
            self.root.mainloop()
        finally:
            # Cleanup when window is closed
            self.running = False
            if self.socketConnection:
                self.socketConnection.close()


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