"""
Cyberpunk-themed UI for LuckyOnes E2EE chat application.
Purple, black, and gray color scheme with modern styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from PIL import Image, ImageTk
import io
import base64


class CyberpunkStyle:
    """Cyberpunk color scheme and styling."""
    
    # Colors
    PRIMARY = "#8B5CF6"      # Purple
    SECONDARY = "#A78BFA"    # Light purple
    BACKGROUND = "#0F0F0F"   # Dark black
    SURFACE = "#1A1A1A"      # Dark gray
    SURFACE_LIGHT = "#2D2D2D" # Medium gray
    TEXT_PRIMARY = "#FFFFFF"  # White
    TEXT_SECONDARY = "#9CA3AF" # Gray
    ACCENT = "#EC4899"       # Pink
    SUCCESS = "#10B981"      # Green
    WARNING = "#F59E0B"      # Orange
    ERROR = "#EF4444"        # Red
    
    # Fonts
    FONT_FAMILY = "Consolas"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 11
    FONT_SIZE_LARGE = 14
    FONT_SIZE_TITLE = 18


class CyberpunkButton(tk.Button):
    """Custom cyberpunk-styled button."""
    
    def __init__(self, parent, text="", command=None, **kwargs):
        # Set default font if not provided
        if 'font' not in kwargs:
            kwargs['font'] = (CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_NORMAL)
        
        # Set default bg if not provided
        if 'bg' not in kwargs:
            kwargs['bg'] = CyberpunkStyle.SURFACE
        
        # Set default fg if not provided
        if 'fg' not in kwargs:
            kwargs['fg'] = CyberpunkStyle.TEXT_PRIMARY
        
        # Set default activebackground if not provided
        if 'activebackground' not in kwargs:
            kwargs['activebackground'] = CyberpunkStyle.PRIMARY
        
        # Set default activeforeground if not provided
        if 'activeforeground' not in kwargs:
            kwargs['activeforeground'] = CyberpunkStyle.TEXT_PRIMARY
        
        # Set default relief if not provided
        if 'relief' not in kwargs:
            kwargs['relief'] = "flat"
        
        # Set default bd if not provided
        if 'bd' not in kwargs:
            kwargs['bd'] = 0
        
        # Set default padx if not provided
        if 'padx' not in kwargs:
            kwargs['padx'] = 10
        
        # Set default pady if not provided
        if 'pady' not in kwargs:
            kwargs['pady'] = 5
        
        # Set default cursor if not provided
        if 'cursor' not in kwargs:
            kwargs['cursor'] = "hand2"
        
        super().__init__(
            parent,
            text=text,
            command=command,
            **kwargs
        )
        
        # Add hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.config(bg=CyberpunkStyle.SURFACE_LIGHT)
    
    def _on_leave(self, event):
        self.config(bg=CyberpunkStyle.SURFACE)


class CyberpunkEntry(tk.Entry):
    """Custom cyberpunk-styled entry."""
    
    def __init__(self, parent, **kwargs):
        # Set default font if not provided
        if 'font' not in kwargs:
            kwargs['font'] = (CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_NORMAL)
        
        # Set default bg if not provided
        if 'bg' not in kwargs:
            kwargs['bg'] = CyberpunkStyle.SURFACE
        
        # Set default fg if not provided
        if 'fg' not in kwargs:
            kwargs['fg'] = CyberpunkStyle.TEXT_PRIMARY
        
        # Set default insertbackground if not provided
        if 'insertbackground' not in kwargs:
            kwargs['insertbackground'] = CyberpunkStyle.PRIMARY
        
        # Set default relief if not provided
        if 'relief' not in kwargs:
            kwargs['relief'] = "flat"
        
        # Set default bd if not provided
        if 'bd' not in kwargs:
            kwargs['bd'] = 1
        
        # Set default highlightthickness if not provided
        if 'highlightthickness' not in kwargs:
            kwargs['highlightthickness'] = 1
        
        # Set default highlightcolor if not provided
        if 'highlightcolor' not in kwargs:
            kwargs['highlightcolor'] = CyberpunkStyle.PRIMARY
        
        # Set default highlightbackground if not provided
        if 'highlightbackground' not in kwargs:
            kwargs['highlightbackground'] = CyberpunkStyle.SURFACE_LIGHT
        
        super().__init__(
            parent,
            **kwargs
        )


class CyberpunkText(tk.Text):
    """Custom cyberpunk-styled text widget."""
    
    def __init__(self, parent, **kwargs):
        # Set default font if not provided
        if 'font' not in kwargs:
            kwargs['font'] = (CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_NORMAL)
        
        # Set default bg if not provided
        if 'bg' not in kwargs:
            kwargs['bg'] = CyberpunkStyle.BACKGROUND
        
        # Set default fg if not provided
        if 'fg' not in kwargs:
            kwargs['fg'] = CyberpunkStyle.TEXT_PRIMARY
        
        # Set default insertbackground if not provided
        if 'insertbackground' not in kwargs:
            kwargs['insertbackground'] = CyberpunkStyle.PRIMARY
        
        # Set default relief if not provided
        if 'relief' not in kwargs:
            kwargs['relief'] = "flat"
        
        # Set default bd if not provided
        if 'bd' not in kwargs:
            kwargs['bd'] = 0
        
        # Set default highlightthickness if not provided
        if 'highlightthickness' not in kwargs:
            kwargs['highlightthickness'] = 0
        
        # Set default wrap if not provided
        if 'wrap' not in kwargs:
            kwargs['wrap'] = tk.WORD
        
        super().__init__(
            parent,
            **kwargs
        )


class CyberpunkLabel(tk.Label):
    """Custom cyberpunk-styled label."""
    
    def __init__(self, parent, text="", **kwargs):
        # Set default font if not provided
        if 'font' not in kwargs:
            kwargs['font'] = (CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_NORMAL)
        
        # Set default fg if not provided
        if 'fg' not in kwargs:
            kwargs['fg'] = CyberpunkStyle.TEXT_PRIMARY
        
        # Set default bg if not provided
        if 'bg' not in kwargs:
            kwargs['bg'] = CyberpunkStyle.BACKGROUND
        
        super().__init__(
            parent,
            text=text,
            **kwargs
        )


class CyberpunkFrame(tk.Frame):
    """Custom cyberpunk-styled frame."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=CyberpunkStyle.BACKGROUND,
            **kwargs
        )


