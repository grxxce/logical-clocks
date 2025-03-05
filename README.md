# Simulating Scale Models & Logical Clocks
## Assignment 3
### Directory Structure
```
LOGICAL-CLOCKS/
├── Client/
│   ├── main.py
│   └── test_simulations.py
├── Server/
│   ├── main.py
│   ├── test_server.py
├── proto/
│   ├── service.proto
│   ├── service_pb2.py
│   └── service_pb2_grpc.py
├── logs/
├── results/
│   ├── simulation_0
│   ├── simulation_1
│   ├── ....

```
## Updated Setup
1. Install the required packages:
    ```bash 
    pip install -r requirements.txt
    ```

2. Generate Protocol Buffer code (only needed if you modify the proto files):
   ```bash
   python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/service.proto
   ```

3. Start the simulation:
   ```bash
   python simulation.py --ip your_ip --port 5001 --duration 90 --runs 5
   ```

4. After the simulation concludes, run the analysis to get updated plots from the log data:
   ```bash
   python analysis.py --runs 5
   ```

5. Run the tests:
   ```bash
   pytest Client/test_simulation.py
   pytest Server/test_server.py
   ```

## This assignment builds on our previous implementation of a messaging application that uses gRPC specifications in order to exchange messages between clients and servers. Below, you can find the architecture for our gRPC specifications and some helpful notes.

## gRPC  Specification

- **Service Definition**: Defined in `proto/service.proto` using the Protocol Buffers IDL
- **Generated Code**: The protocol compiler generates client and server code in `service_pb2.py` and `service_pb2_grpc.py`
- **RPC Methods**: Supports both unary calls (request-response) and streaming for real-time messaging
- **Message Types**: Strongly typed message definitions for most operations

Key gRPC services include:
- `SendMessage`: Message delivery to recipients
- `GetPendingMessage`: Streams pending messages to clients
- `MonitorMessages`: Real-time message monitoring via server streaming


### Test Coverage
- **Client Side**:  
  - Authentication and registration interface.
  - Chat interface functionality.
  - ServerRequest serialization/deserialization.
  - UI component actions and error handling.
- **Server Side**:  
  - Request parsing and validation.
  - Serialization and deserialization using both the custom and JSON protocols.
  - Database operations.
  - Business logic and service actions.

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Ensure the server is running and reachable.
   - Confirm that the host IP and port match between the client and server.