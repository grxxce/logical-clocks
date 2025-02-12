import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatUI:
    def __init__(self, root, callbacks, username, all_users):
        self.root = root
        self.username = username
        self.all_users = all_users
        
        # Store callbacks
        self.send_message_callback = callbacks.get('send_message')
        # self.search_users_callback = callbacks.get('search_users')
        self.get_inbox_callback = callbacks.get('get_inbox')
        self.save_settings_callback = callbacks.get('save_settings')
        self.delete_account_callback = callbacks.get('delete_account')
        
        # Configure the window
        self.root.title(f"Chat - {username}")
        self.root.geometry("1000x700")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        self.style.configure('TEntry', font=('Arial', 11))
        self.style.configure('TButton', font=('Arial', 11))
        
        self.create_widgets()
        self._refresh_inbox()  # Load initial inbox

        self.update_search_results(
            [user for user in all_users if user != username]
        )
        
    def create_widgets(self):
        # Main container with two columns
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Column (Search, Inbox, Settings)
        self.left_column = ttk.Frame(self.main_frame, width=250)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        self.left_column.pack_propagate(False)  # Maintain width
        
        # Create search panel (top of left column)
        self.create_search_panel()
        
        # Create inbox panel (middle of left column)
        self.create_inbox_panel()
        
        # Create settings panel (bottom of left column)
        self.create_settings_panel()
        
        # Right Column (Chat Area)
        self.create_chat_panel()
        
    def create_search_panel(self):
        """Create the search panel at the top of left column"""
        self.search_frame = ttk.LabelFrame(self.left_column, text="Search Users", padding="5")
        self.search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search input
        self.search_var = tk.StringVar()
        # Fix: Change 'w' to 'write' and use trace_add instead of trace
        self.search_var.trace_add('write', self._on_search_change)
        
        self.search_input = ttk.Entry(
            self.search_frame,
            textvariable=self.search_var,
            font=('Arial', 11)
        )
        self.search_input.pack(fill=tk.X, pady=(0, 5))
        
        # Search results
        self.search_results = tk.Listbox(
            self.search_frame,
            height=6,
            font=('Arial', 11),
            selectmode=tk.SINGLE
        )
        self.search_results.pack(fill=tk.X)
        self.search_results.bind('<<ListboxSelect>>', self._on_user_select)
    
    def create_inbox_panel(self):
        """Create the inbox panel below search panel"""
        self.inbox_frame = ttk.LabelFrame(self.left_column, text="Inbox", padding="5")
        self.inbox_frame.pack(fill=tk.BOTH, expand=True)
        
        # Inbox list
        self.inbox_list = tk.Listbox(
            self.inbox_frame,
            selectmode=tk.SINGLE,
            font=('Arial', 11)
        )
        self.inbox_list.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.inbox_list.bind('<<ListboxSelect>>', self._on_inbox_select)
        
        # Refresh button
        ttk.Button(
            self.inbox_frame,
            text="Refresh Inbox",
            command=self._refresh_inbox
        ).pack(fill=tk.X)
    
    def create_chat_panel(self):
        """Create the chat panel (right side)"""
        self.chat_frame = ttk.LabelFrame(self.main_frame, text="Select a conversation", padding="5")
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Message input area
        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X)
        
        self.message_input = ttk.Entry(
            self.input_frame,
            font=('Arial', 11)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_input.bind('<Return>', lambda e: self._handle_send())
        
        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self._handle_send
        )
        self.send_button.pack(side=tk.RIGHT)
        
    def _handle_send(self):
        """Handle sending a message"""
        print("_handle_send is sending message")
        message = self.message_input.get().strip()

        # Checks if recipient is set
        if message and hasattr(self, 'selected_recipient'):
            print("sending:", self.selected_recipient, message)
            self.send_message_callback(self.selected_recipient, message)
            self.message_input.delete(0, tk.END)
    
    def _on_search_change(self, *args):
        """Handle search input changes"""
        search_text = self.search_var.get().strip()
        # if search_text:
            # Use callback to filter users
            # results = self.search_users_callback(search_text)
        # else:
            # Show all users except current user when search is empty
        results = [user for user in self.all_users if user != self.username]
        
        self.update_search_results(results)
    
    def _on_user_select(self, event):
        """Handle user selection from search results"""
        selection = self.search_results.curselection()
        if selection:
            self.selected_recipient = self.search_results.get(selection[0])
            self.chat_display.configure(state='normal')
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.configure(state='disabled')
            self.chat_frame.configure(text=f"Chat with {self.selected_recipient}")
    
    def _on_inbox_select(self, event):
        """Handle inbox conversation selection"""
        selection = self.inbox_list.curselection()
        if selection:
            self.selected_recipient = self.inbox_list.get(selection[0])
            self.chat_frame.configure(text=f"Chat with {self.selected_recipient}")
            # Load chat history here
    
    def _refresh_inbox(self):
        """Refresh inbox conversations"""
        conversations = self.get_inbox_callback()
        self.inbox_list.delete(0, tk.END)
        for conv in conversations:
            self.inbox_list.insert(tk.END, conv)
    
    def display_message(self, from_user, message):
        """Display a message in the chat area"""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"{from_user}: {message}\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
    
    def update_search_results(self, users):
        """Update the search results listbox"""
        self.search_results.delete(0, tk.END)
        for user in users:
            self.search_results.insert(tk.END, user)


    def create_settings_panel(self):
        """Create the settings panel at the bottom of left column"""
        self.settings_frame = ttk.LabelFrame(self.left_column, text="Settings", padding="5")
        self.settings_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Message history limit setting
        history_frame = ttk.Frame(self.settings_frame)
        history_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            history_frame,
            text="Messages to show:",
            font=('Arial', 10)
        ).pack(side=tk.LEFT)
        
        self.history_var = tk.StringVar(value="50")  # Default value
        history_spinbox = ttk.Spinbox(
            history_frame,
            from_=10,
            to=200,
            width=5,
            textvariable=self.history_var,
            command=self._on_history_change
        )
        history_spinbox.pack(side=tk.RIGHT)
        
        # Save Settings Button
        ttk.Button(
            self.settings_frame,
            text="Save Settings",
            command=self._save_settings
        ).pack(fill=tk.X, pady=(0, 5))
        
        # Separator
        ttk.Separator(self.settings_frame).pack(fill=tk.X, pady=5)
        
        # Danger Zone
        danger_frame = ttk.LabelFrame(self.settings_frame, text="Danger Zone", padding="5")
        danger_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Delete Account Button
        delete_button = ttk.Button(
            danger_frame,
            text="Delete Account",
            style='Danger.TButton',
            command=self._confirm_delete_account
        )
        delete_button.pack(fill=tk.X)
        
        # Configure danger button style
        self.style.configure('Danger.TButton', 
                           foreground='red',
                           font=('Arial', 11, 'bold'))
    
    def _on_history_change(self):
        """Handle message history limit change"""
        try:
            value = int(self.history_var.get())
            if value < 10:
                self.history_var.set("10")
            elif value > 200:
                self.history_var.set("200")
        except ValueError:
            self.history_var.set("50")  # Reset to default if invalid
    
    def _save_settings(self):
        """Save user settings"""
        try:
            history_limit = int(self.history_var.get())
            # Call callback to save settings
            if hasattr(self, 'save_settings_callback'):
                self.save_settings_callback({
                    'message_history_limit': history_limit
                })
            messagebox.showinfo("Success", "Settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid settings values")
    
    def _confirm_delete_account(self):
        """Show confirmation dialog before deleting account"""
        if messagebox.askyesno("Confirm Delete", 
                             "Are you sure you want to delete your account?\n"
                             "This action cannot be undone!",
                             icon='warning'):
            if hasattr(self, 'delete_account_callback'):
                self.delete_account_callback()