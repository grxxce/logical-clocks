import sys
import socket
import selectors
import types
from collections import defaultdict
from service_actions import register, login, delete_account, delete_message, update_notification_limit
from Model.SerializationManager import SerializationManager as SM
import json

# todo: bot up with ipp address as command line argument 
# todo: cooked can we use HTTO oor auth?


"""
Welcome & Command-Line Arguments.
We recommend using PORT = 5001 or 5002.

Proper usage to launch server:
    
    python3 main.py PORT VERSION=1
"""
if not len(sys.argv) == 4 and not len(sys.argv) == 3:
    sys.exit("Please follow the proper usage: python3 main.py PORT VERSION=1")
# TODO: more easy checks??? brownie points???
# elif not isinstance(sys.argv[2], int) or int(sys.argv[2]) < 0:
#     sys.exit("The PORT entered must be a positive integer.") 


# MARK: Configuration
isJSON = False

PORT = int(sys.argv[1])
if sys.argv[2]:
    VERSION = int(sys.argv[2])
else:
    VERSION = 1


# MARK: Prepare sockets & selectors
selector = selectors.DefaultSelector()
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 


# MARK: Track necessary states
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
        print(f"Accepted connection from {addr}.")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        selector.register(conn, events, data=data)
    except socket.error as e:
        print(f"Failed to accept socket connection with socket error: {e}")


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
            print(f"Closing connection to {data.addr}")
            username = None
            for user, client_sock in active_connections.items():
                if client_sock == sock:
                    username = user
                    break
            
            # Remove from active_connections if found
            if username:
                print(f"Removing active connection for user: {username}")
                active_connections.pop(username)
            
            selector.unregister(sock)
            sock.close()


# MARK: Managing Client-Server Requests & Operations
def handle_client_requests(sock, data):
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
    print(f"Entering handle_client_requests: data.outb = {data.outb}")
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
        print(f"Verify parsed request with OPCODE {opcode}: {arguments}")

        # Considering the given operation desired, respond accordingly.
        # Call out to helper functionalities & operation-handy code.
        match opcode:         
            case "REGISTER":
                # Response will be op_code, arguments
                register_request = register(*arguments)
                response = SM.serialize_to_str(VERSION, register_request[0], register_request[1], isJSON)
            
            case "LOGIN":
                print("ARGUMENTS", arguments)
                login_response = login(*arguments)
                # Ensure that we add this connection to our currently active
                # connections.
                
                # Send success immediately
                # if response.split("§")[2] == "LOGIN_SUCCESS":
                #     data.outb = response.encode("utf-8")
                #     sent = sock.send(data.outb)             # Send the response over the wire.
                #     data.outb = data.outb[sent:] 
                    
                #     active_connections[arguments[0]] = sock
                #     check_pending_messages(arguments[0])
                #     response = ""
                if login_response[0] == "LOGIN_SUCCESS":
                    # Serialize data
                    serialized_response = SM.serialize_to_str(VERSION, login_response[0], login_response[1], isJSON)
                    data.outb = serialized_response.encode("utf-8")
                    sent = sock.send(data.outb)             # Send the response over the wire.
                    data.outb = data.outb[sent:]

                    # Add this connection to our active ones.
                    active_connections[arguments[0]] = sock
                    check_pending_messages(arguments[0])
                    response = ""  

                else:
                    # Login failed, so let the user know.
                    print(f"Failed to login user: {login_response}")
                    response = SM.serialize_to_str(VERSION, login_response[0], login_response[1], isJSON)

            case "SEND_MESSAGE":
                response = send_message(*arguments)
                # response = SM.serialize_to_str(VERSION, send_message_response[0], send_message_response[1], isJSON)
                # print("RESPONSE TO SEND MESSAGE", response)
            case "DELETE_MESSAGE":
                delete_message_response = delete_message(*arguments)
                response = SM.serialize_to_str(VERSION, delete_message_response[0], delete_message_response[1], isJSON)
            case "DELETE_ACCOUNT":
                delete_account_response = delete_account(*arguments)
                response = SM.serialize_to_str(VERSION, delete_account_response[0], delete_account_response[1], isJSON)
            case "NOTIFICATION_LIMIT":
                update_limit_response = update_notification_limit(*arguments)
                response = SM.serialize_to_str(VERSION, update_limit_response[0], update_limit_response[1], isJSON)
            case _:
                response = "Nothing to do."

        # Encode the appropriate response, which may contain
        # information about the success or failure of an operation,
        # using the already serialize strings and converting them into byte strings.
        data.outb = response.encode("utf-8")
        sent = sock.send(data.outb)             # Send the response over the wire.
        data.outb = data.outb[sent:]            # Clear the output buffer.
        print(f"Check outb: {data.outb}")     # MUST be empty when all is sent.
        print(f"Response sent successfully via {sock}")
    except Exception as e:
        # TODO: make this better!!
        print(f"handling_client_reponse: error handling data {data}, with error {e}")


