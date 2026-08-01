from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from src.feature_engineering import prepare_ml_data


def check_class_imbalance(y_train, y_test):
    """Check class imbalance in training and testing data."""

    print("CLASS IMBALANCE CHECK")
    print("=" * 40)

    train_counts = y_train.value_counts().sort_index()
    test_counts = y_test.value_counts().sort_index()

    print("Training target distribution:")
    print(train_counts)
    print()

    print("Testing target distribution:")
    print(test_counts)
    print()

    imbalance_df = pd.DataFrame({
        "dataset": ["train_normal", "train_suspicious", "test_normal", "test_suspicious"],
        "count": [
            train_counts.get(0, 0),
            train_counts.get(1, 0),
            test_counts.get(0, 0),
            test_counts.get(1, 0),
        ],
    })

    return imbalance_df


def train_models(X_train, y_train):
    """Train baseline and balanced machine-learning models."""

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Logistic Regression Balanced": LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight="balanced"
        ),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Decision Tree Balanced": DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=42
        ),
        "Random Forest Balanced": RandomForestClassifier(
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
    """Evaluate models using accuracy, precision, recall, F1, and confusion matrix."""

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
    results_df = results_df.sort_values(
        by=["f1_score", "recall", "precision"],
        ascending=False
    )

    return results_df


def save_confusion_matrices(models, X_test, y_test):
    """Save confusion matrices for every model."""

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / "confusion_matrices.csv"

    rows = []

    for model_name, model in models.items():
        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)

        rows.append({
            "model": model_name,
            "true_negative": int(cm[0][0]),
            "false_positive": int(cm[0][1]),
            "false_negative": int(cm[1][0]),
            "true_positive": int(cm[1][1]),
        })

    confusion_df = pd.DataFrame(rows)
    confusion_df.to_csv(output_path, index=False)

    print(f"Confusion matrices saved to: {output_path}")

    return confusion_df


def get_feature_importance(best_model, feature_names, best_model_name):
    """Extract feature importance or coefficients from the best model."""

    if hasattr(best_model, "feature_importances_"):
        importance_values = best_model.feature_importances_
        importance_type = "feature_importance"

    elif hasattr(best_model, "coef_"):
        importance_values = abs(best_model.coef_[0])
        importance_type = "absolute_coefficient"

    else:
        return pd.DataFrame(columns=["feature", "importance", "importance_type"])

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importance_values,
    })

    importance_df["importance_type"] = importance_type
    importance_df["model"] = best_model_name

    importance_df = importance_df.sort_values(by="importance", ascending=False)

    return importance_df


def save_feature_importance(importance_df):
    """Save feature importance results."""

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / "feature_importance.csv"

    importance_df.to_csv(output_path, index=False)

    print(f"Feature importance saved to: {output_path}")


def create_feature_importance_chart(importance_df):
    """Create a chart of the top 15 features."""

    if importance_df.empty:
        return

    project_root = Path(__file__).resolve().parents[1]
    images_path = project_root / "images"
    images_path.mkdir(parents=True, exist_ok=True)

    top_features = importance_df.head(15).sort_values(by="importance")

    plt.figure()
    plt.barh(top_features["feature"], top_features["importance"])
    plt.title("Top ML Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.savefig(images_path / "ml_feature_importance.png")
    plt.close()

    print("Feature importance chart saved to: images/ml_feature_importance.png")


def save_model_results(results_df, imbalance_df):
    """Save model comparison and class imbalance results."""

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed"
    output_path.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(output_path / "model_comparison_results.csv", index=False)
    imbalance_df.to_csv(output_path / "class_imbalance_summary.csv", index=False)

    print(f"Model comparison results saved to: {output_path / 'model_comparison_results.csv'}")
    print(f"Class imbalance summary saved to: {output_path / 'class_imbalance_summary.csv'}")


def select_best_model(models, results_df):
    """
    Select best model.

    F1 score is the main metric.
    Recall is the secondary metric because missing suspicious logins is risky.
    """

    best_model_name = results_df.iloc[0]["model"]
    best_model = models[best_model_name]

    return best_model_name, best_model


def save_best_model(best_model, best_model_name, encoder):
    """Save the best model and encoder."""

    project_root = Path(__file__).resolve().parents[1]
    models_path = project_root / "models"
    models_path.mkdir(parents=True, exist_ok=True)

    model_path = models_path / "security_model.joblib"
    encoder_path = models_path / "onehot_encoder.joblib"
    metadata_path = models_path / "model_metadata.joblib"

    joblib.dump(best_model, model_path)
    joblib.dump(encoder, encoder_path)

    metadata = {
        "best_model_name": best_model_name,
        "model_path": str(model_path),
        "encoder_path": str(encoder_path),
    }

    joblib.dump(metadata, metadata_path)

    print(f"Best model: {best_model_name}")
    print(f"Saved best model to: {model_path}")
    print(f"Saved encoder to: {encoder_path}")
    print(f"Saved model metadata to: {metadata_path}")


def main():
    print("Starting machine-learning model training...")
    print("=" * 50)

    X_train, X_test, y_train, y_test, encoder = prepare_ml_data()

    imbalance_df = check_class_imbalance(y_train, y_test)

    models = train_models(X_train, y_train)

    results_df = evaluate_models(models, X_test, y_test)

    print()
    print("MODEL COMPARISON RESULTS")
    print("=" * 40)
    print(results_df)

    confusion_df = save_confusion_matrices(models, X_test, y_test)

    best_model_name, best_model = select_best_model(models, results_df)

    feature_names = X_train.columns
    importance_df = get_feature_importance(best_model, feature_names, best_model_name)

    save_model_results(results_df, imbalance_df)
    save_feature_importance(importance_df)
    create_feature_importance_chart(importance_df)
    save_best_model(best_model, best_model_name, encoder)

    print()
    print("Best model selected:")
    print(best_model_name)

    print()
    print("Top 10 important features:")
    print(importance_df.head(10))

    print()
    print("Machine-learning training complete.")


if __name__ == "__main__":
    main()