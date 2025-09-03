import logging
from datetime import datetime, timedelta, timezone
from github_client import github_client
from models import IssueActivity
from app import db
import os

logger = logging.getLogger(__name__)


def check_stale_issues():
    """Background job to check and mark stale issues"""
    from app import app

    with app.app_context():
        try:
            stale_days = int(os.getenv("STALE_DAYS", "14"))  # Default 14 days
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=stale_days)

            logger.info(f"Checking for issues stale after {stale_days} days")

            # Find issues that haven't been active and aren't already marked as stale
            stale_issues = (
                db.session.query(IssueActivity)
                .filter(
                    IssueActivity.last_activity < cutoff_date,
                    IssueActivity.is_stale == False,
                )
                .all()
            )

            logger.info(f"Found {len(stale_issues)} potentially stale issues")

            for issue_activity in stale_issues:
                try:
                    repo_full_name = issue_activity.repo_full_name
                    issue_number = issue_activity.issue_number

                    # Check if the issue is still open on GitHub
                    issue = github_client.get_issue(repo_full_name, issue_number)

                    if issue.state == "open":
                        # Add stale label
                        github_client.add_labels_to_issue(
                            repo_full_name, issue_number, ["stale"]
                        )

                        # Post stale comment
                        stale_comment = f"""This issue has been automatically marked as stale because it has not had recent activity for {stale_days} days.

It will be closed in 7 days if no further activity occurs. To keep this issue open:
- Add a comment explaining why this issue should remain open
- Remove the `stale` label
- Add the `pinned` label to prevent future stale marking

Thank you for your contributions!"""

                        github_client.add_comment_to_issue(
                            repo_full_name, issue_number, stale_comment
                        )

                        # Mark as stale in our database
                        issue_activity.is_stale = True
                        db.session.commit()

                        logger.info(
                            f"Marked issue #{issue_number} in {repo_full_name} as stale"
                        )

                    else:
                        # Issue is closed, remove from tracking
                        db.session.delete(issue_activity)
                        db.session.commit()
                        logger.info(
                            f"Removed closed issue #{issue_number} from tracking"
                        )

                except Exception as e:
                    logger.error(
                        f"Failed to process stale issue {issue_activity.repo_full_name}#{issue_activity.issue_number}: {e}"
                    )
                    db.session.rollback()
                    continue

            # Clean up very old stale issues (close them after additional time)
            close_days = int(
                os.getenv("STALE_CLOSE_DAYS", "7")
            )  # Additional days before closing
            close_cutoff = datetime.now(timezone.utc) - timedelta(
                days=stale_days + close_days
            )

            very_stale_issues = (
                db.session.query(IssueActivity)
                .filter(
                    IssueActivity.last_activity < close_cutoff,
                    IssueActivity.is_stale == True,
                )
                .all()
            )

            for issue_activity in very_stale_issues:
                try:
                    repo_full_name = issue_activity.repo_full_name
                    issue_number = issue_activity.issue_number

                    # Check if issue is still open and has stale label
                    issue = github_client.get_issue(repo_full_name, issue_number)

                    if issue.state == "open":
                        stale_labels = [label.name for label in issue.labels]
                        if "stale" in stale_labels and "pinned" not in stale_labels:
                            # Close the issue
                            close_comment = "This issue has been automatically closed due to inactivity. If you believe this issue is still relevant, please reopen it or create a new issue with updated information."

                            github_client.add_comment_to_issue(
                                repo_full_name, issue_number, close_comment
                            )
                            github_client.close_issue(repo_full_name, issue_number)

                            logger.info(
                                f"Automatically closed stale issue #{issue_number} in {repo_full_name}"
                            )

                    # Remove from tracking
                    db.session.delete(issue_activity)
                    db.session.commit()

                except Exception as e:
                    logger.error(
                        f"Failed to close stale issue {issue_activity.repo_full_name}#{issue_activity.issue_number}: {e}"
                    )
                    db.session.rollback()
                    continue

            logger.info("Stale issue check completed")

        except Exception as e:
            logger.error(f"Failed to check stale issues: {e}")
