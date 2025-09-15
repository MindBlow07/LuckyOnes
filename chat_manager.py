"""
Chat management system for LuckyOnes E2EE chat application.
Handles threads, messages, and auto-deletion timers.
"""

import time
import threading
import base64
import os
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import io


class ChatMessage:
    """Represents a chat message."""
    
    def __init__(self, content: str, sender_id: str, sender_username: str, 
                 thread_id: str, timestamp: float, message_type: str = "text"):
        self.content = content
        self.sender_id = sender_id
        self.sender_username = sender_username
        self.thread_id = thread_id
        self.timestamp = timestamp
        self.message_type = message_type  # "text" or "image"
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            'content': self.content,
            'sender_id': self.sender_id,
            'sender_username': self.sender_username,
            'thread_id': self.thread_id,
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChatMessage':
        """Create message from dictionary."""
        message = cls(
            content=data['content'],
            sender_id=data['sender_id'],
            sender_username=data['sender_username'],
            thread_id=data['thread_id'],
            timestamp=data['timestamp'],
            message_type=data.get('message_type', 'text')
        )
        message.created_at = datetime.fromisoformat(data['created_at'])
        return message


class ChatThread:
    """Represents a chat thread."""
    
    def __init__(self, thread_id: str, name: str, is_private: bool = False, 
                 creator_id: str = None, expires_hours: int = 12):
        self.thread_id = thread_id
        self.name = name
        self.is_private = is_private
        self.creator_id = creator_id
        self.created_at = datetime.now()
        self.expires_at = None
        self.messages = []
        self.participants = set()
        
        # Set expiration time (main thread never expires)
        if thread_id != "main" and expires_hours > 0:
            self.expires_at = self.created_at + timedelta(hours=expires_hours)
    
    def add_message(self, message: ChatMessage):
        """Add a message to the thread."""
        self.messages.append(message)
        self.participants.add(message.sender_id)
    
    def is_expired(self) -> bool:
        """Check if thread has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def get_time_remaining(self) -> Optional[timedelta]:
        """Get time remaining until expiration."""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def to_dict(self) -> Dict:
        """Convert thread to dictionary."""
        return {
            'thread_id': self.thread_id,
            'name': self.name,
            'is_private': self.is_private,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'message_count': len(self.messages),
            'participant_count': len(self.participants)
        }


class ImageManager:
    """Manages image storage and auto-deletion."""
    
    def __init__(self, temp_dir: str = "temp_images"):
        self.temp_dir = temp_dir
        self.images = {}  # {image_id: image_info}
        self.cleanup_thread = None
        self.running = False
        
        # Create temp directory
        os.makedirs(temp_dir, exist_ok=True)
    
    def start(self):
        """Start the image manager."""
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self):
        """Stop the image manager."""
        self.running = False
        self._cleanup_all_images()
    
    def store_image(self, image_data: bytes, sender_id: str, thread_id: str) -> str:
        """Store an image and return its ID."""
        import hashlib
        image_id = hashlib.sha256(f"{image_data}{sender_id}{time.time()}".encode()).hexdigest()[:16]
        
        # Save image to temp file
        image_path = os.path.join(self.temp_dir, f"{image_id}.jpg")
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        # Store image info
        self.images[image_id] = {
            'path': image_path,
            'sender_id': sender_id,
            'thread_id': thread_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=30)  # 30 min expiration
        }
        
        return image_id
    
    def get_image(self, image_id: str) -> Optional[bytes]:
        """Get image data by ID."""
        if image_id not in self.images:
            return None
        
        image_info = self.images[image_id]
        if datetime.now() > image_info['expires_at']:
            self._delete_image(image_id)
            return None
        
        try:
            with open(image_info['path'], 'rb') as f:
                return f.read()
        except:
            return None
    
    def get_image_thumbnail(self, image_id: str, size: tuple = (200, 200)) -> Optional[ImageTk.PhotoImage]:
        """Get image thumbnail for display."""
        image_data = self.get_image(image_id)
        if not image_data:
            return None
        
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except:
            return None
    
    def _delete_image(self, image_id: str):
        """Delete an image."""
        if image_id in self.images:
            image_info = self.images[image_id]
            try:
                os.remove(image_info['path'])
            except:
                pass
            del self.images[image_id]
    
    def _cleanup_loop(self):
        """Cleanup loop for expired images."""
        while self.running:
            try:
                current_time = datetime.now()
                expired_images = []
                
                for image_id, image_info in self.images.items():
                    if current_time > image_info['expires_at']:
                        expired_images.append(image_id)
                
                for image_id in expired_images:
                    self._delete_image(image_id)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Image cleanup error: {e}")
                time.sleep(60)
    
    def _cleanup_all_images(self):
        """Clean up all images."""
        for image_id in list(self.images.keys()):
            self._delete_image(image_id)


class ChatManager:
    """Main chat management system."""
    
    def __init__(self):
        self.threads = {}  # {thread_id: ChatThread}
        self.current_thread_id = "main"
        self.message_handlers = []
        self.thread_handlers = []
        self.image_manager = ImageManager()
        self.cleanup_thread = None
        self.running = False
        
        # Create main thread
        self._create_main_thread()
    
    def start(self):
        """Start the chat manager."""
        self.running = True
        self.image_manager.start()
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self):
        """Stop the chat manager."""
        self.running = False
        self.image_manager.stop()
    
    def _create_main_thread(self):
        """Create the main thread."""
        main_thread = ChatThread(
            thread_id="main",
            name="Main Chat",
            is_private=False,
            creator_id="system"
        )
        self.threads["main"] = main_thread
        self.current_thread_id = "main"
    
    def create_thread(self, name: str, is_private: bool = False, creator_id: str = None) -> str:
        """Create a new thread."""
        import hashlib
        thread_id = hashlib.sha256(f"{name}{creator_id}{time.time()}".encode()).hexdigest()[:16]
        
        thread = ChatThread(
            thread_id=thread_id,
            name=name,
            is_private=is_private,
            creator_id=creator_id
        )
        
        self.threads[thread_id] = thread
        
        # Notify handlers
        for handler in self.thread_handlers:
            try:
                handler('thread_created', thread)
            except:
                pass
        
        return thread_id
    
    def add_message(self, content: str, sender_id: str, sender_username: str, 
                   thread_id: str = None, message_type: str = "text") -> ChatMessage:
        """Add a message to a thread."""
        if thread_id is None:
            thread_id = self.current_thread_id
        
        if thread_id not in self.threads:
            return None
        
        message = ChatMessage(
            content=content,
            sender_id=sender_id,
            sender_username=sender_username,
            thread_id=thread_id,
            timestamp=time.time(),
            message_type=message_type
        )
        
        self.threads[thread_id].add_message(message)
        
        # Notify handlers
        for handler in self.message_handlers:
            try:
                handler('message_added', message)
            except:
                pass
        
        return message
    
    def add_image_message(self, image_data: bytes, sender_id: str, sender_username: str, 
                         thread_id: str = None) -> ChatMessage:
        """Add an image message to a thread."""
        if thread_id is None:
            thread_id = self.current_thread_id
        
        if thread_id not in self.threads:
            return None
        
        # Store image
        image_id = self.image_manager.store_image(image_data, sender_id, thread_id)
        
        # Create message with image reference
        message = ChatMessage(
            content=f"[IMAGE:{image_id}]",
            sender_id=sender_id,
            sender_username=sender_username,
            thread_id=thread_id,
            timestamp=time.time(),
            message_type="image"
        )
        
        self.threads[thread_id].add_message(message)
        
        # Notify handlers
        for handler in self.message_handlers:
            try:
                handler('message_added', message)
            except:
                pass
        
        return message
    
    def get_thread_messages(self, thread_id: str = None) -> List[ChatMessage]:
        """Get messages from a thread."""
        if thread_id is None:
            thread_id = self.current_thread_id
        
        if thread_id not in self.threads:
            return []
        
        return self.threads[thread_id].messages.copy()
    
    def get_threads(self) -> List[ChatThread]:
        """Get all threads."""
        return list(self.threads.values())
    
    def get_thread(self, thread_id: str) -> Optional[ChatThread]:
        """Get a specific thread."""
        return self.threads.get(thread_id)
    
    def set_current_thread(self, thread_id: str):
        """Set the current active thread."""
        if thread_id in self.threads:
            self.current_thread_id = thread_id
    
    def get_current_thread(self) -> Optional[ChatThread]:
        """Get the current active thread."""
        return self.threads.get(self.current_thread_id)
    
    def register_message_handler(self, handler: Callable):
        """Register a message event handler."""
        self.message_handlers.append(handler)
    
    def register_thread_handler(self, handler: Callable):
        """Register a thread event handler."""
        self.thread_handlers.append(handler)
    
    def _cleanup_loop(self):
        """Cleanup loop for expired threads."""
        while self.running:
            try:
                expired_threads = []
                
                for thread_id, thread in self.threads.items():
                    if thread.is_expired():
                        expired_threads.append(thread_id)
                
                for thread_id in expired_threads:
                    if thread_id != "main":  # Never delete main thread
                        self._delete_thread(thread_id)
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Thread cleanup error: {e}")
                time.sleep(60)
    
    def _delete_thread(self, thread_id: str):
        """Delete a thread."""
        if thread_id in self.threads and thread_id != "main":
            thread = self.threads[thread_id]
            del self.threads[thread_id]
            
            # If this was the current thread, switch to main
            if self.current_thread_id == thread_id:
                self.current_thread_id = "main"
            
            # Notify handlers
            for handler in self.thread_handlers:
                try:
                    handler('thread_deleted', thread)
                except:
                    pass
