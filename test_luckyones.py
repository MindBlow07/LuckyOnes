"""
Test script for LuckyOnes E2EE Chat Application
Tests basic functionality without requiring GUI.
"""

import sys
import time
import threading
from crypto_utils import CryptoManager
from network_utils import NetworkServer, NetworkClient, MessageProtocol
from chat_manager import ChatManager


def test_crypto():
    """Test cryptographic functions."""
    print("Testing cryptographic functions...")
    
    try:
        crypto = CryptoManager()
        
        # Test key generation
        public_key = crypto.get_public_key()
        user_id = crypto.get_user_id()
        username = crypto.get_username()
        
        print(f"✓ Generated user ID: {user_id}")
        print(f"✓ Generated username: {username}")
        print(f"✓ Generated public key: {public_key.hex()[:16]}...")
        
        # Test message encryption/decryption
        test_message = "Hello, this is a test message!"
        encrypted = crypto.encrypt_message(test_message, public_key)
        decrypted = crypto.decrypt_message(encrypted)
        
        if decrypted == test_message:
            print("✓ Message encryption/decryption works")
        else:
            print("✗ Message encryption/decryption failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Crypto test failed: {e}")
        return False


def test_chat_manager():
    """Test chat manager functionality."""
    print("\nTesting chat manager...")
    
    try:
        chat_manager = ChatManager()
        chat_manager.start()
        
        # Test thread creation
        thread_id = chat_manager.create_thread("Test Thread", False, "test_user")
        print(f"✓ Created thread: {thread_id}")
        
        # Test message addition
        message = chat_manager.add_message(
            "Test message",
            "test_user",
            "TestUser",
            thread_id
        )
        
        if message:
            print("✓ Added message to thread")
        else:
            print("✗ Failed to add message")
            return False
        
        # Test thread retrieval
        threads = chat_manager.get_threads()
        if len(threads) >= 2:  # Main thread + test thread
            print(f"✓ Retrieved {len(threads)} threads")
        else:
            print("✗ Failed to retrieve threads")
            return False
        
        chat_manager.stop()
        return True
        
    except Exception as e:
        print(f"✗ Chat manager test failed: {e}")
        return False


def test_server():
    """Test server functionality."""
    print("\nTesting server...")
    
    try:
        server = NetworkServer(6661)  # Use different port for testing
        
        # Start server in background
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(1)
        
        if server.running:
            print("✓ Server started successfully")
        else:
            print("✗ Server failed to start")
            return False
        
        # Stop server
        server.stop()
        return True
        
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False


def test_client_server_communication():
    """Test client-server communication."""
    print("\nTesting client-server communication...")
    
    try:
        # Start server
        server = NetworkServer(6662)  # Use different port for testing
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        time.sleep(1)
        
        if not server.running:
            print("✗ Server not running")
            return False
        
        # Create client
        crypto = CryptoManager()
        client = NetworkClient(crypto)
        
        # Connect to server
        if client.connect("127.0.0.1", 6662):
            print("✓ Client connected to server")
            
            # Send a test message
            if client.send_message("Test message from client", "main"):
                print("✓ Client sent message")
            else:
                print("✗ Client failed to send message")
                return False
            
            # Disconnect
            client.disconnect()
            print("✓ Client disconnected")
        else:
            print("✗ Client failed to connect")
            return False
        
        # Stop server
        server.stop()
        return True
        
    except Exception as e:
        print(f"✗ Client-server communication test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("LuckyOnes E2EE Chat Application - Test Suite")
    print("=" * 50)
    
    tests = [
        test_crypto,
        test_chat_manager,
        test_server,
        test_client_server_communication
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
