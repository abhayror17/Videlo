from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from hashlib import md5
from pathlib import Path


def verify_webhook_signature(event_uuid: str, signature_hex: str, public_key_path: str) -> bool:
    """
    Verify webhook signature using RSA public key.
    
    Args:
        event_uuid: The event UUID from the webhook
        signature_hex: The signature in hex format
        public_key_path: Path to the public key PEM file
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Load public key
        key_path = Path(public_key_path)
        if not key_path.exists():
            return False
            
        with open(key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        
        # Create MD5 hash of the event UUID
        event_data_hash = md5(event_uuid.encode()).digest()
        
        # Convert hex signature to bytes
        signature_bytes = bytes.fromhex(signature_hex)
        
        # Verify the signature
        public_key.verify(
            signature_bytes,
            event_data_hash,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False
