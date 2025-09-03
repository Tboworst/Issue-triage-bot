import logging
from github_client import github_client
from rules_manager import rules_manager
from models import IssueActivity
from app import db
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def handle_issue_opened(payload: dict) -> dict:
    """Handle issues.opened webhook event"""
    try:
        # Extract issue information
        repo_full_name = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
        issue_title = payload["issue"].get("title", "")
        issue_body = payload["issue"].get("body", "")

        logger.info(f"Processing new issue #{issue_number} in {repo_full_name}")

        # Combine title and body for keyword matching
        issue_text = f"{issue_title} {issue_body}"

        # Match labels based on keywords
        matched_labels = rules_manager.match_labels(issue_text)
        if matched_labels:
            github_client.add_labels_to_issue(
                repo_full_name, issue_number, matched_labels
            )

        # Match owners based on path hints in the body
        matched_owners = rules_manager.match_owners(issue_body)
        if matched_owners:
            github_client.assign_users_to_issue(
                repo_full_name, issue_number, matched_owners
            )

        # Add checklist comment if body is too short
        if len(issue_body.strip()) < 40:
            checklist_comment = """Thanks for opening this issue! To help us better understand and resolve it, please provide:

- [ ] **Steps to reproduce** the issue
- [ ] **Expected behavior** vs **actual behavior**
- [ ] **Error messages or logs** (if any)
- [ ] **Environment details** (OS, browser, version, etc.)
- [ ] **Screenshots or recordings** (if applicable)

This information will help us investigate and resolve the issue more quickly."""

            github_client.add_comment_to_issue(
                repo_full_name, issue_number, checklist_comment
            )

        # Track issue activity for stale detection
        try:
            issue_activity = IssueActivity(
                repo_full_name=repo_full_name,
                issue_number=issue_number,
                last_activity=datetime.now(timezone.utc),
            )
            db.session.add(issue_activity)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to track issue activity: {e}")
            db.session.rollback()

        return {
            "status": "success",
            "issue": issue_number,
            "labels_added": matched_labels,
            "owners_assigned": matched_owners,
            "checklist_added": len(issue_body.strip()) < 40,
        }

    except Exception as e:
        logger.error(f"Failed to handle issue opened event: {e}")
        return {"status": "error", "message": str(e)}


def handle_issue_event(payload: dict) -> dict:
    """Handle various issue events"""
    action = payload.get("action")

    if action == "opened":
        import asyncio

        return asyncio.run(handle_issue_opened(payload))
    elif action in ["edited", "labeled", "assigned", "commented"]:
        # Update activity tracking for these events
        try:
            repo_full_name = payload["repository"]["full_name"]
            issue_number = payload["issue"]["number"]

            activity = (
                db.session.query(IssueActivity)
                .filter_by(repo_full_name=repo_full_name, issue_number=issue_number)
                .first()
            )

            if activity:
                activity.last_activity = datetime.now(timezone.utc)
                activity.is_stale = False  # Reset stale status on activity
                db.session.commit()

        except Exception as e:
            logger.error(f"Failed to update issue activity: {e}")
            db.session.rollback()

    return {"status": "ignored", "action": action}
