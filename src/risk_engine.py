from pathlib import Path

import pandas as pd


def calculate_risk_score(login_event):
    """
    Calculate a point-based risk score for one login event.

    Returns:
        dict containing risk_score, risk_level, recommended_action, and risk_reasons
    """

    score = 0
    reasons = []

    new_device = login_event.get("new_device", False)
    foreign_login = login_event.get("foreign_login", False)
    unusual_hour = login_event.get("unusual_hour", False)
    mfa_used = login_event.get("mfa_used", False)
    impossible_travel = login_event.get("impossible_travel", False)
    suspicious_ip = login_event.get("suspicious_ip", False)
    login_success = login_event.get("login_success", False)

    failed_attempts = login_event.get("failed_attempts", 0)
    mfa_failed_attempts = login_event.get("mfa_failed_attempts", 0)

    # New device risk
    if new_device:
        score += 30
        reasons.append("Login came from a new device")

    # Foreign login risk
    if foreign_login:
        score += 30
        reasons.append("Login came from a foreign or unusual country")

    # Unusual login hour risk
    if unusual_hour:
        score += 30
        reasons.append("Login occurred during an unusual hour")

    # Failed attempts risk
    if failed_attempts >= 5:
        score += 40
        reasons.append("Login had 5 or more failed attempts")
    elif failed_attempts >= 3:
        score += 30
        reasons.append("Login had multiple failed attempts")

    # MFA not used risk
    if not mfa_used:
        score += 30
        reasons.append("Multi-factor authentication was not used")

    # Impossible travel risk
    if impossible_travel:
        score += 45
        reasons.append("Login was flagged for impossible travel")

    # Suspicious IP risk
    if suspicious_ip:
        score += 40
        reasons.append("Login came from a suspicious IP address")

    # MFA fatigue risk
    if mfa_failed_attempts >= 3:
        score += 40
        reasons.append("Login had repeated MFA failures")

    # Successful login after many failed attempts
    if failed_attempts >= 5 and login_success:
        score += 20
        reasons.append("Login succeeded after many failed attempts")

    # Combination rule: new device without MFA
    if new_device and not mfa_used:
        score += 15
        reasons.append("New device login did not use MFA")

    # Combination rule: foreign login without MFA
    if foreign_login and not mfa_used:
        score += 15
        reasons.append("Foreign login did not use MFA")

    # Combination rule: unusual hour without MFA
    if unusual_hour and not mfa_used:
        score += 15
        reasons.append("Unusual-hour login did not use MFA")

    # Combination rule: suspicious IP with failed attempts
    if suspicious_ip and failed_attempts >= 3:
        score += 15
        reasons.append("Suspicious IP had multiple failed attempts")

    # Cap score at 100
    final_score = min(score, 100)

    risk_level = get_risk_level(final_score)
    recommended_action = get_recommended_action(risk_level)

    if not reasons:
        reasons.append("No major suspicious risk factors were detected")

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "risk_reasons": "; ".join(reasons),
    }

def get_risk_level(score):
    """
    Convert numeric score into Low, Medium, High, or Critical.
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
    Recommend an action based on the risk level.
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
    Apply risk scoring to every login event in the dataset.
    """

    risk_results = df.apply(calculate_risk_score, axis=1)

    df["risk_score"] = risk_results.apply(lambda result: result["risk_score"])
    df["risk_level"] = risk_results.apply(lambda result: result["risk_level"])
    df["recommended_action"] = risk_results.apply(lambda result: result["recommended_action"])
    df["risk_reasons"] = risk_results.apply(lambda result: result["risk_reasons"])

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
    Save the scored dataset.
    """

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / "login_events_scored.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)
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
    print("Sample scored records:")
    print(
        df[
            [
                "login_id",
                "risk_score",
                "risk_level",
                "recommended_action",
                "risk_reasons",
            ]
        ].head()
    )

    print()
    print("Risk scoring complete.")


if __name__ == "__main__":
    main()