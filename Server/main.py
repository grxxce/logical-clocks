import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc
from auth_handler import AuthHandler
from database import DatabaseManager
from collections import defaultdict

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MessageServerServicer_to_server(MessageServer(), server)
    server.add_insecure_port('[::]:5001')
    server.start()
    print("Server started on port 5001")
    server.wait_for_termination()

class MessageServer(service_pb2_grpc.MessageServerServicer):

    def __init__(self):
        self.active_clients = {}
        self.pending_messages = defaultdict(list)
        self.message_queue = defaultdict(list)
    
    def Register(self, request, context):
        try:
            
            status, message = AuthHandler.register_user(request.username, request.password, request.email)
            
            if status:
                status_message = service_pb2.RegisterResponse.RegisterStatus.SUCCESS
                return service_pb2.RegisterResponse(
                    status=status_message, 
                    message=message)
            else:
                return service_pb2.RegisterResponse(
                    status=status, 
                    message=message)
        except:
            status = service_pb2.RegisterResponse.RegisterStatus.FAILURE
            return service_pb2.RegisterResponse(
                status=status, 
                message="User registration failed")
        
    def Login(self, request, context):
        try:
            response, message = AuthHandler.authenticate_user(request.username, request.password)
            
            if response:
                status_message = service_pb2.LoginResponse.LoginStatus.SUCCESS
                return service_pb2.LoginResponse(
                    status=status_message, 
                    message=message)
            else:
                status = service_pb2.LoginResponse.LoginStatus.FAILURE
                return service_pb2.LoginResponse(
                    status=status, 
                    message=message)
        except:
            status_message = service_pb2.LoginResponse.LoginStatus.FAILURE
            return service_pb2.LoginResponse(
                status=status_message, 
                message="User login failed")
    
    def GetUsers(self, request, context):
        try:
            users = DatabaseManager.get_contacts()
            for user in users:
                print("user: ", user)
                yield service_pb2.GetUsersResponse(
                    status=service_pb2.GetUsersResponse.GetUsersStatus.SUCCESS,
                    username=user
                )
        except:
            yield service_pb2.GetUsersResponse(
                status=service_pb2.GetUsersResponse.GetUsersStatus.FAILURE,
                username=""
            )

    def SendMessage(self, request, context):
        try:
            print("request.recipient: ", request.recipient)
            print("self.active_clients.keys(): ", self.active_clients.keys())
            message_request = service_pb2.Message(
                    sender=request.sender,
                    recipient=request.recipient,
                    message=request.message,
                    timestamp=request.timestamp
                )
            if request.recipient in self.active_clients.keys():
                print("found recipient")
                self.message_queue[request.recipient].append(message_request)
                print("sent to found recipient")
                return service_pb2.MessageResponse(
                    status=service_pb2.MessageResponse.MessageStatus.SUCCESS
                )
            else:
                print("no recipient found")
                self.pending_messages[request.recipient].append(message_request)
                print("added to queue")
                return service_pb2.MessageResponse(
                    status=service_pb2.MessageResponse.MessageStatus.SUCCESS
                )
        except Exception as e:
            print("Error sending message: ", e)
            pass


    def GetPendingMessage(self, request, context):
        try:
            counter = 0
            while self.pending_messages[request.username] and counter < request.inbox_limit:
                counter += 1
                pending_message = self.pending_messages[request.username].pop(0)
                yield service_pb2.PendingMessageResponse(
                    status=service_pb2.PendingMessageResponse.PendingMessageStatus.SUCCESS,
                    message=pending_message
                )
        except:
            yield service_pb2.PendingMessageResponse(
                status=service_pb2.PendingMessageResponse.PendingMessageStatus.FAILURE,
                message="failed to get pending messages"
            )
    
    def MonitorMessages(self, request, context):
        print("in monitor messages")
        try:
            # client_stream = context.peer()
            client_stream = context
            self.active_clients[request.username] = client_stream
            print("active clients: ", self.active_clients)
            while True:
                if self.message_queue[request.username]:
                    print("message queue", self.message_queue[request.username])
                    print("AHHHHH")
                    message = self.message_queue[request.username].pop(0)
                    print("popped message", message, type(message))
                    yield message
                    print("done")
        except Exception as e:
            print("Error: ", e)

    def DeleteAccount(self, request, context):
        try:
            status = DatabaseManager.delete_account(request.username)
            if status:
                return service_pb2.DeleteAccountResponse(
                    status=service_pb2.DeleteAccountResponse.DeleteAccountStatus.SUCCESS
                )
            else:
                return service_pb2.DeleteAccountResponse(
                    status=service_pb2.DeleteAccountResponse.DeleteAccountStatus.FAILURE
                )
        except:
            return service_pb2.DeleteAccountResponse(
                status=service_pb2.DeleteAccountResponse.DeleteAccountStatus.FAILURE
            )
    
    def SaveSettings(self, request, context):
        try:
            status = DatabaseManager.save_settings(request.username, request.setting)
            if status:
                return service_pb2.SaveSettingsResponse(
                    status=service_pb2.SaveSettingsResponse.SaveSettingsStatus.SUCCESS
                )
            else:
                return service_pb2.SaveSettingsResponse(
                    status=service_pb2.SaveSettingsResponse.SaveSettingsStatus.FAILURE
                )
        except:
            return service_pb2.SaveSettingsResponse(
                status=service_pb2.SaveSettingsResponse.SaveSettingsStatus.FAILURE
            )
    
    def GetSettings(self, request, context):
        try: 
            settings = DatabaseManager.get_settings(request.username)
            return service_pb2.GetSettingsResponse(
                status=service_pb2.GetSettingsResponse.GetSettingsStatus.SUCCESS,
                setting=settings
            )
        except:
            return service_pb2.GetSettingsResponse(
                status=service_pb2.GetSettingsResponse.GetSettingsStatus.FAILURE,
                setting=0
            )
    
if __name__ == "__main__":
    serve()