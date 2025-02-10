import tkinter as tk
from tkinter import ttk, messagebox
import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# TODO: HANDLE FAILED CONNECTIONS (NO RETURN)
# TODO: add a config file for the security + port 

class LoginClient:
    def __init__(self, base_url='http://localhost:5002'):
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
        
        self.create_widgets()

    def create_widgets(self):
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

    def send_request(self, message):
        """Send HTTP request to server using custom protocol."""
        try:
            print("length", str(len(message)))
            headers = {
                'Content-Type': 'text/plain',
                'Content-Length': str(len(message))
            }
            
            req = Request(self.base_url, message.encode('utf-8'), headers, method='POST')
            
            with urlopen(req) as response:
                return response.read().decode('utf-8')
                
        except HTTPError as e:
            return f"ERROR§HTTP Error: {str(e)}"
        except URLError as e:
            return "ERROR§Could not connect to server"
        except Exception as e:
            return f"ERROR§{str(e)}"

    def login(self):
        """Handle login button click."""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Protocol: LOGIN§username§password
        message = f"LOGIN§{username}§{password}"
        response = self.send_request(message)
        
        status, message = response.split('§', 1)
        if status == "SUCCESS":
            messagebox.showinfo("Success", message)
            # Here you could open a new window for the logged-in user
        else:
            messagebox.showerror("Error", message)

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
        message = f"REGISTER§{username}§{password}§{email}"
        response = self.send_request(message)
        
        status, message = response.split('§', 1)
        if status == "SUCCESS":
            messagebox.showinfo("Success", message)
            # Clear registration fields
            self.register_username.delete(0, tk.END)
            self.register_password.delete(0, tk.END)
            self.register_confirm.delete(0, tk.END)
            self.register_email.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)
