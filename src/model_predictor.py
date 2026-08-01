from pathlib import Path

import joblib
import pandas as pd

from src.feature_engineering import (
    NUMERIC_FEATURES,
    BOOLEAN_FEATURES,
    CATEGORICAL_FEATURES,
    clean_feature_values,
)


def load_model_assets():
    """Load saved model, encoder, and metadata."""

    project_root = Path(__file__).resolve().parents[1]
    models_path = project_root / "models"

    model_path = models_path / "security_model.joblib"
    encoder_path = models_path / "onehot_encoder.joblib"
    metadata_path = models_path / "model_metadata.joblib"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at: {model_path}")

    if not encoder_path.exists():
        raise FileNotFoundError(f"Encoder not found at: {encoder_path}")

    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)

    metadata = {}
    if metadata_path.exists():
        metadata = joblib.load(metadata_path)

    return model, encoder, metadata


def prepare_single_login(login_event, encoder):
    """Prepare one login event for model prediction."""

    selected_columns = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES

    df = pd.DataFrame([login_event])

    missing_columns = [col for col in selected_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    X = df[selected_columns].copy()
    X = clean_feature_values(X)

    encoded_array = encoder.transform(X[CATEGORICAL_FEATURES])
    encoded_columns = encoder.get_feature_names_out(CATEGORICAL_FEATURES)

    encoded_df = pd.DataFrame(encoded_array, columns=encoded_columns, index=X.index)
    non_categorical_df = X[NUMERIC_FEATURES + BOOLEAN_FEATURES]

    X_encoded = pd.concat([non_categorical_df, encoded_df], axis=1)

    return X_encoded


def predict_login(login_event):
    """Predict whether a single login event is suspicious."""

    model, encoder, metadata = load_model_assets()

    X_encoded = prepare_single_login(login_event, encoder)

    prediction = model.predict(X_encoded)[0]

    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(X_encoded)[0][1]
    else:
        probability = None

    return {
        "prediction": int(prediction),
        "prediction_label": "Suspicious" if prediction == 1 else "Normal",
        "suspicious_probability": round(float(probability), 4) if probability is not None else None,
        "model_used": metadata.get("best_model_name", "Unknown"),
    }


def main():
    """Example prediction."""

    example_login = {
        "login_hour": 2,
        "failed_attempts": 5,
        "mfa_failed_attempts": 0,
        "mfa_used": False,
        "new_device": True,
        "foreign_login": True,
        "unusual_hour": True,
        "impossible_travel": False,
        "suspicious_ip": True,
        "login_success": True,
        "device_type": "Laptop",
        "browser": "Chrome",
        "country": "Germany",
        "mfa_type": "None",
    }

    result = predict_login(example_login)

    print("Prediction result:")
    print(result)


if __name__ == "__main__":
    main()