import sys
import socket
import selectors
import types
from collections import defaultdict
from service_actions import register, login, delete_account, get_settings, save_settings
from Model.SerializationManager import SerializationManager as SM
import argparse
import logging


import grpc
import server_pb2
import server_pb2_grpc


"""
Welcome!
This file contains essential components of setting up the server and its handlers.
Its handlers parse and respond to client requests.

To launch the server, we recommend using PORT = 5001 or 5002 and following the usage below.

Example usage to launch server:
    
    python3 main.py --port 5001 --version 1

Example to use JSON:

    python3 main.py --port 5001 --version 1 --isJSON true
"""

# Configure logging set-up. We want to log times & types of logs, as well as
# function names & the subsequent message.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
)

# Create a logger
logger = logging.getLogger(__name__)

# MARK: Configuration & handle command-line arguments.
# We will set up our port, version, and protocol through command line arguments.
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chat Client')

    # Add arguments
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='Server port (default: 5001)'
    )

    parser.add_argument(
        '--version',
        type=int,
        default=1,
        help="Version to use (default: 1)"
    )

    parser.add_argument(
        '--isJSON',
        type=bool,
        default=False,
        help='Do not include flag unless you want to use JSON protocol (default: False)'
    )
    return parser.parse_args()

# Set up arguments.
args = parse_arguments()
PORT = args.port
VERSION = args.version
isJSON = args.isJSON

# MARK: Prepare Sockets & Selectors
selector = selectors.DefaultSelector()
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 

# Track necessary states
active_connections = {}                 # Track currently connected clients
pending_messages = defaultdict(list)    # Track undelivered messages
pending_deletion = defaultdict(list)    # Track messages to be deleted

# MARK: Managing Client-Server Connections
def accept_connection(sock):
    """
    Registers and forms socket connections between the server and individual clients.
    Utilizes selectors in a non-blocking manner to accept and register socket connections.

    Parameters:
            sock: A socket used to connect with the client.
    Returns:
            Void: Registers the connection in our global selectors.
            Error: If the socket fails to connect, a socket error will be raised. 
    """
    try:
        conn, addr = sock.accept()
        logger.info(f"Accepted connection from {addr}.")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        selector.register(conn, events, data=data)
    except socket.error as e:
        logger.error(f"Failed to accept socket connection with socket error: {e}")

def service_connection(key, mask):
    """
    Maintains socket connections to handle incoming messages and to address socket closures.
    Calls upon helper functions to handle cases of requests.

    Parameters:
            key: key pieces of information about a socket, including its data, fd, 
                    and more.
            mask: an integer representing events occuring on the socket
    Returns:
            Void: handles delegating to specific functionalities
    """
    sock = key.fileobj
    data = key.data
    # Data received from the client
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
            handle_client_requests(sock, data)
        else:
            logger.info(f"Closing connection to {data.addr}")
            username = None
            for user, client_sock in active_connections.items():
                if client_sock == sock:
                    username = user
                    break
            
            # Remove from active_connections, if found
            if username:
                print(f"Removing active connection for user: {username}")
                active_connections.pop(username)
            
            # Stop observing the socket and close the connection.
            selector.unregister(sock)
            sock.close()


