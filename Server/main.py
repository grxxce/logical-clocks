import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc
from auth_handler import AuthHandler
from database import DatabaseManager

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
        self.pending_messages = {}
    
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
                status=status_meassage, 
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
            if request.recipient in self.active_clients:
                self.active_clients[request.recipient].send
        except:
            print("Error: ", e)
            pass


    def GetPendingMessage(self, request, context):
        pass
    
    def MonitorMessages(self, request, context):
        try:
            client_stream = context.peer()
            self.active_clients[request.username] = client_stream
            print("active clients: ", self.active_clients)
        except:
            print("Error: ", e)
            pass

    def DeleteAccount(self, request, context):
        pass
    
    def SaveSettings(self, request, context):
        pass

    def GetSettings(self, request, context):
        pass
    
    
if __name__ == "__main__":
    serve()