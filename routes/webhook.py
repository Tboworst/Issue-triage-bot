import json
import logging
from flask import Blueprint, request, jsonify
from security import verify_github_signature, get_webhook_secret
from handlers.issues import handle_issue_event
from handlers.comments import handle_comment_event

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle GitHub webhook events"""
    try:
        # Get request data
        signature = request.headers.get('X-Hub-Signature-256')
        event_type = request.headers.get('X-GitHub-Event')
        body = request.get_data()
        
        # Verify signature
        webhook_secret = get_webhook_secret()
        if not signature or not verify_github_signature(signature, body, webhook_secret):
            logger.warning("Invalid webhook signature")
            return jsonify({"error": "Invalid signature"}), 401
        
        # Parse payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            return jsonify({"error": "Invalid JSON"}), 400
        
        logger.info(f"Received {event_type} webhook event")
        
        # Route to appropriate handler
        result = {"status": "ignored", "event": event_type}
        
        if event_type == "issues":
            result = handle_issue_event(payload)
        elif event_type == "issue_comment":
            result = handle_comment_event(payload)
        elif event_type == "ping":
            result = {"status": "pong", "message": "Webhook configured successfully"}
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        return jsonify({"error": "Internal server error"}), 500
