import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc
from google.protobuf import empty_pb2
from datetime import datetime

from UI.signup import LoginUI
from UI.chat import ChatUI
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# Configure logging set-up. We want to log times & types of logs, as well as
# function names & the subsequent message.
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = service_pb2_grpc.MessageServerStub(self.channel)
        self.root = tk.Tk()
        self.show_login_ui()

        self.messageObservation = threading.Thread(target=self._monitor_messages, daemon=True)

    def run(self):
        try: 
            self.root.mainloop()
        finally:
            #todo: remove user from active clients
            pass

        # MONITOR
        # responses = stub.MonitorMessages(service_pb2.MonitorMessagesRequest(username="testuser"))
        # _ = stub.SendMessage(service_pb2.Message(
        #     sender="testuser",
        #     recipient="testuser2",
        #     message="Hello, world 1! a real new mesage",
        #     timestamp="time"
        # ))

        # GET PENDING MESSAGE
        # responses = stub.GetPendingMessage(service_pb2.PendingMessageRequest(username="testuser2", inbox_limit=1))

        # DELETE ACCOUNT
        # response = stub.DeleteAccount(service_pb2.DeleteAccountRequest(username="testuser2"))
        # responses = stub.GetUsers(service_pb2.GetUsersRequest(username="testuser2"))

        # SAVE SETTINGS
        # _ = stub.SaveSettings(service_pb2.SaveSettingsRequest(username="testuser", setting=100))
        # GET SETTINGS
        # response = stub.GetSettings(service_pb2.GetSettingsRequest(username="testuser"))
        # print("response: ", response)

        # ITERATE THROUGH STREAM
        # try:
        #     for response in responses:
        #         print("response: ", response)
        #         # Access specific fields from the GetUsersResponse message
        # except Exception as e:
        #     print("error: ", e)
        

    def show_login_ui(self):
        """Show the login UI."""
        for widget in self.root.winfo_children():
            widget.destroy() 
        self.ui = LoginUI(
            root=self.root,
            login_callback=self._handle_login,
            register_callback=self._handle_register
        )

    def show_chat_ui(self, username, settings, all_users, pending_messages):
        """
        Create the initial chat UI
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.current_user = username

        callbacks = {
            'send_message': self._handle_send_message,
            'get_inbox': self._handle_get_inbox,
            'save_settings': self._handle_save_settings,
            'delete_account': self._handle_delete_account
        }
        
        self.chat_ui = ChatUI(
            root=self.root,
            callbacks=callbacks,
            username=username,
            all_users=all_users, 
            pending_messages=pending_messages,
            settings=settings,
        )

        self.messageObservation.start()

    def _handle_login(self, username, password):
        response = self.stub.Login(service_pb2.LoginRequest(username=username, password=password))
        logger.info(f"Client {username} sent login request to server.")
        if response.status == service_pb2.LoginResponse.LoginStatus.SUCCESS:
            settings, all_users, pending_messages = self._handle_setup(username)
            self.show_chat_ui(username, settings, all_users, pending_messages)
        else:
            messagebox.showerror("Login Failed", response.message)
    
    def _handle_register(self, username, password, email):
        response = self.stub.Register(service_pb2.RegisterRequest(username=username, password=password, email=email))
        logger.info(f"Client {username} sent register request to server.")
        if response.status == service_pb2.RegisterResponse.RegisterStatus.SUCCESS:
            settings, all_users, pending_messages = self._handle_setup(username)
            self.show_chat_ui(username, settings, all_users, pending_messages)
        else:
            messagebox.showerror("Register Failed", response.message)

    def _handle_setup(self, username):
        '''
        After successful registration or login, handle:
        (1) Allow user to monitor messages
        (2) Fetch and return list of online users
        (3) Fetch and return user's settings
        (4) Fetch and return list of pending messages
        '''
        # _ = self.stub.MonitorMessages(service_pb2.MonitorMessagesRequest(username=username))

        user_responses = self.stub.GetUsers(service_pb2.GetUsersRequest(username=username))            
        all_users = [user.username for user in user_responses]

        settings_response = self.stub.GetSettings(service_pb2.GetSettingsRequest(username=username))
        settings = settings_response.setting

        pending_responses = self.stub.GetPendingMessage(service_pb2.PendingMessageRequest(username=username, inbox_limit=settings))
        pending_messages = [pending_message for pending_message in pending_responses]
        # pending_messages = ""
                
        return settings, all_users, pending_messages

    def _handle_send_message(self, recipient, message):
        try: 
            print("attempting to send messages")

            message_request = service_pb2.Message(
                sender=self.current_user,
                recipient=recipient,
                message=message,
                timestamp=str(datetime.now())
            )
            response = self.stub.SendMessage(message_request)

            if response.status == service_pb2.MessageResponse.MessageStatus.SUCCESS:
                print("message sent successfully")
            else:
                print("message not sent")

        except Exception as e:
            print("error: ", e)
    
    def _monitor_messages(self):
        try:

            message_iterator = self.stub.MonitorMessages(service_pb2.MonitorMessagesRequest(username=self.current_user))
            while True:
                try:
                    print("AHH")
                    for message in message_iterator:
                        self.chat_ui.display_message(from_user=message.sender, message=message.message)
                except Exception as e:
                    print("Error in monitor message:", e)
        except Exception as e:
            print("Failed with error in monitor messages:", e)

    def _handle_get_inbox(self):
        print("getting inbox")
        settings_response = self.stub.GetSettings(service_pb2.GetSettingsRequest(username=self.current_user))
        settings = settings_response.setting
        
        print("getting pending messages")
        responses = self.stub.GetPendingMessage(service_pb2.PendingMessageRequest(username=self.current_user, inbox_limit=settings))

        pending_messages = {}
        for response in responses:
            if response.message.sender not in pending_messages:
                pending_messages[response.message.sender] = []
            pending_messages[response.message.sender].append(
                {
                    'sender': response.message.sender,
                    'message': response.message.message,
                    'timestamp': response.message.timestamp
                }
            )
        print("these are the pending messages:", pending_messages)
        return pending_messages
    
    def _handle_save_settings(self, settings):
        response = self.stub.SaveSettings(service_pb2.SaveSettingsRequest(username=self.current_user, setting=settings))

    def _handle_delete_account(self):
        response = self.stub.DeleteAccount(service_pb2.DeleteAccountRequest(username=self.current_user))
        if response.status == service_pb2.DeleteAccountResponse.DeleteAccountStatus.SUCCESS:
            self.root.destroy()
        else:
            messagebox.showerror("Delete Account Failed", response.message)


if __name__ == "__main__":
    client = Client(host="localhost", port=5001)
    client.run()