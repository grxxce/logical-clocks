import socket
from UI.signup import LoginClient
import tkinter as tk


# Main login UI — this is HTTP connection

# Another UI/Connection Attempt

import tkinter as tk
from tkinter import ttk, messagebox
import re


# Add config file for versioning too!
version = 1

class Client:
    def __init__(self, base_url='http://localhost:5002'):
        self.connectedWithServer = False
        self.socketConnection = None
        self.base_url = base_url
        
        self.root = tk.Tk()
        self.root.title("Login System")
        self.root.geometry("500x700")
        self.root.resizable(True, True)
        
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))
        self.style.configure('TEntry', font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12))
        
        self.create_login_widgets()

    def establishServerConnection(self):
        try: 
            print("Starting socket connection")
            self.socketConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # TODO: dont' hardcode this
            PORT = 5001
            hostname = socket.gethostname()
            HOST = socket.gethostbyname(hostname) 
            server_address = (HOST, PORT)

            # Connect to the server
            try:
                self.socketConnection.connect(server_address)
                print("Connected to the server")
                self.socketConnection.setblocking(False)
                # Send data to the server
                self.connectedWithServer = True
                while True:
                    # try:
                    data = self.socketConnection.recv(1024)
                    print('Received', repr(data))
                    # except socket.error as e:
                    #     print(f"error: {e}")
            except socket.error as e:
                print(f"Connection to server failed with error: {e}")
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, closing connection")
            self.socketConnection.close()


    # Socket Connections & Management
    def send_request(self, message):
        try:
            print("length", len(message))
            if not self.connectedWithServer:
                self.establishServerConnection()
            # If established successfully, then send request
            self.socketConnection.send(message.encode())
            self.handle_responses(self)
        except:
            print("AHHh")

    def handle_responses(self):
        # while True:
        #     data = self.socketConnection.recv(1024)
        #     print(f"Received: {data.decode()}")
        # Infinitely listen to the socket
        while True:
            # Look at all currently registered sockets, and if we get an event sent, it selects it & then we handle the events.
            events = selector.select(timeout=None)
            # event_count += 1
            # print("events: ", event_count)
            for key, mask in events:
                if key.data is None:
                    print("accepting connection!")
                    accept_connection(key.fileobj)
                else:
                    # print("servicing connection")
                    service_connection(key, mask)


    # Login & Register Info
    def create_login_widgets(self):
        """Create and setup all GUI widgets."""
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="User Authentication System",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=20)
        
        # Login Frame
        self.login_frame = ttk.LabelFrame(self.main_frame, text="Login", padding="10")
        self.login_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.login_frame, text="Username:").pack(fill=tk.X, pady=5)
        self.login_username = ttk.Entry(self.login_frame)
        self.login_username.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.login_frame, text="Password:").pack(fill=tk.X, pady=5)
        self.login_password = ttk.Entry(self.login_frame, show="*")
        self.login_password.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            self.login_frame,
            text="Login",
            command=self.login
        ).pack(fill=tk.X, pady=10)
        
        # Register Frame
        self.register_frame = ttk.LabelFrame(self.main_frame, text="Register", padding="10")
        self.register_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(self.register_frame, text="Username:").pack(fill=tk.X, pady=5)
        self.register_username = ttk.Entry(self.register_frame)
        self.register_username.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.register_frame, text="Password:").pack(fill=tk.X, pady=5)
        self.register_password = ttk.Entry(self.register_frame, show="*")
        self.register_password.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.register_frame, text="Confirm Password:").pack(fill=tk.X, pady=5)
        self.register_confirm = ttk.Entry(self.register_frame, show="*")
        self.register_confirm.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.register_frame, text="Email:").pack(fill=tk.X, pady=5)
        self.register_email = ttk.Entry(self.register_frame)
        self.register_email.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            self.register_frame,
            text="Register",
            command=self.register
        ).pack(fill=tk.X, pady=10)

    def validate_email(self, email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
       

    def login(self):
        """Handle login button click."""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Protocol: LOGIN§username§password
        length = len(username)+len(password)+1
        message = f"{version}§LOGIN§{length}§{username}§{password}"
        self.send_request(message)
        print("login message sent")

    def register(self):
        """Handle register button click."""
        username = self.register_username.get().strip()
        password = self.register_password.get()
        confirm = self.register_confirm.get()
        email = self.register_email.get().strip()
        
        # Validation
        if not all([username, password, confirm, email]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Invalid email format")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        
        # Protocol: REGISTER§username§password§email
        length = len(username) + len(password) + len(email) + 2
        message = f"{version}§REGISTER§{length}§{username}§{password}§{email}"
        self.send_request(message)


client = Client()
client.root.mainloop()



# SOCKET CONNECTION CODE

# try: 
#     print("Starting socket connection")
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # TODO: dont' hardcode this
#     PORT = 5001
#     hostname = socket.gethostname()
#     HOST = socket.gethostbyname(hostname) 
#     server_address = (HOST, PORT)

#     # Connect to the server
#     try:
#         client_socket.connect(server_address)

#         # Send data to the server
#         print("Connected to the server")
#         message = "Hello from the client!"
#         client_socket.send(message.encode())

#         # Receive data from the server
#         data = client_socket.recv(1024)
#         print(f"Received: {data.decode()}")
#     except socket.error as e:
#         print(f"Connection to server failed with error: {e}")

# except KeyboardInterrupt:
#     print("Caught keyboard interrupt, closing connection")
#     client_socket.close()