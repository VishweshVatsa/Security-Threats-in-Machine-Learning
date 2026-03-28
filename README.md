# Security Threats in Machine Learning

This project demonstrates the vulnerability of standard machine learning image classifiers to simple adversarial attacks. It trains three classical ML models on the MNIST handwritten digit dataset and evaluates their performance drop when subjected to adversarial noise.

## 🚀 Features

*   **Dataset**: Uses the classic MNIST dataset (784 features, normalized and standardized).
*   **Models Evaluated**:
    *   K-Nearest Neighbors (KNN)
    *   Logistic Regression
    *   Support Vector Machine (SVM)
*   **Adversarial Attack Simulation**: Introduces a custom `add_stronger_adversarial_noise` function which creates adversarial examples by adding scaled noise to the test images.
*   **Visualizations**: Includes sample image plots, confusion matrices for the clean evaluations, and bar charts comparing the accuracy of the models on clean vs. adversarial data.

## 📋 Requirements

Ensure you have Python installed along with the following data science libraries:

```bash
pip install numpy matplotlib scikit-learn
```

## 🛠️ Usage

To run the pipeline, simply execute the `main.py` script:

```bash
python main.py
```

The script will:
1. Download and preprocess the MNIST dataset.
2. Display sample images.
3. Train the KNN, Logistic Regression, and SVM models.
4. Output the baseline accuracy and confusion matrices for each.
5. Generate an adversarial test set.
6. Evaluate and print the accuracy of the models on the adversarial data.
7. Display a final comparative bar chart showing the performance degradation.

## 📁 Project Structure

*   `main.py`: The core script containing the entire pipeline from data loading to adversarial evaluation. This is originally derived from a Google Colab notebook (`PBLMTE.ipynb`).
*   `README.md`: This project documentation file.