def send_message(sender, recipient, message):
    """ADD COMMENTS"""
    print(f"Sending message from {sender} to {recipient}: {message}")
    # Case 1: Recipient is online.
    #       Then, send the message immediately.
    # 
    # Case 2: The recipient is not online.
    #       Then, wait until they are back to check.
    OP_CODE = "NEW_MESSAGE"
    request = SM.serialize_to_str(VERSION, OP_CODE, [sender, recipient, message], isJSON)
    # if jsonSelected:
    #     request = ClientRequest.serializeJSON(VERSION, OP_CODE, [sender, recipient, message])
    # else:
    #     request = ClientRequest.serialize(VERSION, OP_CODE, [sender, recipient, message])

    if recipient in active_connections.keys():
        # They are online, so send the message
        # Okay, so we have now added data to the buffer of this particular socket of 
        # the person who is receiving the message, thus we must select their data buffer and
        # clear it!
        # sent = active_connections[recipient].send(request.encode("utf-8"))
        sent = active_connections[recipient].send(request.encode("utf-8"))
        key = selector.get_key(active_connections[recipient])
        key.data.outb = key.data.outb[sent:]
        
        # if jsonSelected:
        #     message_status = ClientRequest.serializeJSON(VERSION, "RECEIVED_MESSAGE", [sender, message])
        # else:
        #     message_status = ClientRequest.serialize(VERSION, "RECEIVED_MESSAGE", [sender, message])
        message_status = SM.serialize_to_str(VERSION, "RECEIVED_MESSAGE", [sender, message], isJSON)
        print("MESSAGE STATUS 1", message_status)
        return message_status
    else:
        # Add to a list of pending messages, so that when the user 
        # comes back online that they will receive their messages.
        pending_messages[recipient].append(request)
        # To ensure no failures occur!
        
        # if jsonSelected:
        #     message_status = ClientRequest.serializeJSON(VERSION, "RECEIVED_MESSAGE", [sender, message])
        # else:
        #     message_status = ClientRequest.serialize(VERSION, "RECEIVED_MESSAGE", [sender, message])
        message_status = SM.serialize_to_str(VERSION, "RECEIVED_MESSAGE", [sender, message], isJSON)
        print("MESSAGE STATUS 2", message_status)
        return message_status


def check_pending_messages(username):
    """Documentation"""
    if len(pending_messages[username]) > 0:
        print("check_pending_messages")
        # Send over all of the pending messages to the client.
        try:
            for message in pending_messages[username]:
                print("found a pending message", message)
                active_connections[username].send(message.encode("utf-8"))
            pending_messages[username] = []
        except: 
            # The socket must have disconnected, thus hold onto the pending options.
            return

if __name__ == "__main__":
    # AF_INET defines the address family (ex. IPv4)
    # SOCK_STREAM defines socket type (ex. TCP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Listening on", (HOST, PORT))
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
                    print("accepting connection!")
                    accept_connection(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        selector.close()
