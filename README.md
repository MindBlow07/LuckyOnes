# LuckyOnes
A Python-based end-to-end encrypted chat application with cyberpunk styling and automatic message deletion.

## Features

- **End-to-End Encryption**: Uses AES-256-GCM, X25519 key exchange, and Double Ratchet protocol
- **Cyberpunk UI**: Purple, black, and gray color scheme with modern styling
- **Auto-Deletion**: Threads expire after 12 hours, images after 30 minutes
- **No Logging**: Messages are never permanently stored
- **Tor Support**: Network communication can go through Tor (basic implementation)
- **Thread Management**: Main chat + private/public threads with countdown timers
- **Image Sharing**: Send images with automatic deletion
- **No Registration**: Automatic username generation, no login required

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python luckyones_server.py --port 6660
```

The server will start on port 6660 by default. You can specify a different port with the `--port` argument.

### Starting the Client

```bash
python luckyones_client.py
```

1. The client will show a lobby window with your auto-generated username
2. Enter the server host (default: 127.0.0.1) and port (default: 6660)
3. Click "CONNECT" to join the chat
4. Use the chat interface to send messages and create threads

## Security Features

- **No Message Logging**: Messages are never stored permanently
- **End-to-End Encryption**: All communication is encrypted
- **Forward Secrecy**: Double Ratchet protocol ensures past messages remain secure
- **Automatic Cleanup**: Images and temporary threads are automatically deleted
- **No User Data**: No registration, no personal information stored

## Architecture

- `crypto_utils.py`: Cryptographic functions and Double Ratchet implementation
- `network_utils.py`: Network communication and protocol handling
- `chat_manager.py`: Chat logic, thread management, and auto-deletion
- `ui_cyberpunk.py`: Cyberpunk-themed user interface
- `luckyones_client.py`: Main client application
- `luckyones_server.py`: Main server application

## Thread Types

- **Main Chat**: Permanent thread that never expires
- **Public Threads**: Visible to all users, expire after 12 hours
- **Private Threads**: Only visible to creator, expire after 12 hours

## Image Handling

- Images are stored temporarily in the `temp_images/` directory
- Automatic deletion after 30 minutes
- Support for JPG, PNG, GIF, and BMP formats

## Network Protocol

The application uses a custom protocol for client-server communication:

- `JOIN`: Client joins the server
- `LEAVE`: Client leaves the server
- `MESSAGE`: Text message
- `IMAGE`: Image message
- `CREATE_THREAD`: Create new thread
- `DELETE_THREAD`: Delete thread (automatic)

## Development

To run in development mode:

1. Start the server in one terminal
2. Start multiple clients in different terminals to test multi-user functionality
3. Test thread creation, image sharing, and auto-deletion features
