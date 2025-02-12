import socket
import selectors
import types
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

def accept_connection(sock):
    """Add documentation soon!"""
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # Register a handler essentially?
    selector.register(conn, events, data=data)
    active_connections[addr] = conn
    print("active connections", active_connections)


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
            selector.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            # return_data = "Service connection established."
            # return_data = return_data.encode("utf-8")
            # sent = sock.send(return_data)
            # data.outb = data.outb[sent:]
            something = 0



# Dealing with one client <-> server relationship at a time!
# Main point of contact with main.py
def handle_client_response(sock, data):
    print("handle_client_response")
    print(data.outb)
    # Decipher message as a Message object.
    try:
        request = parse_request(data)
        opcode = request.opcode
        arguments = request.arguments

        match opcode:                
            case "REGISTER":
                response = register(*arguments)
                print("register called & did stuff", response)
            case "LOGIN":
                response = login(*arguments)
                print(f"login: {response}")
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

        print("Response:", response)
        # print(f"Finished parsing request with response: {response}")
        # take response & handle it / serialize it
        response = response.encode("utf-8")
        sent = sock.send(response)
        data.outb = data.outb[sent:]
        print("response sent!")
    except:
        print(f"handling_client_reponse: error handling data {data}")

def send_message(curr_connections, sender, recipient, message):
    # Case 1: Recipient is online.
    #       Then, send the message immediately.
    # 
    # Case 2: The recipient is not online.
    #       Then, wait until they are back to check.
    if recipient in curr_connections.keys():
        # They are online, so send the message
        message_request = f"NEW_MESSAGE§{sender}§{recipient}§{message}"
        request = f"{version}§{len(message_request)}§{message_request}"
        curr_connections[recipient].send(request.encode("utf-8"))
    else:
        # not online!
        print("to be done")

# def send_message():
#     # send to recipient
#     print("to be implemented")


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
