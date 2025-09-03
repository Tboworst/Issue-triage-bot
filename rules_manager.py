import json
import os
import logging
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class RulesManager:
    """Manage label and owner assignment rules"""
    
    def __init__(self):
        self.rules_dir = Path("rules")
        self.rules_dir.mkdir(exist_ok=True)
        self.labels_file = self.rules_dir / "labels.json"
        self.owners_file = self.rules_dir / "owners.json"
        
    def load_label_rules(self) -> Dict[str, List[str]]:
        """Load label assignment rules from JSON file"""
        try:
            if self.labels_file.exists():
                with open(self.labels_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load label rules: {e}")
        
        # Return default rules if file doesn't exist or failed to load
        return {
            "bug": ["error", "exception", "crash", "fail", "broken", "issue"],
            "feature": ["feature", "enhancement", "request", "proposal", "improve"],
            "documentation": ["docs", "documentation", "readme", "guide", "tutorial"],
            "question": ["question", "help", "how", "why", "what"],
            "duplicate": ["duplicate", "same", "already", "exists"],
            "wontfix": ["wontfix", "rejected", "invalid"],
            "performance": ["slow", "performance", "speed", "optimize", "lag"],
            "security": ["security", "vulnerability", "exploit", "attack"]
        }
    
    def save_label_rules(self, rules: Dict[str, List[str]]) -> bool:
        """Save label assignment rules to JSON file"""
        try:
            with open(self.labels_file, 'w') as f:
                json.dump(rules, f, indent=2)
            logger.info("Label rules saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save label rules: {e}")
            return False
    
    def load_owner_rules(self) -> Dict[str, List[str]]:
        """Load owner assignment rules from JSON file"""
        try:
            if self.owners_file.exists():
                with open(self.owners_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load owner rules: {e}")
        
        # Return default rules if file doesn't exist or failed to load
        return {
            "src/api/": ["api-team", "backend-team"],
            "src/web/": ["frontend-team", "ui-team"],
            "src/mobile/": ["mobile-team"],
            "docs/": ["docs-team", "technical-writers"],
            "test/": ["qa-team", "testing-team"],
            "config/": ["devops-team", "infrastructure-team"],
            "scripts/": ["devops-team"],
            "database/": ["database-team", "backend-team"]
        }
    
    def save_owner_rules(self, rules: Dict[str, List[str]]) -> bool:
        """Save owner assignment rules to JSON file"""
        try:
            with open(self.owners_file, 'w') as f:
                json.dump(rules, f, indent=2)
            logger.info("Owner rules saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save owner rules: {e}")
            return False
    
    def match_labels(self, text: str) -> List[str]:
        """Match text against label rules and return applicable labels"""
        rules = self.load_label_rules()
        text_lower = text.lower()
        matched_labels = []
        
        for label, keywords in rules.items():
            if any(keyword in text_lower for keyword in keywords):
                matched_labels.append(label)
        
        return matched_labels
    
    def match_owners(self, text: str) -> List[str]:
        """Match text against owner rules and return applicable owners"""
        rules = self.load_owner_rules()
        matched_owners = []
        
        for path, owners in rules.items():
            if path in text:
                matched_owners.extend(owners)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(matched_owners))

# Global instance
rules_manager = RulesManager()

