import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatUI:
    def __init__(self, root, send_message_callback, username):
        self.root = root
        self.send_message_callback = send_message_callback
        self.username = username
        
        # Configure the window
        self.root.title(f"Chat - {username}")
        self.root.geometry("800x600")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            height=20,
            state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Message input area
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.message_input = ttk.Entry(self.input_frame)
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self._handle_send
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.message_input.bind('<Return>', lambda e: self._handle_send())
    
    def _handle_send(self):
        """Handle send button click or Enter key."""
        message = self.message_input.get().strip()
        if message:
            self.send_message_callback(message)
            self.message_input.delete(0, tk.END)
    
    def display_message(self, username, message):
        """Display a message in the chat area."""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"{username}: {message}\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)  # Auto-scroll to bottom