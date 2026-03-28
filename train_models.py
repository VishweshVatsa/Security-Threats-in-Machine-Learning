import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import joblib
import os

def main():
    print("Downloading MNIST... (This may take a minute)")
    X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)
    X = X / 255.0  # Normalize pixels to [0,1]
    y = y.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Scaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    print("Training KNN...")
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X_train_scaled, y_train)

    print("Training Logistic Regression...")
    log_reg = LogisticRegression(max_iter=1000)
    log_reg.fit(X_train_scaled, y_train)

    print("Training SVM (this may take 5-10 minutes)...")
    svm = SVC()
    svm.fit(X_train_scaled, y_train)

    print("Saving models to disk...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(knn, 'models/knn.pkl')
    joblib.dump(log_reg, 'models/log_reg.pkl')
    joblib.dump(svm, 'models/svm.pkl')

    print("Models saved successfully in 'models/' directory.")

if __name__ == "__main__":
    main()
