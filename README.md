# Git Commit Risk Analyzer

A preventative Git hook powered by Machine Learning that predicts whether your staged changes are high-risk (bug-inducing) *before* you even commit them to the repository history.

## Project Structure
This repository contains the full end-to-end Machine Learning pipeline:
- `data_miner.py`: A data engineering script that uses `GitPython` to programmatically crawl through massive open-source repositories, extract historical commit diffs, and label bug-fixing commits using Regex.
- `train_advanced_model.py`: Trains a sophisticated Logistic Regression classifier using multi-modal features (TF-IDF text analysis on the diffs combined with numerical scaling on code churn metrics).
- `analyze_commit.py`: The core inference engine and Explainable AI (XAI) script. When a commit is blocked, it unpacks the model's coefficients to tell the developer *exactly* which keywords (e.g., "TODO: hack") or metrics triggered the risk threshold.
- `config.py`: Reads `.riskconfig.json` to dynamically adjust strictness based on the current Git branch.
- `install_hook.py`: An installer script that automatically configures the `.git/hooks/pre-commit` script.
- `risk_model.pkl`: The compiled, trained machine learning artifact (Logistic Regression model + StandardScaler + TfidfVectorizer).

## Authorship and Code Adaptation
**All code in this repository was written entirely by me (Yash Mishra) for this specific course project.** No code was adapted from prior projects or copied from external repositories. The implementation of the data extraction, model training, and hook inference logic are original contributions for the "Product Prototype" track. Large Language Models (LLMs) were vastly used to create a large number of `test_examples` alongside some minor debugging and brainstorming, as acknowledged in the term paper.

## Dependencies
Ensure you have Python 3.9+ installed. Since macOS manages the system Python, it is highly recommended to use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Key dependencies include `scikit-learn`, `numpy`, `scipy`, `joblib`, and `GitPython`.

## Dataset Downloading
**You do not need to manually download any datasets.** 
The `data_miner.py` script acts as an automated data engine. When executed, it programmatically clones the public `pallets/flask` repository directly from GitHub into a temporary directory, crawls thousands of commits to extract text diffs and churn metrics, generates the dataset in memory, and immediately uses it to train the model. 

## Instructions to Run
### 1. Installation & Setup
To install the Git Risk Analyzer into your local repository, run the provided installer script:
```bash
python install_hook.py
```
This will automatically configure the `.git/hooks/pre-commit` script and make it executable.

### 2. Usage
Simply stage your files and commit normally:
```bash
git add .
git commit -m "Your commit message"
```

If your changes match historical patterns of bugs or exceed your branch's configured threshold, the terminal will intercept the commit and explain why:
```text
[Risk Analyzer] Branch: 'master' | Threshold: 0.3
[Risk Analyzer] Commit risk prob: 0.83 (5 insertions, 1 deletions in 1 files)
ERROR: High-risk commit! Review needed.

--- Model Interpretability (Top Risk Factors) ---
  1. Keyword 'hack' heavily increased risk score.
  2. Keyword 'TODO' heavily increased risk score.
```

To bypass the hook in emergencies, you can use `git commit --no-verify`.

## Configuration
You can customize the analyzer by editing `.riskconfig.json`. You can define custom risk thresholds for specific branches or whitelist certain words.
