import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from proto import service_pb2
from proto import service_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:5001')
    stub = service_pb2_grpc.MessageServerStub(channel)
    # response = stub.Register(service_pb2.RegisterRequest(username="testuser2", password="testpassword", email="test@test.com"))
    # response = stub.Login(service_pb2.LoginRequest(username="testuser2", password="testpassword"))
    # print(response)
    responses = stub.GetUsers(service_pb2.GetUsersRequest(username="testuser2"))
    
    try:
        print("responses: ", responses)
        for response in responses:
            print(response)
    except Exception as e:
        print("error: ", e)

if __name__ == "__main__":
    run()