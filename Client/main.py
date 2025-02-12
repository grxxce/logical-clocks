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

    def show_chat_ui(self, username):
        """Switch to chat UI."""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.current_username = username
        self.chat_ui = ChatUI(
            root=self.root,
            send_message_callback=self._handle_chat_message,
            username=username
        )
    
    def _handle_chat_message(self, message):
        """Handle sending chat messages."""
        chat_message = f"CHAT§{self.current_username}§{message}"
        self.send_request(chat_message)

    def _handle_login(self, username, password):
        """Callback for login button."""
        length = len(username) + len(password) + 1
        message = f"{version}§LOGIN§{length}§{username}§{password}"
        self.send_request(message)
        print("login message sent")
    
    def _handle_register(self, username, password, email):
        """Callback for register button."""
        length = len(username) + len(password) + len(email) + 2
        message = f"{version}§REGISTER§{length}§{username}§{password}§{email}"
        self.send_request(message)
    

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
        if parts[0] == "LOGINSUCCESS":
            # Switch to chat UI on the main thread
            print("switching to chat ui")
            self.root.after(0, lambda: self.show_chat_ui(parts[1]))
        elif parts[0] == "CHAT":
            # Display chat message
            if hasattr(self, 'chat_ui'):
                self.root.after(0, lambda: self.chat_ui.display_message(parts[1], parts[2]))


    # Socket Connections & Management
    def send_request(self, message):
        try:
            if not self.connectedWithServer:
                self.establishServerConnection()
            # If established successfully, then send request
            self.socketConnection.send(message.encode())
            self.handle_responses(self)
        except:
            print("AHHh")

    def handle_responses(self):
        print("handling responses")
        while True:
            # Look at all currently registered sockets, and if we get an event sent, it selects it & then we handle the events.
            events = selector.select(timeout=None)
            # event_count += 1
            # print("events: ", event_count)
            for key, mask in events:
                if key.data is None:
                    print("accepting connection!")
                else:
                    print("servicing connection")

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