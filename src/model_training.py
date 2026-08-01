from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from src.feature_engineering import prepare_ml_data


def train_models(X_train, y_train):
    """Train baseline machine-learning models."""

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced"
        ),
    }

    trained_models = {}

    for model_name, model in models.items():
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)
        trained_models[model_name] = model

    return trained_models


def evaluate_models(models, X_test, y_test):
    """Evaluate trained models using classification metrics."""

    results = []

    for model_name, model in models.items():
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred)

        results.append({
            "model": model_name,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "true_negative": int(cm[0][0]),
            "false_positive": int(cm[0][1]),
            "false_negative": int(cm[1][0]),
            "true_positive": int(cm[1][1]),
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="f1_score", ascending=False)

    return results_df


def save_model_results(results_df):
    """Save model comparison results."""
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / "model_comparison_results.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)

    print(f"Model comparison results saved to: {output_path}")


def select_best_model(models, results_df):
    """Select the best model based on F1 score."""

    best_model_name = results_df.iloc[0]["model"]
    best_model = models[best_model_name]

    return best_model_name, best_model


def save_best_model(best_model, best_model_name):
    """Save the best trained model."""
    project_root = Path(__file__).resolve().parents[1]
    models_path = project_root / "models"
    models_path.mkdir(parents=True, exist_ok=True)

    model_path = models_path / "security_model.joblib"

    joblib.dump(best_model, model_path)

    print(f"Best model: {best_model_name}")
    print(f"Saved best model to: {model_path}")


def main():
    print("Starting machine-learning model training...")
    print("=" * 50)

    X_train, X_test, y_train, y_test, encoder = prepare_ml_data()

    models = train_models(X_train, y_train)
    results_df = evaluate_models(models, X_test, y_test)

    print()
    print("Model comparison results:")
    print(results_df)

    save_model_results(results_df)

    best_model_name, best_model = select_best_model(models, results_df)
    save_best_model(best_model, best_model_name)

    print()
    print("Machine-learning training complete.")


if __name__ == "__main__":
    main()