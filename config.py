import json
import os
import subprocess

class ConfigManager:
    """
    Handles repository-specific configuration for the Git Risk Analyzer.
    Allows dynamic risk thresholds based on the current Git branch.
    """
    def __init__(self, config_path=".riskconfig.json"):
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self.config = self._load_config()

    def _load_config(self):
        default_config = {
            "thresholds": {"default": 0.5},
            "ignored_extensions": [],
            "whitelist_words": []
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge dictionaries safely
                    default_config.update(user_config)
            except Exception as e:
                print(f"[Warning] Failed to load {self.config_path}: {e}")
        return default_config

    def get_current_branch(self):
        try:
            branch = subprocess.check_output(
                ["git", "branch", "--show-current"], 
                text=True
            ).strip()
            return branch
        except Exception:
            return "default"

    def get_threshold(self):
        branch = self.get_current_branch()
        thresholds = self.config.get("thresholds", {})
        
        # Return branch specific threshold if it exists, otherwise default
        if branch in thresholds:
            return thresholds[branch]
        return thresholds.get("default", 0.5)

    def is_file_ignored(self, filename):
        exts = self.config.get("ignored_extensions", [])
        return any(filename.endswith(ext) for ext in exts)

    def contains_whitelist(self, message):
        words = self.config.get("whitelist_words", [])
        return any(word.lower() in message.lower() for word in words)

if __name__ == "__main__":
    cm = ConfigManager()
    print(f"Current Branch: {cm.get_current_branch()}")
    print(f"Active Threshold: {cm.get_threshold()}")
