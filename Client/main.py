import socket
from UI.signup import LoginUI
from UI.chat import ChatUI
import tkinter as tk
from tkinter import ttk, messagebox
import re
import threading

# Add config file for versioning too!
version = 1

class Client:
    def __init__(self, base_url='http://localhost:5002'):
        self.connectedWithServer = False
        self.socketConnection = None
        self.base_url = base_url
        self.running = True # flag to control socket thread
        
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
        print("username", self.current_username)
        chat_request = f"SEND_MESSAGE§{self.current_username}§{recipient}§{message}"
        chat_message = f"{version}§{len(chat_request)}§{chat_request}"
        print("chat_message", chat_message)
        self.send_request(chat_message)

    
    def _handle_get_inbox(self):
        """Handle inbox refresh requests"""
        # inbox_request = f"INBOX§{self.current_username}"
        # print("handle_get_inbox calling send_request")
        # self.send_request(inbox_request)
        # You'll need to implement response handling
        return ["conversation1", "conversation2"]  # Placeholder

    def _handle_login(self, username, password):
        """Callback for login button."""
        login_request = f"LOGIN§{username}§{password}"
        message = f"{version}§{len(login_request)}§{login_request}"
        print("handle_login calling send_request")
        self.send_request(message)
        print("login message sent")
    
    def _handle_register(self, username, password, email):
        """Callback for register button."""
        register_request = f"REGISTER§{username}§{password}§{email}"
        message = f"{version}§{len(register_request)}§{register_request}"
        print("handle_register calling send_request")
        self.send_request(message)
    
    def _handle_save_settings(self, settings):
        """Handle saving user settings"""
        settings_request = f"SETTINGS§{self.current_username}§{settings['message_history_limit']}"
        print("handle_save_settings calling send_request")
        self.send_request(settings_request)

    def _handle_delete_account(self):
        """Handle account deletion"""
        delete_request = f"DELETE_ACCOUNT§{self.current_username}"
        message = f"{version}§{len(delete_request)}§{delete_request}"
        self.send_request(message)
        # Close the chat window and return to login
        # self.root.destroy()

    def establishServerConnection(self):
        try: 
            print("Starting socket connection")
            self.socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # TODO: dont' hardcode this
            PORT = 5001
            hostname = socket.gethostname()
            HOST = socket.gethostbyname(hostname) 
            server_address = (HOST, PORT)
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
                        self.handle_server_response(decoded_data)
                except socket.error:
                    continue
        
        except Exception as e:
            print(f"Socket error: {e}")
        
        finally:
            if self.socketConnection:
                self.socketConnection.close()
    
    def handle_server_response(self, data):
        """Handle different types of server responses."""
        parts = data.split('§')
        if parts[2] == "LOGIN_SUCCESS":
            # Switch to chat UI on the main thread
            username = parts[4]
            print("username supposed", username)
            all_users = parts[6:]  # Store all users for searching
            print(f"Logged in as: {username}")
            print(f"Available users: {all_users}")
            
            # Switch to chat UI and pass all users
            self.root.after(0, lambda: self.show_chat_ui(username, all_users))
        elif parts[2] == "SEND_MESSAGE":
            # Display chat message
            if hasattr(self, 'chat_ui'):
                self.root.after(0, lambda: self.chat_ui.display_message(parts[1], parts[2]))
        elif parts[2] == "DELETE_ACCOUNT_SUCCESS":
            messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
            self.show_login_ui()
        
    # Socket Connections & Management
    def send_request(self, message):
        try:
            if not self.connectedWithServer:
                self.establishServerConnection()
            
            # If established successfully, then send request
            print("sending_request sending: ", message.encode())
            self.socketConnection.send(message.encode('utf-8'))
            # sent = self.socketConnection.send(message.encode('utf-8'))
            # data.outb = data.outb[sent:]
        
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


if __name__ == "__main__":
    client = Client()
    client.run()