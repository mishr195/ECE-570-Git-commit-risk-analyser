import subprocess, sys, joblib
import numpy as np
from scipy.sparse import hstack
from config import ConfigManager
import os

def get_staged_stats():
    diff_cmd = ["git", "diff", "--cached", "--numstat"]
    out = subprocess.check_output(diff_cmd, text=True).strip()
    if not out:
        return 0, 0, 0
    
    lines_added = 0
    lines_deleted = 0
    files_changed = 0
    
    for line in out.split('\n'):
        parts = line.split()
        if len(parts) >= 3:
            added = parts[0]
            deleted = parts[1]
            if added != '-': lines_added += int(added)
            if deleted != '-': lines_deleted += int(deleted)
            files_changed += 1
            
    return lines_added, lines_deleted, files_changed

def explain_prediction(diff, vectorizer, model, diff_vec):
    try:
        feature_names = vectorizer.get_feature_names_out()
        coefficients = model.coef_[0]
        
        nonzero_indices = diff_vec.nonzero()[1]
        
        contributions = []
        for idx in nonzero_indices:
            word = feature_names[idx]
            weight = coefficients[idx]
            tf_idf_val = diff_vec[0, idx]
            contribution = weight * tf_idf_val
            contributions.append((word, contribution))
            
        contributions.sort(key=lambda x: x[1], reverse=True)
        
        print("\n--- Model Interpretability (Top Risk Factors) ---")
        if not contributions:
            print("  No significant risky keywords found in diff.")
            return
            
        # Print top 3 contributing factors
        for i, (word, score) in enumerate(contributions[:3]):
            if score > 0:
                print(f"  {i+1}. Keyword '{word}' heavily increased risk score.")
    except Exception as e:
        print(f"  [XAI Unavailable] {e}")

def analyze_staged_changes():
    config = ConfigManager()
    threshold = config.get_threshold()
    
    # Get the staged diff from git
    diff_cmd = ["git", "diff", "--cached"]
    diff = subprocess.check_output(diff_cmd, text=True)
    
    if not diff.strip(): return 0
    
    lines_added, lines_deleted, files_changed = get_staged_stats()
        
    model_path = os.path.join(os.path.dirname(__file__), "risk_model.pkl")
    try:
        artifact = joblib.load(model_path)
    except Exception:
        print("[Risk Analyzer Error] Model not found. Did you run the training script?")
        return 0
        
    vectorizer = artifact["vectorizer"]
    scaler = artifact["scaler"]
    model = artifact["model"]
    
    X_diff_vec = vectorizer.transform([diff])
    X_num = [[float(lines_added), float(lines_deleted), float(files_changed)]]
    X_num_scl = scaler.transform(X_num)
    X_final = hstack([X_diff_vec, X_num_scl])
    
    prob = model.predict_proba(X_final)[0][1]
    
    print(f"\n[Risk Analyzer] Branch: '{config.get_current_branch()}' | Threshold: {threshold}")
    print(f"[Risk Analyzer] Commit risk prob: {prob:.2f} ({lines_added} insertions, {lines_deleted} deletions in {files_changed} files)")
    
    if prob >= threshold:
        print("ERROR: High-risk commit! Review needed.")
        explain_prediction(diff, vectorizer, model, X_diff_vec)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(analyze_staged_changes())
