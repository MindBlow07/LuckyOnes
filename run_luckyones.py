"""
LuckyOnes Launcher
Simple launcher script for the LuckyOnes E2EE chat application.
"""

import sys
import subprocess
import os
import argparse


def run_server(port=6660):
    """Run the server."""
    print("Starting LuckyOnes Server...")
    try:
        subprocess.run([sys.executable, "luckyones_server.py", "--port", str(port)])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Failed to start server: {e}")


def run_client():
    """Run the client."""
    print("Starting LuckyOnes Client...")
    try:
        subprocess.run([sys.executable, "luckyones_client.py"])
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Failed to start client: {e}")


def run_tests():
    """Run the test suite."""
    print("Running LuckyOnes Tests...")
    try:
        result = subprocess.run([sys.executable, "test_luckyones.py"])
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run tests: {e}")
        return False


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(description="LuckyOnes E2EE Chat Launcher")
    parser.add_argument(
        "mode",
        choices=["server", "client", "test"],
        help="Mode to run: server, client, or test"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6660,
        help="Port for server mode (default: 6660)"
    )
    
    args = parser.parse_args()
    
    # Check if required files exist
    required_files = [
        "luckyones_server.py",
        "luckyones_client.py",
        "crypto_utils.py",
        "network_utils.py",
        "chat_manager.py",
        "ui_cyberpunk.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"Error: Missing required files: {', '.join(missing_files)}")
        print("Please make sure you're running this from the LuckyOnes directory.")
        sys.exit(1)
    
    if args.mode == "server":
        run_server(args.port)
    elif args.mode == "client":
        run_client()
    elif args.mode == "test":
        success = run_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
