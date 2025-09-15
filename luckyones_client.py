"""
LuckyOnes E2EE Chat Client
Main client application with lobby and chat functionality.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import threading
import time
from typing import Optional

# Import our modules
from crypto_utils import CryptoManager
from network_utils import NetworkClient, MessageProtocol
from chat_manager import ChatManager
from ui_cyberpunk import LobbyWindow, ChatWindow, CyberpunkStyle


class LuckyOnesClient:
    """Main LuckyOnes client application."""
    
    def __init__(self):
        self.crypto_manager = CryptoManager()
        self.network_client = None
        self.chat_manager = ChatManager()
        self.lobby_window = None
        self.chat_window = None
        self.connected = False
        
        # Create main window (hidden initially)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        
        # Show lobby
        self._show_lobby()
    
    def _show_lobby(self):
        """Show the lobby window."""
        self.lobby_window = LobbyWindow(self._on_connect)
        self.lobby_window.show(self.crypto_manager.get_username())
    
    def _on_connect(self, host: str, port: int) -> bool:
        """Handle connection attempt."""
        try:
            # Create network client
            self.network_client = NetworkClient(self.crypto_manager)
            
            # Register message handlers
            self.network_client.register_message_handler(MessageProtocol.MESSAGE, self._on_network_message)
            self.network_client.register_message_handler(MessageProtocol.IMAGE, self._on_network_image)
            self.network_client.register_message_handler(MessageProtocol.CREATE_THREAD, self._on_network_thread)
            self.network_client.register_message_handler(MessageProtocol.ERROR, self._on_network_error)
            
            # Attempt connection
            if self.network_client.connect(host, port):
                self.connected = True
                self._show_chat()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def _show_chat(self):
        """Show the chat window."""
        if self.lobby_window:
            self.lobby_window.window.destroy()
            self.lobby_window = None
        
        self.chat_window = ChatWindow(
            self.chat_manager,
            self.network_client,
            self.crypto_manager
        )
        
        # Start chat window in a separate thread
        chat_thread = threading.Thread(target=self.chat_window.show, daemon=True)
        chat_thread.start()
    
    def _on_network_message(self, message_data: dict):
        """Handle incoming network message."""
        try:
            data = message_data.get('data', {})
            content = data.get('content', '')
            sender_id = data.get('sender_id', '')
            sender_username = data.get('sender_username', 'Unknown')
            thread_id = data.get('thread_id', 'main')
            
            # Add message to chat manager
            self.chat_manager.add_message(
                content,
                sender_id,
                sender_username,
                thread_id
            )
            
        except Exception as e:
            print(f"Error handling network message: {e}")
    
    def _on_network_image(self, message_data: dict):
        """Handle incoming network image."""
        try:
            data = message_data.get('data', {})
            image_b64 = data.get('image_data', '')
            sender_id = data.get('sender_id', '')
            sender_username = data.get('sender_username', 'Unknown')
            thread_id = data.get('thread_id', 'main')
            
            if image_b64:
                # Decode base64 image
                import base64
                image_data = base64.b64decode(image_b64)
                
                # Add image to chat manager
                self.chat_manager.add_image_message(
                    image_data,
                    sender_id,
                    sender_username,
                    thread_id
                )
            
        except Exception as e:
            print(f"Error handling network image: {e}")
    
    def _on_network_thread(self, message_data: dict):
        """Handle incoming network thread creation."""
        try:
            data = message_data.get('data', {})
            thread_id = data.get('thread_id', '')
            thread_name = data.get('thread_name', '')
            is_private = data.get('is_private', False)
            creator_id = data.get('creator_id', '')
            
            if thread_id and thread_name:
                # Create thread in chat manager
                self.chat_manager.create_thread(
                    thread_name,
                    is_private,
                    creator_id
                )
            
        except Exception as e:
            print(f"Error handling network thread: {e}")
    
    def _on_network_error(self, message_data: dict):
        """Handle network error."""
        try:
            data = message_data.get('data', {})
            error_msg = data.get('error', 'Unknown error')
            print(f"Network error: {error_msg}")
            
        except Exception as e:
            print(f"Error handling network error: {e}")
    
    def run(self):
        """Run the client application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._cleanup()
        except Exception as e:
            print(f"Client error: {e}")
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources."""
        if self.network_client:
            self.network_client.disconnect()
        
        if self.chat_manager:
            self.chat_manager.stop()
        
        if self.root:
            self.root.quit()


def main():
    """Main entry point."""
    print("Starting LuckyOnes E2EE Chat Client...")
    print("=" * 50)
    
    try:
        client = LuckyOnesClient()
        client.run()
    except Exception as e:
        print(f"Failed to start client: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
