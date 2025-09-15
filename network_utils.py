"""
Network communication utilities for LuckyOnes E2EE chat application.
Handles client-server communication with Tor support.
"""

import socket
import threading
import json
import time
import requests
from typing import Dict, List, Optional, Callable, Any
from crypto_utils import CryptoManager


class TorProxy:
    """Simple Tor proxy handler."""
    
    def __init__(self, tor_proxy: str = "127.0.0.1:9050"):
        self.tor_proxy = tor_proxy
        self.proxies = {
            'http': f'socks5://{tor_proxy}',
            'https': f'socks5://{tor_proxy}'
        }
    
    def is_tor_available(self) -> bool:
        """Check if Tor is available."""
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=self.proxies,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_tor_ip(self) -> Optional[str]:
        """Get our Tor IP address."""
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=self.proxies,
                timeout=10
            )
            return response.json().get('origin')
        except:
            return None


class MessageProtocol:
    """Message protocol for client-server communication."""
    
    # Message types
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    MESSAGE = "MESSAGE"
    IMAGE = "IMAGE"
    CREATE_THREAD = "CREATE_THREAD"
    DELETE_THREAD = "DELETE_THREAD"
    USER_LIST = "USER_LIST"
    THREAD_LIST = "THREAD_LIST"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    
    @staticmethod
    def create_message(msg_type: str, data: Dict[str, Any], user_id: str = None) -> bytes:
        """Create a protocol message."""
        message = {
            'type': msg_type,
            'timestamp': time.time(),
            'data': data
        }
        if user_id:
            message['user_id'] = user_id
        
        return json.dumps(message).encode('utf-8')
    
    @staticmethod
    def parse_message(data: bytes) -> Dict[str, Any]:
        """Parse a protocol message."""
        try:
            return json.loads(data.decode('utf-8'))
        except:
            return {'type': 'ERROR', 'data': {'error': 'Invalid message format'}}


