import logging
from github_client import github_client
from models import IssueActivity
from app import db
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def handle_comment_event(payload: dict) -> dict:
    """Handle issue_comment webhook events"""
    action = payload.get("action")

    if action != "created":
        return {"status": "ignored", "action": action}

    try:
        repo_full_name = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
        comment_body = payload["comment"].get("body", "").strip()

        logger.info(f"Processing comment on issue #{issue_number} in {repo_full_name}")

        # Update activity tracking
        try:
            activity = (
                db.session.query(IssueActivity)
                .filter_by(repo_full_name=repo_full_name, issue_number=issue_number)
                .first()
            )

            if activity:
                activity.last_activity = datetime.now(timezone.utc)
                activity.is_stale = False
                db.session.commit()

        except Exception as e:
            logger.error(f"Failed to update issue activity: {e}")
            db.session.rollback()

        # Process slash commands
        if comment_body.startswith("/"):
            return process_slash_command(repo_full_name, issue_number, comment_body)

        return {"status": "success", "message": "Comment processed"}

    except Exception as e:
        logger.error(f"Failed to handle comment event: {e}")
        return {"status": "error", "message": str(e)}


def process_slash_command(repo_full_name: str, issue_number: int, command: str) -> dict:
    """Process slash commands in comments"""
    command = command.lower().strip()
    parts = command.split()

    if not parts:
        return {"status": "error", "message": "Empty command"}

    cmd = parts[0]

    try:
        if cmd == "/close":
            github_client.close_issue(repo_full_name, issue_number)
            return {"status": "success", "action": "issue_closed"}

        elif cmd == "/area" and len(parts) > 1:
            label = parts[1]
            github_client.add_labels_to_issue(repo_full_name, issue_number, [label])
            return {"status": "success", "action": "label_added", "label": label}

        elif cmd == "/size" and len(parts) > 1:
            size = parts[1].lower()
            if size in ["s", "m", "l", "xl"]:
                size_label = f"size:{size}"
                github_client.add_labels_to_issue(
                    repo_full_name, issue_number, [size_label]
                )
                return {"status": "success", "action": "size_label_added", "size": size}
            else:
                return {
                    "status": "error",
                    "message": "Invalid size. Use s, m, l, or xl",
                }

        elif cmd == "/priority" and len(parts) > 1:
            priority = parts[1].lower()
            if priority in ["low", "medium", "high", "critical"]:
                priority_label = f"priority:{priority}"
                github_client.add_labels_to_issue(
                    repo_full_name, issue_number, [priority_label]
                )
                return {
                    "status": "success",
                    "action": "priority_label_added",
                    "priority": priority,
                }
            else:
                return {
                    "status": "error",
                    "message": "Invalid priority. Use low, medium, high, or critical",
                }

        elif cmd == "/assign" and len(parts) > 1:
            assignee = parts[1].replace("@", "")  # Remove @ if present
            github_client.assign_users_to_issue(
                repo_full_name, issue_number, [assignee]
            )
            return {
                "status": "success",
                "action": "user_assigned",
                "assignee": assignee,
            }

        else:
            return {"status": "error", "message": f"Unknown command: {cmd}"}

    except Exception as e:
        logger.error(f"Failed to process slash command '{command}': {e}")
        return {"status": "error", "message": str(e)}
