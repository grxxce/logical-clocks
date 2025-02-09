import socket
from UI.signup import LoginClient

# Main login UI — this is HTTP connection
login_client = LoginClient()
login_client.root.mainloop()

try: 
    print("Starting socket connection")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # todo: dont' hardcode this
    PORT = 5001
    hostname = socket.gethostname()
    HOST = socket.gethostbyname(hostname) 
    server_address = (HOST, PORT)

    # Connect to the server
    client_socket.connect(server_address)

    # Send data to the server
    print("Connected to the server")
    message = "Hello from the client!"
    client_socket.send(message.encode())

    # Receive data from the server
    data = client_socket.recv(1024)
    print(f"Received: {data.decode()}")

except KeyboardInterrupt:
    print("Caught keyboard interrupt, closing connection")
    client_socket.close()