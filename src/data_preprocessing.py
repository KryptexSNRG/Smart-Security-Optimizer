from pathlib import Path

import pandas as pd


def load_raw_data():
    """Load the raw login dataset."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "data" / "raw" / "login_events.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {input_path}")

    return pd.read_csv(input_path)


def remove_duplicates(df):
    """Remove duplicate rows and duplicate login IDs."""
    df = df.drop_duplicates()

    if "login_id" in df.columns:
        df = df.drop_duplicates(subset=["login_id"])

    return df


def clean_timestamps(df):
    """Convert timestamp column to datetime and recreate time-based fields."""
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df["login_hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

    return df


def handle_missing_values(df):
    """Handle missing values in the dataset."""

    categorical_columns = [
        "country",
        "city",
        "usual_country",
        "usual_city",
        "device_type",
        "browser",
        "ip_address",
        "mfa_type",
        "attack_type",
    ]

    boolean_columns = [
        "mfa_used",
        "new_device",
        "foreign_login",
        "unusual_hour",
        "impossible_travel",
        "suspicious_ip",
        "login_success",
    ]

    numeric_columns = [
        "login_hour",
        "failed_attempts",
        "mfa_failed_attempts",
        "is_suspicious",
    ]

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].fillna(False)

    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    return df


def fix_data_types(df):
    """Convert columns to correct data types."""

    boolean_columns = [
        "mfa_used",
        "new_device",
        "foreign_login",
        "unusual_hour",
        "impossible_travel",
        "suspicious_ip",
        "login_success",
    ]

    integer_columns = [
        "login_hour",
        "failed_attempts",
        "mfa_failed_attempts",
        "is_suspicious",
    ]

    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    for col in integer_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)

    return df


def validate_ranges(df):
    """Fix values that fall outside expected ranges."""

    if "login_hour" in df.columns:
        df = df[df["login_hour"].between(0, 23)]

    if "failed_attempts" in df.columns:
        df["failed_attempts"] = df["failed_attempts"].clip(lower=0, upper=20)

    if "mfa_failed_attempts" in df.columns:
        df["mfa_failed_attempts"] = df["mfa_failed_attempts"].clip(lower=0, upper=20)

    if "is_suspicious" in df.columns:
        df["is_suspicious"] = df["is_suspicious"].apply(lambda x: 1 if x == 1 else 0)

    return df


def create_security_features(df):
    """Create extra features that will help the risk engine and ML model."""

    df["no_mfa"] = ~df["mfa_used"]

    df["multiple_failed_attempts"] = df["failed_attempts"] >= 3

    df["high_failed_attempts"] = df["failed_attempts"] >= 5

    df["risky_new_device_no_mfa"] = df["new_device"] & df["no_mfa"]

    df["risky_foreign_no_mfa"] = df["foreign_login"] & df["no_mfa"]

    df["risky_unusual_hour"] = df["unusual_hour"] & (
        df["new_device"] | df["foreign_login"] | df["no_mfa"]
    )

    df["mfa_fatigue_risk"] = df["mfa_failed_attempts"] >= 3

    return df


def save_clean_data(df):
    """Save the cleaned dataset to data/processed."""
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / "login_events_clean.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Cleaned dataset saved to: {output_path}")
    print(f"Final row count: {len(df)}")


def preprocess_data():
    """Run the full preprocessing pipeline."""
    df = load_raw_data()

    print("Starting preprocessing...")
    print(f"Original row count: {len(df)}")

    df = remove_duplicates(df)
    df = clean_timestamps(df)
    df = handle_missing_values(df)
    df = fix_data_types(df)
    df = validate_ranges(df)
    df = create_security_features(df)

    save_clean_data(df)

    print("Preprocessing complete.")

    return df


if __name__ == "__main__":
    preprocess_data()