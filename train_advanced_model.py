import joblib
import csv
import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import sys
csv.field_size_limit(sys.maxsize)

def main():
    print("Loading real-world dataset (Flask Repository)...")
    X_diff = []
    X_num = [] # Contains [lines_added, lines_deleted, files_changed]
    labels = []
    
    with open("real_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            X_diff.append(row["diff"])
            X_num.append([
                float(row["lines_added"]),
                float(row["lines_deleted"]),
                float(row["files_changed"])
            ])
            labels.append(int(row["label"]))
            
    print(f"Loaded {len(X_diff)} commits total. Risky commits: {sum(labels)}")

    # Splitting lists manually ensuring stratification given class imbalance
    X_diff_tr, X_diff_te, X_num_tr, X_num_te, y_tr, y_te = train_test_split(
        X_diff, X_num, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print("Engineering Multi-Modal Features...")
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1,2))
    X_diff_tr_vec = vectorizer.fit_transform(X_diff_tr)
    X_diff_te_vec = vectorizer.transform(X_diff_te)
    
    scaler = StandardScaler()
    X_num_tr_scl = scaler.fit_transform(X_num_tr)
    X_num_te_scl = scaler.transform(X_num_te)
    
    X_train_final = hstack([X_diff_tr_vec, X_num_tr_scl])
    X_test_final = hstack([X_diff_te_vec, X_num_te_scl])
    
    print("Training robust Logistic Regression on combined features...")
    model = LogisticRegression(C=1.0, class_weight='balanced', max_iter=1000)
    model.fit(X_train_final, y_tr)
    
    # Evaluate
    y_pred = model.predict(X_test_final)
    
    print("\n" + "="*50)
    print("REAL-WORLD TEST SET RESULTS (FLASK REPO)")
    print("="*50)
    print("Confusion Matrix:")
    print(confusion_matrix(y_te, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_te, y_pred, target_names=["Safe (0)", "Risky (1)"]))
    print("="*50)

    artifact = {
        "vectorizer": vectorizer,
        "scaler": scaler,
        "model": model
    }
    joblib.dump(artifact, "risk_model.pkl")
    print("\nMulti-Modal Pipeline saved to risk_model.pkl!")

if __name__ == "__main__":
    main()
