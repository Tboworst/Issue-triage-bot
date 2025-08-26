import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

def verify_github_signature(signature_header: str, body: bytes, secret: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC SHA-256
    
    Args:
        signature_header: The X-Hub-Signature-256 header value
        body: The raw request body
        secret: The webhook secret
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature_header:
        logger.warning("No signature header provided")
        return False
    
    if not secret:
        logger.warning("No webhook secret configured")
        return False
    
    try:
        # GitHub sends signature as "sha256=<hash>"
        if not signature_header.startswith('sha256='):
            logger.warning("Invalid signature format")
            return False
        
        # Extract the hash part
        expected_hash = signature_header[7:]
        
        # Compute the HMAC
        computed_hash = hmac.new(
            secret.encode('utf-8'),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        is_valid = hmac.compare_digest(expected_hash, computed_hash)
        
        if not is_valid:
            logger.warning("Invalid webhook signature")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False

def get_webhook_secret():
    """Get webhook secret from environment"""
    import os
    return os.getenv("GH_WEBHOOK_SECRET", "")