class NetworkClient:
    """Client-side network handler."""
    
    def __init__(self, crypto_manager: CryptoManager):
        self.crypto_manager = crypto_manager
        self.socket = None
        self.connected = False
        self.server_host = None
        self.server_port = None
        self.message_handlers = {}
        self.receive_thread = None
        self.tor_proxy = TorProxy()
    
    def connect(self, host: str, port: int = 6660, use_tor: bool = False) -> bool:
        """Connect to the server."""
        try:
            self.server_host = host
            self.server_port = port
            
            if use_tor and self.tor_proxy.is_tor_available():
                # For Tor connections, we'd need a different approach
                # This is a simplified version
                print("Tor connection not fully implemented in this version")
                return False
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            
            # Send join message
            join_data = {
                'user_id': self.crypto_manager.get_user_id(),
                'username': self.crypto_manager.get_username(),
                'public_key': self.crypto_manager.get_public_key().hex()
            }
            
            message = MessageProtocol.create_message(
                MessageProtocol.JOIN, 
                join_data, 
                self.crypto_manager.get_user_id()
            )
            
            self.socket.send(message)
            self.connected = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.connected and self.socket:
            try:
                leave_data = {'user_id': self.crypto_manager.get_user_id()}
                message = MessageProtocol.create_message(
                    MessageProtocol.LEAVE,
                    leave_data,
                    self.crypto_manager.get_user_id()
                )
                self.socket.send(message)
            except:
                pass
            
            self.connected = False
            self.socket.close()
            self.socket = None
    
    def send_message(self, content: str, thread_id: str = "main", recipient_id: str = None):
        """Send a text message."""
        if not self.connected:
            return False
        
        try:
            message_data = {
                'content': content,
                'thread_id': thread_id,
                'timestamp': time.time()
            }
            
            if recipient_id:
                # Direct message - encrypt for specific recipient
                # This would require getting their public key first
                message_data['recipient_id'] = recipient_id
            
            message = MessageProtocol.create_message(
                MessageProtocol.MESSAGE,
                message_data,
                self.crypto_manager.get_user_id()
            )
            
            self.socket.send(message)
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def send_image(self, image_data: bytes, thread_id: str = "main"):
        """Send an image."""
        if not self.connected:
            return False
        
        try:
            # Convert image to base64 for transmission
            import base64
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            message_data = {
                'image_data': image_b64,
                'thread_id': thread_id,
                'timestamp': time.time()
            }
            
            message = MessageProtocol.create_message(
                MessageProtocol.IMAGE,
                message_data,
                self.crypto_manager.get_user_id()
            )
            
            self.socket.send(message)
            return True
            
        except Exception as e:
            print(f"Failed to send image: {e}")
            return False
    
    def create_thread(self, thread_name: str, is_private: bool = False):
        """Create a new thread."""
        if not self.connected:
            return False
        
        try:
            message_data = {
                'thread_name': thread_name,
                'is_private': is_private,
                'creator_id': self.crypto_manager.get_user_id()
            }
            
            message = MessageProtocol.create_message(
                MessageProtocol.CREATE_THREAD,
                message_data,
                self.crypto_manager.get_user_id()
            )
            
            self.socket.send(message)
            return True
            
        except Exception as e:
            print(f"Failed to create thread: {e}")
            return False
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a message handler."""
        self.message_handlers[message_type] = handler
    
    def _receive_loop(self):
        """Main receive loop."""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = MessageProtocol.parse_message(data)
                message_type = message.get('type')
                
                if message_type in self.message_handlers:
                    self.message_handlers[message_type](message)
                
            except Exception as e:
                if self.connected:
                    print(f"Receive error: {e}")
                break
        
        self.connected = False


class NetworkServer:
    """Server-side network handler."""
    
    def __init__(self, port: int = 6660):
        self.port = port
        self.socket = None
        self.clients = {}  # {client_socket: client_info}
        self.threads = {}  # {thread_id: thread_info}
        self.running = False
        self.accept_thread = None
    
    def start(self):
        """Start the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.port))
            self.socket.listen(10)
            self.running = True
            
            # Create main thread
            self.threads['main'] = {
                'name': 'Main Chat',
                'is_private': False,
                'created_at': time.time(),
                'expires_at': None,  # Main thread never expires
                'creator_id': 'system'
            }
            
            print(f"Server started on port {self.port}")
            
            # Start accept thread
            self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.accept_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the server."""
        self.running = False
        
        # Disconnect all clients
        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        
        self.clients.clear()
        
        if self.socket:
            self.socket.close()
            self.socket = None
    
    def _accept_loop(self):
        """Accept new client connections."""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"New connection from {address}")
                
                # Start client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Handle a client connection."""
        client_info = {
            'socket': client_socket,
            'address': address,
            'user_id': None,
            'username': None,
            'public_key': None,
            'connected_at': time.time()
        }
        
        self.clients[client_socket] = client_info
        
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                message = MessageProtocol.parse_message(data)
                self._process_message(client_socket, message)
                
        except Exception as e:
            print(f"Client {address} error: {e}")
        finally:
            self._disconnect_client(client_socket)
    
    def _process_message(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Process a message from a client."""
        message_type = message.get('type')
        client_info = self.clients.get(client_socket)
        
        if message_type == MessageProtocol.JOIN:
            self._handle_join(client_socket, message)
        elif message_type == MessageProtocol.LEAVE:
            self._handle_leave(client_socket, message)
        elif message_type == MessageProtocol.MESSAGE:
            self._handle_message(client_socket, message)
        elif message_type == MessageProtocol.IMAGE:
            self._handle_image(client_socket, message)
        elif message_type == MessageProtocol.CREATE_THREAD:
            self._handle_create_thread(client_socket, message)
    
    def _handle_join(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Handle client join."""
        data = message.get('data', {})
        client_info = self.clients[client_socket]
        
        client_info['user_id'] = data.get('user_id')
        client_info['username'] = data.get('username')
        client_info['public_key'] = data.get('public_key')
        
        print(f"User {client_info['username']} joined")
        
        # Send welcome message
        welcome_data = {
            'message': f"Welcome {client_info['username']}!",
            'thread_id': 'main'
        }
        
        response = MessageProtocol.create_message(
            MessageProtocol.MESSAGE,
            welcome_data,
            'system'
        )
        
        client_socket.send(response)
    
    def _handle_leave(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Handle client leave."""
        client_info = self.clients.get(client_socket)
        if client_info:
            print(f"User {client_info.get('username', 'Unknown')} left")
        self._disconnect_client(client_socket)
    
    def _handle_message(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Handle text message."""
        data = message.get('data', {})
        client_info = self.clients.get(client_socket)
        
        if not client_info or not client_info.get('user_id'):
            return
        
        # Broadcast message to all clients
        broadcast_data = {
            'content': data.get('content'),
            'thread_id': data.get('thread_id', 'main'),
            'sender_id': client_info['user_id'],
            'sender_username': client_info['username'],
            'timestamp': data.get('timestamp', time.time())
        }
        
        response = MessageProtocol.create_message(
            MessageProtocol.MESSAGE,
            broadcast_data,
            client_info['user_id']
        )
        
        # Send to all connected clients
        for other_socket in self.clients.keys():
            if other_socket != client_socket:
                try:
                    other_socket.send(response)
                except:
                    pass
    
    def _handle_image(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Handle image message."""
        data = message.get('data', {})
        client_info = self.clients.get(client_socket)
        
        if not client_info or not client_info.get('user_id'):
            return
        
        # Broadcast image to all clients
        broadcast_data = {
            'image_data': data.get('image_data'),
            'thread_id': data.get('thread_id', 'main'),
            'sender_id': client_info['user_id'],
            'sender_username': client_info['username'],
            'timestamp': data.get('timestamp', time.time())
        }
        
        response = MessageProtocol.create_message(
            MessageProtocol.IMAGE,
            broadcast_data,
            client_info['user_id']
        )
        
        # Send to all connected clients
        for other_socket in self.clients.keys():
            if other_socket != client_socket:
                try:
                    other_socket.send(response)
                except:
                    pass
    
    def _handle_create_thread(self, client_socket: socket.socket, message: Dict[str, Any]):
        """Handle thread creation."""
        data = message.get('data', {})
        client_info = self.clients.get(client_socket)
        
        if not client_info or not client_info.get('user_id'):
            return
        
        thread_name = data.get('thread_name')
        is_private = data.get('is_private', False)
        creator_id = data.get('creator_id')
        
        # Generate thread ID
        import hashlib
        thread_id = hashlib.sha256(f"{thread_name}{creator_id}{time.time()}".encode()).hexdigest()[:16]
        
        # Set expiration time (12 hours for non-main threads)
        expires_at = time.time() + (12 * 60 * 60) if thread_id != 'main' else None
        
        self.threads[thread_id] = {
            'name': thread_name,
            'is_private': is_private,
            'created_at': time.time(),
            'expires_at': expires_at,
            'creator_id': creator_id
        }
        
        # Notify all clients about new thread
        thread_data = {
            'thread_id': thread_id,
            'thread_name': thread_name,
            'is_private': is_private,
            'creator_username': client_info['username'],
            'expires_at': expires_at
        }
        
        response = MessageProtocol.create_message(
            MessageProtocol.CREATE_THREAD,
            thread_data,
            client_info['user_id']
        )
        
        # Send to all connected clients
        for other_socket in self.clients.keys():
            try:
                other_socket.send(response)
            except:
                pass
    
    def _disconnect_client(self, client_socket: socket.socket):
        """Disconnect a client."""
        if client_socket in self.clients:
            client_info = self.clients[client_socket]
            print(f"Disconnecting {client_info.get('username', 'Unknown')}")
            del self.clients[client_socket]
        
        try:
            client_socket.close()
        except:
            pass
