import socket
import selectors
import types
from collections import defaultdict
from service_actions import register, login, delete_account, delete_message, update_notification_limit, parse_request


# todo: bot up with ipp address as command line argument 
# todo: cooked can we use HTTO oor auth?

# Constants & State Tracking
selector = selectors.DefaultSelector()
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 
PORT = 5001 # todo: check about if this is allowed!!
HTTP_PORT = 5002
version = 1

# Keep track of the currently connected clients.
active_connections = {}
# username_IP_mappings = {}

pending_messages = defaultdict(list)

def accept_connection(sock):
    """Add documentation soon!"""
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # Register a handler essentially?
    selector.register(conn, events, data=data)
    # active_connections[addr] = conn
    # print("active connections", active_connections)


# Handle service requests
def service_connection(key, mask):
    """Add documentation soon"""
    sock = key.fileobj
    data = key.data
    # Data received from the client
    if mask & selectors.EVENT_READ:
        # read 1024 data points (what unit is this??)
        recv_data = sock.recv(1024)
        # print(f"recv_data: {recv_data}")
        if recv_data:
            data.outb += recv_data
            # print(f"data.outb: {data.outb}")
            # Call handler for message received
            handle_client_response(sock, data)
        else:
            print(f"Closing connection to {data.addr}")
            # Need to remove these from active connection
            selector.unregister(sock)
            # remove_deactivated_connections(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            # return_data = "Service connection established."
            # return_data = return_data.encode("utf-8")
            # sent = sock.send(return_data)
            # data.outb = data.outb[sent:]
            something = 0

# TODO: 
# def remove_deactivated_connections(sock):
#     # Remove the socket of the disconnected client from our active connections list.
#     for key, value in active_connections.items():
#         if value == sock:
#             active_connections.pop(key)



# Dealing with one client <-> server relationship at a time!
# Main point of contact with main.py
def handle_client_response(sock, data):
    print("handle_client_response")
    print("data.outb", data.outb)
    # Decipher message as a Message object.
    try:
        request = parse_request(data)
        opcode = request.opcode
        print("Opcode", opcode)
        arguments = request.arguments

        match opcode:                
            case "REGISTER":
                response = register(*arguments)
            case "LOGIN":
                response = login(*arguments)
                # Link this username to the socket & IP.
                # username_IP_mappings[arguments[0]] = sock.gethostbyname(hostname)
                active_connections[arguments[0]] = sock
                print("about to check pending")
                check_pending_messages(arguments[0])
            case "SEND_MESSAGE":
                response = send_message(*arguments)
                # response = ""
            case "DELETE_MESSAGE":
                response = delete_message(*arguments)
            case "DELETE_ACCOUNT":
                response = delete_account(*arguments)
            case "NOTIFICATION_LIMIT":
                response = update_notification_limit(*arguments)
            case _:
                response = "Nothing to do."

        # take response & handle it / serialize it
        response = response.encode("utf-8")
        sent = sock.send(response)
        data.outb = data.outb[sent:]
        print("response sent!")
    except:
        print(f"handling_client_reponse: error handling data {data}")

def send_message(sender, recipient, message):
    print("attempting to send message", sender, recipient, message)
    # Case 1: Recipient is online.
    #       Then, send the message immediately.
    # 
    # Case 2: The recipient is not online.
    #       Then, wait until they are back to check.
    # print(sender, recipient, message)
    message_request = f"NEW_MESSAGE§{sender}§{recipient}§{message}"
    request = f"{version}§{len(message_request)}§{message_request}"
    if recipient in active_connections.keys():
        # They are online, so send the message
        message_request = f"NEW_MESSAGE§{sender}§{recipient}§{message}"
        request = f"{version}§{len(message_request)}§{message_request}"
        active_connections[recipient].send(request.encode("utf-8"))
        
        message_status = f"RECEIVED_MESSAGE§{sender}§{message}"
        request2 = f"{version}§{len(message_status)}§{message_status}"
        # sent = active_connections[recipient].send(request.encode("utf-8"))
        # active_connections[recipient].outb = active_connections[recipient].outb[sent:]
        # print("sent!")
        return request2
    else:
        # not online!
        # Add to a list of pending messages, so that when the user 
        # comes back online that they will receive their messages.
        print("pending messages append")
        pending_messages[recipient].append(request)


def check_pending_messages(username):
    """Documentation"""
    if len(pending_messages[username]) > 0:
        print("check_pending_messages")
        # Send over all of the pending messages to the client.
        try:
            for message in pending_messages[username]:
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
