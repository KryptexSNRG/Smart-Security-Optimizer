from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


NUMERIC_FEATURES = [
    "login_hour",
    "failed_attempts",
    "mfa_failed_attempts",
]

BOOLEAN_FEATURES = [
    "mfa_used",
    "new_device",
    "foreign_login",
    "unusual_hour",
    "impossible_travel",
    "suspicious_ip",
    "login_success",
]

CATEGORICAL_FEATURES = [
    "device_type",
    "browser",
    "country",
    "mfa_type",
]

TARGET = "is_suspicious"


def load_scored_data():
    """Load the scored login dataset."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "data" / "processed" / "login_events_scored.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Scored dataset not found at: {input_path}")

    return pd.read_csv(input_path)


def select_features_and_target(df):
    """Separate selected ML features from the target variable."""

    selected_columns = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES

    missing_columns = [col for col in selected_columns + [TARGET] if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    X = df[selected_columns].copy()
    y = df[TARGET].copy()

    return X, y


def clean_feature_values(X):
    """Prepare feature values before encoding."""

    for col in NUMERIC_FEATURES:
        X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    for col in BOOLEAN_FEATURES:
        X[col] = X[col].astype(bool).astype(int)

    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].fillna("Unknown").astype(str)

    return X


def encode_categorical_features(X):
    """One-hot encode categorical features and combine them with numeric/Boolean features."""

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    encoded_array = encoder.fit_transform(X[CATEGORICAL_FEATURES])
    encoded_columns = encoder.get_feature_names_out(CATEGORICAL_FEATURES)

    encoded_df = pd.DataFrame(
        encoded_array,
        columns=encoded_columns,
        index=X.index
    )

    non_categorical_df = X[NUMERIC_FEATURES + BOOLEAN_FEATURES]

    X_encoded = pd.concat([non_categorical_df, encoded_df], axis=1)

    return X_encoded, encoder


def create_train_test_split(X, y, test_size=0.2, random_state=42):
    """Create training and testing datasets."""

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )


def prepare_ml_data():
    """Run the full feature engineering pipeline."""

    df = load_scored_data()

    X, y = select_features_and_target(df)
    X = clean_feature_values(X)
    X_encoded, encoder = encode_categorical_features(X)

    X_train, X_test, y_train, y_test = create_train_test_split(X_encoded, y)

    print("Feature engineering complete.")
    print(f"Total rows: {len(df)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")
    print(f"Number of features after encoding: {X_encoded.shape[1]}")
    print()
    print("Target distribution:")
    print(y.value_counts())

    return X_train, X_test, y_train, y_test, encoder


if __name__ == "__main__":
    prepare_ml_data()