import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MessageServerServicer_to_server(MessageServer(), server)
    server.add_insecure_port('[::]:5001')
    server.start()
    print("Server started on port 5001")
    server.wait_for_termination()

class MessageServer(service_pb2_grpc.MessageServerServicer):
    def Register(self, request, context):
        try:
            return service_pb2.RegisterResponse(
                status=service_pb2.RegisterStatus.SUCCESS, 
                message="User registered successfully")
        except:
            return service_pb2.RegisterResponse(
                status=service_pb2.RegisterStatus.FAILED, 
                message="User registration failed")
        
    def Login(self, request, context):
        try:
            return service_pb2.LoginResponse(
                status=service_pb2.LoginStatus.SUCCESS, 
                message="User logged in successfully")
        except:
            return service_pb2.LoginResponse(
                status=service_pb2.LoginStatus.FAILED, 
                message="User login failed")
    
    def GetUsers(self, request, context):
        pass   

    def SendMessage(self, request, context):
        pass

    def GetPendingMessage(self, request, context):
        pass
    
    def MonitorMessages(self, request, context):
        pass

    def DeleteAccount(self, request, context):
        pass
    
    def SaveSettings(self, request, context):
        pass

    def GetSettings(self, request, context):
        pass
    
    
if __name__ == "__main__":
    serve()