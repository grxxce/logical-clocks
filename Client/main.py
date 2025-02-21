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
    response = stub.Register(service_pb2.RegisterRequest(username="testuser", password="testpassword", email="test@test.com"))
    print(response)

if __name__ == "__main__":
    run()