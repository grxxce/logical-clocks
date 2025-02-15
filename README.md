# DIY Wire Protocol Chat Application

## Overview
This project is a client-server chat application that implements a flexible wire protocol for messaging. It supports both a custom delimiter-based protocol and a JSON-based protocol, selectable via a command-line flag. The application features user authentication, real-time messaging, and a graphical user interface (GUI) built with Tkinter.

## Architecture

### Directory Structure
```
DIY-WIRE-PROTOCOL/
├── Client/
│   ├── Model/
│   │   └── ServerRequest.py
│   ├── UI/
│   │   ├── chat.py
│   │   ├── login.py
│   │   └── signup.py
│   ├── communication_manager.py
│   ├── main.py
│   └── middleware.py
├── Server/
│   ├── Model/
│   │   └── ClientRequest.py
│   ├── auth_handler.py
│   ├── database.py
│   ├── main.py
│   └── service_actions.py
└── tests/
    ├── test_chat.py
    ├── test_server_request.py
    └── (other test files)
```

### Components

#### Client Side
- **UI Components** (`Client/UI/`)
  - **chat.py**: Main chat interface with message display, user search, inbox management, and settings.
  - **signup.py**: User registration (and login) interface.
  - **login.py**: Login form interface.
- **Core Modules** (`Client/`)
  - **main.py**: Application entry point, socket management, and command-line argument parsing.
  - **communication_manager.py**: Handles all communications with the server.
  - **middleware.py**: Processes messages, handles protocol implementation, and routes commands.
- **Model** (`Client/Model/`)
  - **ServerRequest.py**: Provides functions to serialize and deserialize requests and responses using both the custom and JSON protocols.

#### Server Side
- **Core Modules** (`Server/`)
  - **main.py**: Server entry point, handles client connections, and manages the socket server.
  - **auth_handler.py**: Manages user authentication and registration.
  - **database.py**: Handles all database operations via SQLite (automatically initialized on first run).
  - **service_actions.py**: Contains business logic to handle different types of client requests.
- **Model** (`Server/Model/`)
  - **ClientRequest.py**: Parses and validates incoming client requests.
  - **SerializationManager.py** (if present): Contains functions for serializing responses to the client using either protocol.

## Protocol Specification

The application supports **two protocols**:

1. **Custom Protocol**  
   Messages follow the format:  
   ```
   VERSION§LENGTH§OPCODE§ARGUMENTS∞
   ```  
   - **VERSION**: Numeric version of the protocol.
   - **LENGTH**: The character length of the operation-specific part (which is built by concatenating the opcode and its arguments, each separated by "§").
   - **OPCODE**: A string defining the operation (e.g., `LOGIN`, `SEND_MESSAGE`).
   - **ARGUMENTS**: Command-specific arguments. For list-type arguments, each element is appended with its own delimiter.
   - The message ends with a trailing "∞" marker.

2. **JSON Protocol**  
   The JSON protocol creates a message object that includes:
   - `version`: Protocol version.
   - `length`: Computed as `len(op_code) + len(arguments)` (number of arguments).
   - `opcode`: Operation code.
   - `arguments`: List of command-specific arguments.

## Running the Application

### Command-Line Options

Both client and server can run in either JSON mode or custom-protocol mode. To use the JSON protocol, simply include the `--json` flag when starting an application.

### Starting the Server
From the project root, start the server with:
```bash
python3 Server/main.py 5001 1 --json
```
- `5001` is the port number.
- `1` is the protocol version.
- Include `--json` to use the JSON protocol. Omit this flag to use the custom delimiter-based protocol.

### Starting the Client
From the project root, start the client with:
```bash
python3 Client/main.py --host 10.250.166.71 --port 5001 --json
```
- `--host` specifies the server's IP address.
- `--port` specifies the server's port.
- Include `--json` if you want the client to communicate with the server using the JSON protocol.

## Setup and Installation

### Prerequisites
- Python 3.7+
- SQLite3 (for the database)
- Required Python packages (install via pip):
  ```bash
  pip install pytest pytest-mock
  ```
  *Note: Tkinter should be available with standard Python installations; if missing, install the appropriate package for your OS.*

### Database Setup
The SQLite database is automatically initialized with the required tables on the first run of the server application.

## Testing

Run the test suite using pytest from the project root:
```bash
python -m pytest -v
```
This runs tests for authentication, messaging, database operations, UI components, and protocol parsing/serialization on both client and server sides.

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

## Features

### User Authentication
- Secure password hashing (e.g., SHA-256).
- Email validation and duplicate username prevention.
- Session management with active connection tracking.

### Messaging
- Real-time message delivery.
- Offline message queuing.
- Message history and user search functionality.

### User Interface
- Clean, intuitive design built with Tkinter.
- Message notifications and contact management.
- Configuration options for notifications and other settings.

## Error Handling

### Client-Side
- Connection loss detection and reconnection strategies.
- Input validation and user feedback for invalid actions.
- UI state management to handle errors gracefully.

### Server-Side
- Robust error handling for database connectivity.
- Validating and filtering malformed or invalid client requests.
- Managing protocol version mismatches and unexpected errors.

## Security Features

1. **Password Security**
   - SHA-256 hashing without storing plaintext passwords.
2. **Input Validation**
   - Strict email and username format verification.
   - Password strength and uniqueness checks.
3. **Session Management**
   - Active session tracking and proper session cleanup upon disconnection.

## Development Guidelines

### Adding New Features
1. Update the protocol specification as needed.
2. Implement the server-side logic in `auth_handler.py`, `database.py`, or `service_actions.py`.
3. Extend the client-side features in `communication_manager.py` or UI components.
4. Update existing test cases and add new ones in the `tests/` directory.
5. Document all changes in the README and inline code docstrings.

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Ensure the server is running and reachable.
   - Confirm that the host IP and port match between client and server.
2. **Database Errors**
   - Check file permissions for the SQLite database file.
   - Ensure the database schema is intact.
   - Delete users.db if needed.

## Future Improvements

1. **Feature Enhancements**
   - Group chat support.
   - File sharing capabilities.
   - End-to-end message encryption.
   - Detailed user profiles.
2. **Technical Enhancements**
   - Connection pooling for improved performance.
   - Message compression and caching.
   - Load balancing for scaling the server.
   - Advanced logging and monitoring.
   - Adding a checksum to the protocol.
