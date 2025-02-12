import socket
import selectors
import types
from service_connection import handle_client_response

# todo: bot up with ipp address as command line argument 
# todo: cooked can we use HTTO oor auth?

selector = selectors.DefaultSelector()
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 
PORT = 5001 # todo: check about if this is allowed!!
HTTP_PORT = 5002

active_connections = {}

def accept_connection(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # Register a handler essentially?
    selector.register(conn, events, data=data)
    active_connections[addr] = conn


# Handle service requests
def service_connection(key, mask):
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
            print("something")


def send_message():
    # send to recipient
    
    print("to be implemented")


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
