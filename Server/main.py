import sys
import os
import grpc
import datetime
import argparse
import logging
import socket # For retrieving local IP address only
from collections import defaultdict
from concurrent import futures
# Handle our file paths properly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proto import service_pb2
from proto import service_pb2_grpc


# MARK: Initialize Logger
# Configure logging set-up. We want to log times & types of logs, as well as
# function names & the subsequent message.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)

# MARK: MessageServer 
class MessageServer(service_pb2_grpc.MessageServerServicer):

    """
    The MessageServer class defines the service protocols defined in our
    proto/service.proto. This class provides vital functionalities that manage
    client conversations and allow clients to request services.
    """
        
    def __init__(self):
        self.active_clients = {}
        self.pending_messages = defaultdict(list)
        self.message_queue = defaultdict(list)

    def GetPendingMessage(self, request : service_pb2.PendingMessageRequest, context) -> service_pb2.PendingMessageResponse:
        """
        Streams messages that a user has missed upon an RPC request.

        Parameters:
            request (PendingMessageRequest): Contains the request info for retrieving pending messages.
                - username (str): The user who is requesting messages.
                - inbox_limit (int): The maximum number of messages to retrieve in one request.
            context (RPCContext): The RPC call context, containing information about the client.

        Yields (streams):
            PendingMessageResponse: A stream of responses containing the messages for the user.
                - status (PendingMessageStatus): SUCCESS if messages are successfully retrieved, FAILURE if not.
                - message (Message): The pending message in the form of a Message as outlined by our proto.

        Behavior with Exceptions:
            If an error occurs while retrieving or streaming pending messages, a failure response is sent to the client with an error message.
        """
        try:
            logger.info(f"Handling request from {request.username} to retrieve pending messages.")
            logger.info(f"Messages pending for {request.username}: {self.pending_messages[request.username]}")

            # Only send the number of messages that the user desires.
            while self.pending_messages[request.username]:
                pending_message = self.pending_messages[request.username].pop(0)
                yield service_pb2.PendingMessageResponse(
                    status=service_pb2.PendingMessageResponse.PendingMessageStatus.SUCCESS,
                    message=pending_message
                )
        except Exception as e:
            logger.error(f"Failed to stream pending messages to {request.username} with error: {e}")
            error_message = service_pb2.Message(sender="error", 
                                                recipient="error", 
                                                message=str(e), 
                                                timestamp=str(datetime.now()))
            yield service_pb2.PendingMessageResponse(
                status=service_pb2.PendingMessageResponse.PendingMessageStatus.FAILURE,
                message=error_message
            )

    # MARK: Message Handling
    def SendMessage(self, request : service_pb2.Message, context) -> service_pb2.MessageResponse:
        """
        Handles a client's RPC request to send a message to another client.

        Parameters:
            request (Message): Contains the message details.
                - sender (str): The username of the sender.
                - recipient (str): The username of the recipient.
                - message (str): The message being sent.
                - timestamp (str): The time when the message was created.
            context (RPCContext): The RPC call context, containing information about the client.

        Returns:
            MessageResponse: A response indicating the status of the message delivery.
                - status (MessageStatus): SUCCESS or FAILURE.

        Note on behavior:
            - If the recipient is active and has a valid streaming connection, the message is added to their message queue for immediate delivery.
            - If the recipient is inactive or unreachable, the message is added to the pending messages queue for later delivery when the recipient becomes active.
            - If an error occurs during the message sending process, a FAILURE message is sent to the client.
        """
        try:
            logger.info(f"Handling request to send a message from {request.sender} to {request.recipient} for message: {request.message}")
            message_request = service_pb2.Message(
                    sender=request.sender,
                    recipient=request.recipient,
                    message=request.message,
                    timestamp=request.timestamp
                )
            
            # If the other client is currently online, send the message instantly.
            if request.recipient in self.active_clients.keys():
                logger.info(f"The recipient {request.recipient} is active, now confirming they have a valid streaming connection.")
                
                # Verify that the connection is still active, or treat this like our pending messages.
                if not self.active_clients[request.recipient].is_active():
                    logger.info(f"The recipient {request.recipient} has become inactive. Removing them from active clients list.")
                    # Remove the disconnected client from the active list.
                    self.active_clients.pop(request.recipient)
                else:
                    logger.info(f"Message from {request.sender} added to queue for streaming to {request.recipient}.")
                    self.message_queue[request.recipient].append(message_request)
                    return service_pb2.MessageResponse(
                        status=service_pb2.MessageResponse.MessageStatus.SUCCESS
                    )
            
            # If the client is not active and reachable, add the message to the pending messages.
            self.pending_messages[request.recipient].append(message_request)
            return service_pb2.MessageResponse(status=service_pb2.MessageResponse.MessageStatus.SUCCESS)
        
        except Exception as e:
            logger.error(f"Failed to send message from {request.sender} to {request.recipient} with error: {e}")
            return service_pb2.MessageResponse(status=service_pb2.MessageResponse.MessageStatus.FAILURE)

    def MonitorMessages(self, request : service_pb2.MonitorMessagesRequest, context) -> service_pb2.Message:
        """
        Handles a client's RPC request to subscribe to updates about new messages.
        This service also handles adding and removing a client from the clients who are active and reachable.
        Clients will create a stream with the server through this monitor service, which will be stored in 
        self.active_clients.

        Parameters:
            request (MonitorMessagesRequest): Contains the client's details.
                - username (str): The username of the sender.
            context (RPCContext): The RPC call context, containing information about the client.

        Yields (stream):
            Message: The message that is to be delivered from a different client to the client who called this service.
        """
        try:
            logger.info(f"Handling client {request.username}'s request to monitor for messages.")
            
            # Check to ensure that this isn't creating a double connection.
            # This could happen if the client was lost and is restarting.
            if request.username in self.active_clients:
                # Remove it and start again
                self.active_clients.pop(request.username)
            
            # Add our client to our active clients and begin listening for messages
            # via a stream.
            client_stream = context
            self.active_clients[request.username] = client_stream
            
            while True:
                # If we have a message ready to send, verify our status and yield the message to the stream.
                if len(self.message_queue[request.username]) > 0:
                    if context.is_active():
                        message = self.message_queue[request.username].pop(0)
                        logger.info(f"Sending a message to {request.username}: {message.message}")
                        yield message
                    else:
                        logger.warning(f"Connection concerns with client {request.username}.")
        
        except Exception as e:
            logger.error(f"Failed to send a message or lost connection to client with error {e}")
        
        finally:
            # When the client's stream closes, remove them from the active clients.
            logger.info(f"Client disconnected with username: {request.username}")
            self.active_clients.pop(request.username)
    

# MARK: Server Initialization

def serve(ip, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_MessageServerServicer_to_server(MessageServer(), server)
    server.add_insecure_port(f'{ip}:{port}')
    server.start()
    logger.info(f"Server started on port {port} for ip {ip}")
    server.wait_for_termination()


# MARK: Command-line arguments.

# Validate an IP address
def validate_ip(value):
    try:
        # Try to convert the value to a valid IP address using socket
        socket.inet_aton(value)  # This will raise an error if not a valid IPv4 address
        return value
    except socket.error:
        raise argparse.ArgumentTypeError(f"Invalid IP address: {value}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Client')

    # Add arguments
    parser.add_argument(
        '--ip',
        type=validate_ip,
        required=True,
        help='Server IP'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Server port (default: 5001)'
    )

    return parser.parse_args()

# MARK: MAIN
if __name__ == "__main__":
    # Set up arguments.
    args = parse_arguments()
    ip = args.ip
    port = args.port
    # Start our server
    serve(ip, port)

# Example usage:
#       python3 main.py --ip 127.0.0.1 --port 51