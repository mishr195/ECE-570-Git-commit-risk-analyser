import os
import re
import csv
import git
import sys
import shutil

class GitRiskMiner:

    def __init__(self, repo_url, target_dir="mining_repo"):
        self.repo_url = repo_url
        self.target_dir = target_dir
        self.bug_patterns = [
            re.compile(r'fix(es|ed)?\s*#?\d+', re.IGNORECASE),
            re.compile(r'resolv(es|ed)?\s*#?\d+', re.IGNORECASE),
            re.compile(r'bug\s*fix', re.IGNORECASE),
            re.compile(r'patch(ed)?', re.IGNORECASE)
        ]
        
    def _clone_or_load(self):
        if not os.path.exists(self.target_dir):
            print(f"Cloning {self.repo_url} into {self.target_dir}...")
            return git.Repo.clone_from(self.repo_url, self.target_dir)
        print(f"Loading existing repository from {self.target_dir}...")
        return git.Repo(self.target_dir)

    def _is_bug_fix(self, message):
        for pattern in self.bug_patterns:
            if pattern.search(message):
                return True
        return False

    def mine_commits(self, max_commits=1000, output_csv="real_dataset.csv"):
        repo = self._clone_or_load()
        commits = list(repo.iter_commits('HEAD', max_count=max_commits))
        
        print(f"Successfully loaded {len(commits)} commits. Starting extraction...")
        dataset = []
        
        for commit in commits:
            if len(commit.parents) > 1:
                continue
                
            message = commit.message.strip()
            label = 1 if self._is_bug_fix(message) else 0
            stats = commit.stats.total
            lines_added = stats['insertions']
            lines_deleted = stats['deletions']
            files_changed = stats['files']
            
            if commit.parents:
                parent = commit.parents[0]
                diff_index = parent.diff(commit, create_patch=True)
                diff_text = ""
                for diff_item in diff_index:
                    if diff_item.diff:
                        try:
                            diff_text += diff_item.diff.decode('utf-8', errors='ignore') + "\n"
                        except Exception:
                            pass
            else:
                diff_text = ""
                
            if not diff_text.strip():
                continue
                
            dataset.append({
                "commit_hash": commit.hexsha,
                "label": label,
                "lines_added": lines_added,
                "lines_deleted": lines_deleted,
                "files_changed": files_changed,
                "diff": diff_text[:5000] # Limit size per diff
            })
            
            if len(dataset) % 100 == 0:
                print(f"Processed {len(dataset)} commits...")
                
        self._export_to_csv(dataset, output_csv)
        
    def _export_to_csv(self, dataset, output_file):
        if not dataset:
            print("No data extracted!")
            return
            
        print(f"Exporting {len(dataset)} records to {output_file}...")
        keys = dataset[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(dataset)
        print("Data Engineering Pipeline complete.")

if __name__ == "__main__":
    # Example usage mining a smaller repository to build the dataset
    miner = GitRiskMiner(repo_url="https://github.com/pallets/flask.git")
    miner.mine_commits(max_commits=5000)
