from pathlib import Path

import pandas as pd


def calculate_risk_score(login_event):
    """
    Calculate a point-based risk score for a single login event.

    Args:
        login_event: A dictionary or pandas Series representing one login event.

    Returns:
        int: Risk score from 0 to 100.
    """

    score = 0

    # New device risk
    if login_event.get("new_device", False):
        score += 15

    # Foreign login risk
    if login_event.get("foreign_login", False):
        score += 20

    # Unusual login hour risk
    if login_event.get("unusual_hour", False):
        score += 10

    # Failed attempts risk
    failed_attempts = login_event.get("failed_attempts", 0)

    if failed_attempts >= 5:
        score += 35
    elif failed_attempts >= 3:
        score += 20

    # MFA not used risk
    if not login_event.get("mfa_used", False):
        score += 10

    # Impossible travel risk
    if login_event.get("impossible_travel", False):
        score += 30

    # Suspicious IP risk
    if login_event.get("suspicious_ip", False):
        score += 25

    # MFA fatigue risk
    mfa_failed_attempts = login_event.get("mfa_failed_attempts", 0)

    if mfa_failed_attempts >= 3:
        score += 25

    # Login success after many failed attempts
    if failed_attempts >= 5 and login_event.get("login_success", False):
        score += 15

    # Cap score at 100
    return min(score, 100)


def get_risk_level(score):
    """
    Convert a numeric risk score into a risk level.
    """

    if score < 30:
        return "Low"
    elif score < 60:
        return "Medium"
    elif score < 80:
        return "High"
    else:
        return "Critical"


def get_recommended_action(risk_level):
    """
    Recommend an authentication action based on risk level.
    """

    if risk_level == "Low":
        return "Allow login"
    elif risk_level == "Medium":
        return "Require MFA"
    elif risk_level == "High":
        return "Require stronger MFA"
    else:
        return "Block login or require additional identity verification"


def apply_risk_scoring(df):
    """
    Apply risk scoring to every row in the dataset.
    """

    df["risk_score"] = df.apply(calculate_risk_score, axis=1)
    df["risk_level"] = df["risk_score"].apply(get_risk_level)
    df["recommended_action"] = df["risk_level"].apply(get_recommended_action)

    return df


def load_clean_data():
    """
    Load the cleaned login dataset.
    """

    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "data" / "processed" / "login_events_clean.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at: {input_path}")

    return pd.read_csv(input_path)


def save_scored_data(df):
    """
    Save the dataset with risk scores.
    """

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / "login_events_scored.csv"

    df.to_csv(output_path, index=False)

    print(f"Scored dataset saved to: {output_path}")
    print(f"Total rows scored: {len(df)}")


def main():
    """
    Run the full risk scoring process.
    """

    print("Starting risk scoring...")

    df = load_clean_data()
    df = apply_risk_scoring(df)
    save_scored_data(df)

    print()
    print("Risk level distribution:")
    print(df["risk_level"].value_counts())

    print()
    print("Average risk score:")
    print(round(df["risk_score"].mean(), 2))

    print()
    print("Risk scoring complete.")


if __name__ == "__main__":
    main()