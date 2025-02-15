# DIY Wire Protocol Chat Application

## Overview
A client-server chat application implementing a custom wire protocol for messaging. The application features user authentication, real-time messaging, and a graphical user interface built with Tkinter.

## Architecture

### Directory Structure
```
DIY-WIRE-PROTOCOL/
├── Client/
│   ├── Model/
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
    └── test_chat.py
```

### Components

#### Client Side

1. **UI Components** (`Client/UI/`)
   - `chat.py`: Main chat interface with message display, user search, and inbox
   - `signup.py`: User registration and login interface
   - `login.py`: Login form interface

2. **Client Core** (`Client/`)
   - `main.py`: Client application entry point and socket management
   - `communication_manager.py`: Handles communication with server
   - `middleware.py`: Message processing and protocol implementation

#### Server Side

1. **Core Components** (`Server/`)
   - `main.py`: Server entry point and connection management
   - `auth_handler.py`: User authentication and registration
   - `database.py`: Database operations and management
   - `service_actions.py`: Request handling and business logic

2. **Model** (`Server/Model/`)
   - `ClientRequest.py`: Request parsing and validation

## Protocol Specification

### Message Format
Messages follow the format: `VERSION§LENGTH§OPCODE§ARGUMENTS`

- `VERSION`: Protocol version number
- `LENGTH`: Length of the message
- `OPCODE`: Operation code defining message type
- `ARGUMENTS`: Command-specific arguments

### Operation Codes

1. **Authentication**
   - `REGISTER`: New user registration
   - `LOGIN`: User authentication

2. **Messaging**
   - `SEND_MESSAGE`: Send message to user
   - `NEW_MESSAGE`: Notify of new message
   - `RECEIVE_MESSAGE`: Confirm message receipt

3. **Account Management**
   - `DELETE_ACCOUNT`: Remove user account
   - `DELETE_MESSAGE`: Remove specific message
   - `NOTIFICATION_LIMIT`: Update notification settings

## Setup and Installation

### Prerequisites
- Python 3.7+
- SQLite3
- Required Python packages:
  ```bash
  pip install pytest pytest-mock tkinter
  ```

### Database Setup
The application uses SQLite for data storage. The database is automatically initialized with required tables on first run.

### Running the Application

1. Start the server:
   ```bash
   python Server/main.py PORT VERSION
   ```
   Example:
   ```bash
   python Server/main.py 5001 1
   ```

2. Start the client:
   ```bash
   python Client/main.py --host localhost --port 5001
   ```

## Testing

Run the test suite using pytest:
```bash
python -m pytest test_chat.py -v
```

### Test Coverage
- Authentication and registration
- Message sending and receiving
- Database operations
- UI component functionality
- Error handling
- Socket connections

## Features

### User Authentication
- Secure password hashing
- Email validation
- Duplicate username prevention

### Messaging
- Real-time message delivery
- Offline message queuing
- Message history
- User search functionality

### User Interface
- Clean, intuitive design
- Message notifications
- Contact management
- Settings configuration

## Error Handling

### Client-Side
- Connection loss detection
- Invalid input validation
- UI state management

### Server-Side
- Database connection errors
- Invalid request handling
- Protocol version mismatch handling

## Security Features

1. **Password Security**
   - SHA-256 hashing
   - No plaintext storage

2. **Input Validation**
   - Email format verification
   - Username uniqueness check
   - Password strength requirements

3. **Session Management**
   - Active connection tracking
   - Proper session cleanup

## Development Guidelines

### Adding New Features
1. Update protocol specification if needed
2. Implement server-side handling
3. Add client-side support
4. Update test cases
5. Document changes

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Include docstrings for functions
- Add comments for complex logic

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify server is running
   - Check port availability
   - Confirm firewall settings

2. **Database Errors**
   - Check SQLite file permissions
   - Verify database schema
   - Check disk space

3. **UI Issues**
   - Verify Tkinter installation
   - Check system resources
   - Review error logs

## Future Improvements

1. **Features**
   - Group chat support
   - File sharing
   - Message encryption
   - User profiles

2. **Technical**
   - Connection pooling
   - Message compression
   - Caching layer
   - Load balancing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License
This project is open source and available under the MIT License.