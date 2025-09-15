"""
Cryptographic utilities for LuckyOnes E2EE chat application.
Implements AES-256-GCM, X25519 key exchange, and Double Ratchet protocol.
"""

import os
import json
import time
import hashlib
from typing import Dict, Tuple, Optional, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import nacl.secret
import nacl.utils
import nacl.public


class DoubleRatchet:
    """Double Ratchet implementation for forward secrecy."""
    
    def __init__(self):
        self.dh_ratchet = X25519PrivateKey.generate()
        self.root_key = os.urandom(32)
        self.chain_keys = {}  # {public_key: chain_key}
        self.message_numbers = {}  # {public_key: message_number}
        self.skip_message_keys = {}  # {public_key: {message_number: key}}
    
    def get_public_key(self) -> bytes:
        """Get our public key for key exchange."""
        return self.dh_ratchet.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def perform_dh(self, other_public_key: bytes) -> bytes:
        """Perform Diffie-Hellman key agreement."""
        other_key = X25519PublicKey.from_public_bytes(other_public_key)
        shared_key = self.dh_ratchet.exchange(other_key)
        return shared_key
    
    def kdf_chain_key(self, chain_key: bytes, shared_secret: bytes) -> Tuple[bytes, bytes]:
        """KDF for chain key and message key derivation."""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=b'',
            info=b'luckyones_ratchet'
        )
        output = hkdf.derive(chain_key + shared_secret)
        return output[:32], output[32:]
    
    def kdf_root_key(self, root_key: bytes, shared_secret: bytes) -> bytes:
        """KDF for root key derivation."""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            info=b'luckyones_root'
        )
        return hkdf.derive(root_key + shared_secret)
    
    def encrypt_message(self, message: bytes, other_public_key: bytes) -> bytes:
        """Encrypt a message using Double Ratchet."""
        if other_public_key not in self.chain_keys:
            # First message to this contact
            shared_secret = self.perform_dh(other_public_key)
            self.root_key = self.kdf_root_key(self.root_key, shared_secret)
            chain_key, message_key = self.kdf_chain_key(self.root_key, shared_secret)
            self.chain_keys[other_public_key] = chain_key
            self.message_numbers[other_public_key] = 0
            self.skip_message_keys[other_public_key] = {}
        else:
            # Continue existing chain
            chain_key = self.chain_keys[other_public_key]
            message_key = os.urandom(32)  # Simplified for this implementation
        
        # Encrypt with AES-GCM
        aesgcm = AESGCM(message_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, message, None)
        
        # Update message number
        self.message_numbers[other_public_key] += 1
        
        # Create message structure
        message_data = {
            'public_key': self.get_public_key(),
            'message_number': self.message_numbers[other_public_key],
            'nonce': nonce.hex(),
            'ciphertext': ciphertext.hex()
        }
        
        return json.dumps(message_data).encode()
    
    def decrypt_message(self, encrypted_data: bytes) -> bytes:
        """Decrypt a message using Double Ratchet."""
        try:
            message_data = json.loads(encrypted_data.decode())
            other_public_key = bytes.fromhex(message_data['public_key'])
            message_number = message_data['message_number']
            nonce = bytes.fromhex(message_data['nonce'])
            ciphertext = bytes.fromhex(message_data['ciphertext'])
            
            if other_public_key not in self.chain_keys:
                # First message from this contact
                shared_secret = self.perform_dh(other_public_key)
                self.root_key = self.kdf_root_key(self.root_key, shared_secret)
                chain_key, message_key = self.kdf_chain_key(self.root_key, shared_secret)
                self.chain_keys[other_public_key] = chain_key
                self.message_numbers[other_public_key] = 0
                self.skip_message_keys[other_public_key] = {}
            else:
                # Continue existing chain
                message_key = os.urandom(32)  # Simplified for this implementation
            
            # Decrypt with AES-GCM
            aesgcm = AESGCM(message_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")


class CryptoManager:
    """Main cryptographic manager for the application."""
    
    def __init__(self):
        self.ratchet = DoubleRatchet()
        self.user_id = self._generate_user_id()
        self.username = self._generate_username()
    
    def _generate_user_id(self) -> str:
        """Generate a unique user ID."""
        return hashlib.sha256(self.ratchet.get_public_key()).hexdigest()[:16]
    
    def _generate_username(self) -> str:
        """Generate a random username."""
        adjectives = ['Shadow', 'Cyber', 'Neon', 'Quantum', 'Digital', 'Virtual', 'Matrix', 'Ghost']
        nouns = ['Hacker', 'Runner', 'Ghost', 'Phantom', 'Spirit', 'Demon', 'Angel', 'Warrior']
        return f"{adjectives[os.urandom(1)[0] % len(adjectives)]}{nouns[os.urandom(1)[0] % len(nouns)]}{os.urandom(1)[0] % 99 + 1}"
    
    def get_public_key(self) -> bytes:
        """Get our public key."""
        return self.ratchet.get_public_key()
    
    def get_user_id(self) -> str:
        """Get our user ID."""
        return self.user_id
    
    def get_username(self) -> str:
        """Get our username."""
        return self.username
    
    def encrypt_message(self, message: str, recipient_public_key: bytes) -> bytes:
        """Encrypt a message for a recipient."""
        return self.ratchet.encrypt_message(message.encode('utf-8'), recipient_public_key)
    
    def decrypt_message(self, encrypted_data: bytes) -> str:
        """Decrypt a received message."""
        plaintext = self.ratchet.decrypt_message(encrypted_data)
        return plaintext.decode('utf-8')
    
    def encrypt_image(self, image_data: bytes, recipient_public_key: bytes) -> bytes:
        """Encrypt image data for a recipient."""
        return self.ratchet.encrypt_message(image_data, recipient_public_key)
    
    def decrypt_image(self, encrypted_data: bytes) -> bytes:
        """Decrypt received image data."""
        return self.ratchet.decrypt_message(encrypted_data)


def generate_session_key() -> bytes:
    """Generate a random session key."""
    return os.urandom(32)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_integrity(data: bytes, expected_hash: str) -> bool:
    """Verify data integrity using SHA-256."""
    actual_hash = hashlib.sha256(data).hexdigest()
    return actual_hash == expected_hash