# MARK: Managing Client-Server Requests & Operations
def handle_client_requests(sock, data):
    """
    Handles incoming requests from the client through deserializing & parsing, then
    delegating to the appropriate helper functions.
    Manages sending appropriate responses to the client.

    Parameters:
            sock: socket connecting the server to the client
            data: a byte string from the client
    Returns:
            Void: handles delegating to specific functionalities
    """
    logger.info(f"Server received client request: {data.outb}")
    try:
        # Decipher message (either from JSON or from our custom serialization)
        # The request is now formatted as a dictionary with the following keys:
            # version
            # length
            # opcode
            # arguments (as arrays of data)
        request = SM.parse_serialized_data(version=VERSION, data=data, isJSON=isJSON)
        opcode = request["opcode"]
        arguments = request["arguments"]

        # Verify parsing.
        logger.debug(f"Verify parsed request with OPCODE {opcode}: {arguments}")

        # Considering the given operation desired, respond accordingly.
        # Call out to helper functionalities & operation-handy code.
        match opcode:         
            case "REGISTER":
                # Response will be op_code, arguments
                register_request = register(*arguments)
                response = SM.serialize_to_str(VERSION, register_request[0], register_request[1], isJSON)

            case "LOGIN":
                login_response = login(*arguments)

                # Ensure that we add this connection to our currently active
                # connections and send the client set-up information.
                if login_response[0] == "LOGIN_SUCCESS":
                    # Serialize data
                    serialized_response = SM.serialize_to_str(VERSION, login_response[0], login_response[1], isJSON)
                    data.outb = serialized_response.encode("utf-8")
                    sent = sock.send(data.outb)             # Send the response over the wire.
                    data.outb = data.outb[sent:]

                    # Add this connection to our active ones.
                    active_connections[arguments[0]] = sock
                    check_pending_messages(arguments[0])
                    response = ""       # No additional response required.
                else:
                    # Login failed, so let the user know.
                    logger.warning(f"Failed to login user: {login_response}")
                    response = SM.serialize_to_str(VERSION, login_response[0], login_response[1], isJSON)

            case "SEND_MESSAGE":
                response = send_message(*arguments)
            case "DELETE_ACCOUNT":
                delete_account_response = delete_account(*arguments)
                response = SM.serialize_to_str(VERSION, delete_account_response[0], delete_account_response[1], isJSON)
            case "GET_SETTINGS":
                # TODO: check
                response = get_settings(*arguments)
                response = SM.serialize_to_str(VERSION, response[0], response[1], isJSON)
            case "SAVE_SETTINGS":
                response = save_settings(*arguments)
                response = SM.serialize_to_str(VERSION, response[0], response[1], isJSON)
            case _:
                logger.warning("Nothing to do reached in handle function.")
                response = "Nothing to do."

        # Encode the appropriate response, which may contain
        # information about the success or failure of an operation,
        # using the already serialized strings and converting them into byte strings.
        data.outb = response.encode("utf-8")
        sent = sock.send(data.outb)             # Send the response over the wire.
        data.outb = data.outb[sent:]            # Clear the output buffer.
        logger.debug(f"Check outb: {data.outb}")       # MUST be empty when all is sent.
        logger.info(f"Response sent successfully via {sock}")
    except Exception as e:
        logger.error(f"Error occurred while handling client request with error {e}")

def send_message(sender, recipient, message):
    """
    Handles a message being sent from one client to another.

    Parameters:
            sender: username as a string
            recipient: username as a string
            message: a string
    Returns:
            message_status: a serialized response upon success
    """
    logger.info(f"Sending message from {sender} to {recipient}: {message}")
    OP_CODE = "NEW_MESSAGE"
    request = SM.serialize_to_str(VERSION, OP_CODE, [sender, recipient, message], isJSON)

    # Case 1: Recipient is online.
    #       Then, send the message immediately.
    if recipient in active_connections.keys():
        # We have now added data to the buffer of this particular socket of 
        # the person who is receiving the message, thus we must select their data buffer and
        # clear it.
        sent = active_connections[recipient].send(request.encode("utf-8"))
        key = selector.get_key(active_connections[recipient])
        key.data.outb = key.data.outb[sent:]
        
        # Document message status.
        message_status = SM.serialize_to_str(VERSION, "RECEIVED_MESSAGE", [sender, message], isJSON)
        return message_status
    else:
        # Case 2: The recipient is not online.
        #       Then, wait until they are back to check.

        # Add to a list of pending messages, so that when the user 
        # comes back online that they will receive their messages.
        pending_messages[recipient].append(request)
        
        # Document message status.
        message_status = SM.serialize_to_str(VERSION, "RECEIVED_MESSAGE", [sender, message], isJSON)
        return message_status

def check_pending_messages(username):
    """
    Checks if a user who has become active has any pending messages.
    If so, delivers the messages.

    Parameters:
            username: a string of the user who has become active
    """
    if len(pending_messages[username]) > 0:
        # Send over all of the pending messages to the client.
        try:
            for message in pending_messages[username]:
                active_connections[username].send(message.encode("utf-8"))
            pending_messages[username] = []
        except Exception as e: 
            # The socket must have disconnected, thus hold onto the pending options.
            logger.error("Something went wrong in sending pending messages with error {e}")
            return

# MARK: Main

if __name__ == "__main__":
    # AF_INET defines the address family (ex. IPv4)
    # SOCK_STREAM defines socket type (ex. TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    logger.info(f"Listening on ({HOST}, {PORT})")
    # Allow the socket to continue working without putting other possible connections on hold.
    server_socket.setblocking(False)
    # Register the initial socket by the server (only looks for incoming connections)
    selector.register(server_socket, selectors.EVENT_READ, data=None)
    
    try:
        # Infinitely listen to the socket
        while True:
            # Look at all currently registered sockets, and if we get an event sent, it selects it & then we handle the events.
            events = selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    logger.info("Accepting connection!")
                    accept_connection(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        selector.close()
