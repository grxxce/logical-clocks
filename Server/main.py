import socket
import selectors
import types
from service_connection import handle_client_response
# from http.server import HTTPServer
# import threading
# from auth_handler import AuthServer
# from auth_handler import AuthHandler


# todo: bot up with ipp address as command line argument 
# todo: cooked can we use HTTO oor auth?


selector = selectors.DefaultSelector()
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 
PORT = 5001 # todo: check about if this is allowed!!
HTTP_PORT = 5002

# run HTTP server
# def run_http_server():
#     http_server = HTTPServer((HOST, HTTP_PORT), AuthServer)
#     print(f"Starting HTTP server on {HOST}:{HTTP_PORT}")
#     http_server.serve_forever()

def accept_connection(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    # todo: find out what this line does
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    # Register a handler essentially?
    selector.register(conn, events, data=data)





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
            # print(f"{key}:{mask}")
            return_data = "data!!"
            return_data = return_data.encode("utf-8")
            sent = sock.send(return_data)
            data.outb = data.outb[sent:]








if __name__ == "__main__":
    # Start HTTP server in a separate thread
    # http_thread = threading.Thread(target=run_http_server, daemon=True)
    # http_thread.start()
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
    
    # Event count (delete later)
    # event_count = 0
    try:
        # Infinitely listen to the socket
        while True:
            # Look at all currently registered sockets, and if we get an event sent, it selects it & then we handle the events.
            events = selector.select(timeout=None)
            # event_count += 1
            # print("events: ", event_count)
            for key, mask in events:
                if key.data is None:
                    print("accepting connection!")
                    accept_connection(key.fileobj)
                else:
                    # print("servicing connection")
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        selector.close()