class LobbyWindow:
    """Lobby window for server connection."""
    
    def __init__(self, on_connect: Callable):
        self.on_connect = on_connect
        self.window = None
        self.host_entry = None
        self.port_entry = None
        self.username_label = None
        self.connect_button = None
    
    def show(self, username: str):
        """Show the lobby window."""
        self.window = tk.Toplevel()
        self.window.title("LuckyOnes - Lobby")
        self.window.geometry("500x400")
        self.window.configure(bg=CyberpunkStyle.BACKGROUND)
        self.window.resizable(False, False)
        
        # Center window
        self.window.transient()
        self.window.grab_set()
        
        # Main frame
        main_frame = CyberpunkFrame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = CyberpunkLabel(
            main_frame,
            text="LUCKY ONES",
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_TITLE, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Username display
        username_frame = CyberpunkFrame(main_frame)
        username_frame.pack(fill=tk.X, pady=(0, 20))
        
        CyberpunkLabel(username_frame, text="Username:").pack(anchor=tk.W)
        self.username_label = CyberpunkLabel(
            username_frame,
            text=username,
            fg=CyberpunkStyle.PRIMARY,
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_LARGE, "bold")
        )
        self.username_label.pack(anchor=tk.W)
        
        # Connection settings
        settings_frame = CyberpunkFrame(main_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Host
        host_frame = CyberpunkFrame(settings_frame)
        host_frame.pack(fill=tk.X, pady=(0, 10))
        
        CyberpunkLabel(host_frame, text="Server Host:").pack(anchor=tk.W)
        self.host_entry = CyberpunkEntry(host_frame)
        self.host_entry.pack(fill=tk.X, pady=(5, 0))
        self.host_entry.insert(0, "127.0.0.1")
        
        # Port
        port_frame = CyberpunkFrame(settings_frame)
        port_frame.pack(fill=tk.X, pady=(0, 10))
        
        CyberpunkLabel(port_frame, text="Port:").pack(anchor=tk.W)
        self.port_entry = CyberpunkEntry(port_frame)
        self.port_entry.pack(fill=tk.X, pady=(5, 0))
        self.port_entry.insert(0, "6660")
        
        # Connect button
        self.connect_button = CyberpunkButton(
            main_frame,
            text="CONNECT",
            command=self._on_connect,
            bg=CyberpunkStyle.PRIMARY,
            fg=CyberpunkStyle.TEXT_PRIMARY
        )
        self.connect_button.pack(pady=(20, 0))
        
        # Status
        self.status_label = CyberpunkLabel(
            main_frame,
            text="Ready to connect",
            fg=CyberpunkStyle.TEXT_SECONDARY
        )
        self.status_label.pack(pady=(10, 0))
    
    def _on_connect(self):
        """Handle connect button click."""
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not host:
            messagebox.showerror("Error", "Please enter a server host")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid port number")
            return
        
        self.connect_button.config(state=tk.DISABLED, text="CONNECTING...")
        self.status_label.config(text="Connecting...", fg=CyberpunkStyle.WARNING)
        
        # Call connect callback
        success = self.on_connect(host, port)
        
        if success:
            self.window.destroy()
        else:
            self.connect_button.config(state=tk.NORMAL, text="CONNECT")
            self.status_label.config(text="Connection failed", fg=CyberpunkStyle.ERROR)


class ChatWindow:
    """Main chat window."""
    
    def __init__(self, chat_manager, network_client, crypto_manager):
        self.chat_manager = chat_manager
        self.network_client = network_client
        self.crypto_manager = crypto_manager
        self.window = None
        self.message_text = None
        self.chat_display = None
        self.thread_listbox = None
        self.create_thread_button = None
        self.send_button = None
        self.image_button = None
        self.thread_countdowns = {}
        
        # Register handlers
        self.chat_manager.register_message_handler(self._on_message_added)
        self.chat_manager.register_thread_handler(self._on_thread_event)
    
    def show(self):
        """Show the chat window."""
        self.window = tk.Tk()
        self.window.title("LuckyOnes - Chat")
        self.window.geometry("1000x700")
        self.window.configure(bg=CyberpunkStyle.BACKGROUND)
        
        # Create UI
        self._create_ui()
        
        # Start chat manager
        self.chat_manager.start()
        
        # Start main loop
        self.window.mainloop()
    
    def _create_ui(self):
        """Create the UI components."""
        # Main container
        main_container = CyberpunkFrame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top frame - title and user info
        top_frame = CyberpunkFrame(main_container)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = CyberpunkLabel(
            top_frame,
            text="LUCKY ONES",
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_TITLE, "bold"),
            fg=CyberpunkStyle.PRIMARY
        )
        title_label.pack(side=tk.LEFT)
        
        user_label = CyberpunkLabel(
            top_frame,
            text=f"User: {self.crypto_manager.get_username()}",
            fg=CyberpunkStyle.TEXT_SECONDARY
        )
        user_label.pack(side=tk.RIGHT)
        
        # Middle frame - chat and threads
        middle_frame = CyberpunkFrame(main_container)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - threads
        left_panel = CyberpunkFrame(middle_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Thread list
        thread_frame = CyberpunkFrame(left_panel)
        thread_frame.pack(fill=tk.BOTH, expand=True)
        
        CyberpunkLabel(
            thread_frame,
            text="THREADS",
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_LARGE, "bold"),
            fg=CyberpunkStyle.PRIMARY
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Thread listbox with scrollbar
        listbox_frame = CyberpunkFrame(thread_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.thread_listbox = tk.Listbox(
            listbox_frame,
            bg=CyberpunkStyle.SURFACE,
            fg=CyberpunkStyle.TEXT_PRIMARY,
            selectbackground=CyberpunkStyle.PRIMARY,
            selectforeground=CyberpunkStyle.TEXT_PRIMARY,
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_SMALL),
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.thread_listbox.yview)
        self.thread_listbox.config(yscrollcommand=scrollbar.set)
        
        self.thread_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.thread_listbox.bind("<<ListboxSelect>>", self._on_thread_select)
        
        # Thread controls
        thread_controls = CyberpunkFrame(thread_frame)
        thread_controls.pack(fill=tk.X, pady=(5, 0))
        
        self.create_thread_button = CyberpunkButton(
            thread_controls,
            text="NEW THREAD",
            command=self._create_thread_dialog
        )
        self.create_thread_button.pack(fill=tk.X)
        
        # Right panel - chat
        right_panel = CyberpunkFrame(middle_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Chat display
        chat_frame = CyberpunkFrame(right_panel)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        CyberpunkLabel(
            chat_frame,
            text="CHAT",
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_LARGE, "bold"),
            fg=CyberpunkStyle.PRIMARY
        ).pack(anchor=tk.W, pady=(0, 5))
        
        # Chat text with scrollbar
        chat_display_frame = CyberpunkFrame(chat_frame)
        chat_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = CyberpunkText(chat_display_frame)
        
        chat_scrollbar = tk.Scrollbar(chat_display_frame, orient=tk.VERTICAL, command=self.chat_display.yview)
        self.chat_display.config(yscrollcommand=chat_scrollbar.set)
        
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Message input
        input_frame = CyberpunkFrame(right_panel)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Message entry
        self.message_text = CyberpunkEntry(input_frame)
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.message_text.bind("<Return>", self._on_send_message)
        
        # Send button
        self.send_button = CyberpunkButton(
            input_frame,
            text="SEND",
            command=self._on_send_message,
            bg=CyberpunkStyle.PRIMARY
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Image button
        self.image_button = CyberpunkButton(
            input_frame,
            text="IMG",
            command=self._on_send_image
        )
        self.image_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Load initial threads
        self._update_thread_list()
    
    def _update_thread_list(self):
        """Update the thread list display."""
        self.thread_listbox.delete(0, tk.END)
        
        for thread in self.chat_manager.get_threads():
            display_text = thread.name
            if thread.thread_id != "main" and thread.expires_at:
                remaining = thread.get_time_remaining()
                if remaining and remaining.total_seconds() > 0:
                    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    if hours > 0:
                        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        time_str = f"{minutes:02d}:{seconds:02d}"
                    display_text += f" ({time_str})"
            
            self.thread_listbox.insert(tk.END, display_text)
    
    def _on_thread_select(self, event):
        """Handle thread selection."""
        selection = self.thread_listbox.curselection()
        if selection:
            thread_index = selection[0]
            threads = self.chat_manager.get_threads()
            if thread_index < len(threads):
                thread = threads[thread_index]
                self.chat_manager.set_current_thread(thread.thread_id)
                self._update_chat_display()
    
    def _update_chat_display(self):
        """Update the chat display."""
        self.chat_display.delete(1.0, tk.END)
        
        current_thread = self.chat_manager.get_current_thread()
        if not current_thread:
            return
        
        messages = self.chat_manager.get_thread_messages(current_thread.thread_id)
        
        for message in messages:
            timestamp = datetime.fromtimestamp(message.timestamp).strftime("%H:%M:%S")
            
            if message.message_type == "text":
                self.chat_display.insert(tk.END, f"[{timestamp}] {message.sender_username}: {message.content}\n")
            elif message.message_type == "image":
                self.chat_display.insert(tk.END, f"[{timestamp}] {message.sender_username}: [IMAGE]\n")
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
    
    def _on_send_message(self, event=None):
        """Handle send message."""
        message = self.message_text.get().strip()
        if not message:
            return
        
        # Add to local chat
        self.chat_manager.add_message(
            message,
            self.crypto_manager.get_user_id(),
            self.crypto_manager.get_username()
        )
        
        # Send via network
        current_thread = self.chat_manager.get_current_thread()
        if current_thread:
            self.network_client.send_message(message, current_thread.thread_id)
        
        # Clear input
        self.message_text.delete(0, tk.END)
    
    def _on_send_image(self):
        """Handle send image."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Add to local chat
            self.chat_manager.add_image_message(
                image_data,
                self.crypto_manager.get_user_id(),
                self.crypto_manager.get_username()
            )
            
            # Send via network
            current_thread = self.chat_manager.get_current_thread()
            if current_thread:
                self.network_client.send_image(image_data, current_thread.thread_id)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send image: {e}")
    
    def _create_thread_dialog(self):
        """Create new thread dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title("Create Thread")
        dialog.geometry("400x200")
        dialog.configure(bg=CyberpunkStyle.BACKGROUND)
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (self.window.winfo_rootx() + 50, self.window.winfo_rooty() + 50))
        
        main_frame = CyberpunkFrame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        CyberpunkLabel(
            main_frame,
            text="CREATE NEW THREAD",
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_LARGE, "bold"),
            fg=CyberpunkStyle.PRIMARY
        ).pack(pady=(0, 20))
        
        # Thread name
        name_frame = CyberpunkFrame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        
        CyberpunkLabel(name_frame, text="Thread Name:").pack(anchor=tk.W)
        name_entry = CyberpunkEntry(name_frame)
        name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Private checkbox
        is_private = tk.BooleanVar()
        private_check = tk.Checkbutton(
            main_frame,
            text="Private Thread",
            variable=is_private,
            bg=CyberpunkStyle.BACKGROUND,
            fg=CyberpunkStyle.TEXT_PRIMARY,
            selectcolor=CyberpunkStyle.SURFACE,
            activebackground=CyberpunkStyle.BACKGROUND,
            activeforeground=CyberpunkStyle.TEXT_PRIMARY,
            font=(CyberpunkStyle.FONT_FAMILY, CyberpunkStyle.FONT_SIZE_NORMAL)
        )
        private_check.pack(anchor=tk.W, pady=(0, 20))
        
        # Buttons
        button_frame = CyberpunkFrame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def create_thread():
            thread_name = name_entry.get().strip()
            if not thread_name:
                messagebox.showerror("Error", "Please enter a thread name")
                return
            
            # Create thread locally
            thread_id = self.chat_manager.create_thread(
                thread_name,
                is_private.get(),
                self.crypto_manager.get_user_id()
            )
            
            # Send via network
            self.network_client.create_thread(thread_name, is_private.get())
            
            dialog.destroy()
        
        CyberpunkButton(
            button_frame,
            text="CREATE",
            command=create_thread,
            bg=CyberpunkStyle.PRIMARY
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        CyberpunkButton(
            button_frame,
            text="CANCEL",
            command=dialog.destroy
        ).pack(side=tk.RIGHT)
    
    def _on_message_added(self, event_type: str, message):
        """Handle message added event."""
        if event_type == "message_added":
            self._update_chat_display()
    
    def _on_thread_event(self, event_type: str, thread):
        """Handle thread event."""
        if event_type in ["thread_created", "thread_deleted"]:
            self._update_thread_list()
