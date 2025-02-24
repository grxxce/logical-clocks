import grpc
from concurrent import futures
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc
from google.protobuf import empty_pb2
from datetime import datetime

def run():
    channel = grpc.insecure_channel('localhost:5001')
    stub = service_pb2_grpc.MessageServerStub(channel)

    # REGISTER
    # response = stub.Register(service_pb2.RegisterRequest(username="testuser2", password="testpassword", email="test@test.com"))

    # LOGIN
    # response = stub.Login(service_pb2.LoginRequest(username="testuser2", password="testpassword"))
    
    # GET USERS
    # responses = stub.GetUsers(service_pb2.GetUsersRequest(username="testuser2"))

    # SEND MESSAGE
    # stub.SendMessage(service_pb2.Message(sender="testuser2", recipient="testuser1", message="Hello, world!"))

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
    _ = stub.SaveSettings(service_pb2.SaveSettingsRequest(username="testuser", setting=100))
    # GET SETTINGS
    response = stub.GetSettings(service_pb2.GetSettingsRequest(username="testuser"))
    print("response: ", response)

    # ITERATE THROUGH STREAM
    # try:
    #     for response in responses:
    #         print("response: ", response)
    #         # Access specific fields from the GetUsersResponse message
    # except Exception as e:
    #     print("error: ", e)

if __name__ == "__main__":
    run()