"""
LuckyOnes E2EE Chat Server
Main server application for handling client connections.
"""

import sys
import signal
import time
from network_utils import NetworkServer, MessageProtocol


class LuckyOnesServer:
    """Main LuckyOnes server application."""
    
    def __init__(self, port: int = 6660):
        self.port = port
        self.server = NetworkServer(port)
        self.running = False
    
    def start(self):
        """Start the server."""
        print("Starting LuckyOnes E2EE Chat Server...")
        print("=" * 50)
        print(f"Server will run on port {self.port}")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            if self.server.start():
                self.running = True
                print(f"✓ Server started successfully on port {self.port}")
                print("✓ Waiting for client connections...")
                
                # Keep server running
                while self.running:
                    time.sleep(1)
                    
            else:
                print("✗ Failed to start server")
                return False
                
        except Exception as e:
            print(f"✗ Server error: {e}")
            return False
        
        return True
    
    def stop(self):
        """Stop the server."""
        print("\nShutting down server...")
        self.running = False
        self.server.stop()
        print("✓ Server stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LuckyOnes E2EE Chat Server")
    parser.add_argument(
        "--port", 
        type=int, 
        default=6660, 
        help="Port to run the server on (default: 6660)"
    )
    
    args = parser.parse_args()
    
    # Validate port
    if not (1 <= args.port <= 65535):
        print("Error: Port must be between 1 and 65535")
        sys.exit(1)
    
    try:
        server = LuckyOnesServer(args.port)
        server.start()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    except Exception as e:
        print(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
