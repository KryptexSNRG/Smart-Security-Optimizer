from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_data():
    """Load the generated login dataset."""
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "raw" / "login_events.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {data_path}")

    return pd.read_csv(data_path)


def validate_row_count(df):
    """Check the number of rows."""
    print("ROW COUNT CHECK")
    print(f"Total rows: {len(df)}")

    if len(df) == 10000:
        print("PASS: Dataset has 10,000 rows.")
    else:
        print("WARNING: Dataset does not have 10,000 rows.")

    print()


def validate_missing_values(df):
    """Check for missing values."""
    print("MISSING VALUES CHECK")
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]

    if missing_values.empty:
        print("PASS: No missing values found.")
    else:
        print("WARNING: Missing values found:")
        print(missing_values)

    print()


def validate_duplicates(df):
    """Check for duplicate rows and duplicate login IDs."""
    print("DUPLICATE CHECK")

    duplicate_rows = df.duplicated().sum()
    duplicate_login_ids = df["login_id"].duplicated().sum()

    print(f"Duplicate rows: {duplicate_rows}")
    print(f"Duplicate login IDs: {duplicate_login_ids}")

    if duplicate_rows == 0 and duplicate_login_ids == 0:
        print("PASS: No duplicate rows or duplicate login IDs found.")
    else:
        print("WARNING: Duplicates found.")

    print()


def validate_field_ranges(df):
    """Check whether important numeric and Boolean fields have valid values."""
    print("FIELD RANGE CHECK")

    checks = {
        "login_hour_valid": df["login_hour"].between(0, 23).all(),
        "failed_attempts_valid": df["failed_attempts"].between(0, 20).all(),
        "mfa_failed_attempts_valid": df["mfa_failed_attempts"].between(0, 20).all(),
        "is_suspicious_valid": df["is_suspicious"].isin([0, 1]).all(),
    }

    for check_name, passed in checks.items():
        if passed:
            print(f"PASS: {check_name}")
        else:
            print(f"WARNING: {check_name} failed")

    print()


def validate_class_distribution(df):
    """Check normal vs suspicious distribution and attack type counts."""
    print("CLASS DISTRIBUTION CHECK")

    suspicious_counts = df["is_suspicious"].value_counts()
    attack_counts = df["attack_type"].value_counts()

    print("Normal vs Suspicious:")
    print(suspicious_counts)
    print()

    print("Attack Type Distribution:")
    print(attack_counts)
    print()

    suspicious_rate = df["is_suspicious"].mean() * 100
    print(f"Suspicious login percentage: {suspicious_rate:.2f}%")
    print()


def create_charts(df):
    """Create basic charts for data validation."""
    project_root = Path(__file__).resolve().parents[1]
    images_path = project_root / "images"
    images_path.mkdir(parents=True, exist_ok=True)

    # Chart 1: Normal vs suspicious logins
    suspicious_counts = df["is_suspicious"].value_counts().sort_index()
    suspicious_counts.index = ["Normal", "Suspicious"]

    plt.figure()
    suspicious_counts.plot(kind="bar")
    plt.title("Normal vs Suspicious Logins")
    plt.xlabel("Login Type")
    plt.ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(images_path / "normal_vs_suspicious.png")
    plt.close()

    # Chart 2: Attack type distribution
    attack_counts = df["attack_type"].value_counts()

    plt.figure()
    attack_counts.plot(kind="bar")
    plt.title("Attack Type Distribution")
    plt.xlabel("Attack Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(images_path / "attack_type_distribution.png")
    plt.close()

    # Chart 3: Failed attempts distribution
    failed_attempts_counts = df["failed_attempts"].value_counts().sort_index()

    plt.figure()
    failed_attempts_counts.plot(kind="bar")
    plt.title("Failed Attempts Distribution")
    plt.xlabel("Failed Attempts")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(images_path / "failed_attempts_distribution.png")
    plt.close()

    # Chart 4: Login hour distribution
    login_hour_counts = df["login_hour"].value_counts().sort_index()

    plt.figure()
    login_hour_counts.plot(kind="bar")
    plt.title("Login Hour Distribution")
    plt.xlabel("Login Hour")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(images_path / "login_hour_distribution.png")
    plt.close()

    print("Charts saved to images folder:")
    print("- images/normal_vs_suspicious.png")
    print("- images/attack_type_distribution.png")
    print("- images/failed_attempts_distribution.png")
    print("- images/login_hour_distribution.png")
    print()


def main():
    df = load_data()

    print("SMART SECURITY OPTIMIZER DATA VALIDATION")
    print("=" * 50)
    print()

    validate_row_count(df)
    validate_missing_values(df)
    validate_duplicates(df)
    validate_field_ranges(df)
    validate_class_distribution(df)
    create_charts(df)

    print("Data validation complete.")


if __name__ == "__main__":
    main()