import os
import logging
from github import Github
from typing import Optional

logger = logging.getLogger(__name__)

class GitHubClient:
    """Wrapper around PyGithub for easier GitHub API interactions"""
    
    def __init__(self):
        token = os.getenv("GH_APP_TOKEN", os.getenv("GITHUB_TOKEN"))
        if not token:
            logger.warning("No GitHub token found. Set GH_APP_TOKEN or GITHUB_TOKEN environment variable.")
            self.github = None
        else:
            self.github = Github(token)
    
    def get_repo(self, full_name: str):
        """Get repository by full name (owner/repo)"""
        if not self.github:
            raise ValueError("GitHub client not initialized - missing token")
        return self.github.get_repo(full_name)
    
    def get_issue(self, repo_full_name: str, issue_number: int):
        """Get specific issue from repository"""
        repo = self.get_repo(repo_full_name)
        return repo.get_issue(number=issue_number)
    
    def add_labels_to_issue(self, repo_full_name: str, issue_number: int, labels: list):
        """Add labels to an issue"""
        try:
            issue = self.get_issue(repo_full_name, issue_number)
            if labels:
                issue.add_to_labels(*labels)
                logger.info(f"Added labels {labels} to issue #{issue_number} in {repo_full_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to add labels to issue: {e}")
            return False
    
    def assign_users_to_issue(self, repo_full_name: str, issue_number: int, assignees: list):
        """Assign users to an issue"""
        try:
            issue = self.get_issue(repo_full_name, issue_number)
            if assignees:
                issue.add_to_assignees(*assignees)
                logger.info(f"Assigned {assignees} to issue #{issue_number} in {repo_full_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to assign users to issue: {e}")
            return False
    
    def add_comment_to_issue(self, repo_full_name: str, issue_number: int, comment: str):
        """Add a comment to an issue"""
        try:
            issue = self.get_issue(repo_full_name, issue_number)
            issue.create_comment(comment)
            logger.info(f"Added comment to issue #{issue_number} in {repo_full_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment to issue: {e}")
            return False
    
    def close_issue(self, repo_full_name: str, issue_number: int):
        """Close an issue"""
        try:
            issue = self.get_issue(repo_full_name, issue_number)
            issue.edit(state="closed")
            logger.info(f"Closed issue #{issue_number} in {repo_full_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to close issue: {e}")
            return False
    
    def get_open_issues_older_than(self, repo_full_name: str, days: int):
        """Get open issues older than specified days"""
        try:
            repo = self.get_repo(repo_full_name)
            from datetime import datetime, timedelta
            cutoff_date = datetime.now(datetime.timezone.utc) - timedelta(days=days)
            
            issues = repo.get_issues(state='open', sort='created', direction='asc')
            old_issues = []
            
            for issue in issues:
                if issue.created_at < cutoff_date:
                    # Check if last activity (comments, labels, etc.) is also old
                    last_activity = max(
                        issue.created_at,
                        issue.updated_at if issue.updated_at else issue.created_at
                    )
                    if last_activity < cutoff_date:
                        old_issues.append(issue)
                else:
                    break  # Issues are sorted by creation date, so we can stop here
                    
            return old_issues
        except Exception as e:
            logger.error(f"Failed to get old issues: {e}")
            return []

# Global instance
github_client = GitHubClient()
