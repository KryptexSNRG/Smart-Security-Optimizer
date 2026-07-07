from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def load_scored_data():
    """Load the scored login dataset."""
    project_root = Path(__file__).resolve().parents[1]
    input_path = project_root / "data" / "processed" / "login_events_scored.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Scored dataset not found at: {input_path}")

    return pd.read_csv(input_path)


def analyze_score_distribution(df):
    """Analyze overall risk score distribution."""
    print("RISK SCORE DISTRIBUTION")
    print("=" * 40)

    print(f"Minimum risk score: {df['risk_score'].min()}")
    print(f"Maximum risk score: {df['risk_score'].max()}")
    print(f"Average risk score: {round(df['risk_score'].mean(), 2)}")
    print(f"Median risk score: {round(df['risk_score'].median(), 2)}")

    print()
    print("Risk level counts:")
    print(df["risk_level"].value_counts())

    print()


def analyze_attack_type_averages(df):
    """Analyze average risk score by attack type."""
    print("AVERAGE RISK SCORE BY ATTACK TYPE")
    print("=" * 40)

    attack_summary = (
        df.groupby("attack_type")
        .agg(
            count=("login_id", "count"),
            avg_risk_score=("risk_score", "mean"),
            min_risk_score=("risk_score", "min"),
            max_risk_score=("risk_score", "max"),
        )
        .sort_values(by="avg_risk_score", ascending=False)
    )

    attack_summary["avg_risk_score"] = attack_summary["avg_risk_score"].round(2)

    print(attack_summary)
    print()

    return attack_summary


def analyze_common_risk_factors(df):
    """Analyze how often each risk factor appears."""
    print("COMMON RISK FACTORS")
    print("=" * 40)

    risk_factors = {
        "new_device": "New device",
        "foreign_login": "Foreign login",
        "unusual_hour": "Unusual hour",
        "impossible_travel": "Impossible travel",
        "suspicious_ip": "Suspicious IP",
        "login_success": "Login success",
    }

    factor_counts = {}

    for column, label in risk_factors.items():
        if column in df.columns:
            factor_counts[label] = df[column].sum()

    factor_counts["Failed attempts >= 3"] = (df["failed_attempts"] >= 3).sum()
    factor_counts["Failed attempts >= 5"] = (df["failed_attempts"] >= 5).sum()
    factor_counts["No MFA"] = (~df["mfa_used"]).sum()

    if "mfa_failed_attempts" in df.columns:
        factor_counts["MFA failed attempts >= 3"] = (df["mfa_failed_attempts"] >= 3).sum()

    factor_df = pd.DataFrame(
        list(factor_counts.items()),
        columns=["risk_factor", "count"]
    ).sort_values(by="count", ascending=False)

    print(factor_df)
    print()

    return factor_df


def identify_weak_rules(df):
    """
    Identify suspicious attack types that may be scored too low.
    """

    print("POTENTIAL WEAK SCORING RULES")
    print("=" * 40)

    suspicious_df = df[df["is_suspicious"] == 1]

    low_scored_suspicious = suspicious_df[suspicious_df["risk_score"] < 30]

    if low_scored_suspicious.empty:
        print("PASS: No suspicious logins are scored as Low risk.")
    else:
        print("WARNING: Some suspicious logins are being scored as Low risk.")
        print()
        print("Low-scored suspicious logins by attack type:")
        print(low_scored_suspicious["attack_type"].value_counts())

    print()

    attack_level_table = pd.crosstab(df["attack_type"], df["risk_level"])
    print("Attack type vs risk level:")
    print(attack_level_table)
    print()

    return low_scored_suspicious, attack_level_table


def create_risk_analysis_charts(df, attack_summary, factor_df):
    """Create charts for risk analysis."""
    project_root = Path(__file__).resolve().parents[1]
    images_path = project_root / "images"
    images_path.mkdir(parents=True, exist_ok=True)

    # Chart 1: Risk level distribution
    risk_level_counts = df["risk_level"].value_counts()

    plt.figure()
    risk_level_counts.plot(kind="bar")
    plt.title("Risk Level Distribution")
    plt.xlabel("Risk Level")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(images_path / "risk_level_distribution.png")
    plt.close()

    # Chart 2: Average risk score by attack type
    plt.figure()
    attack_summary["avg_risk_score"].sort_values().plot(kind="barh")
    plt.title("Average Risk Score by Attack Type")
    plt.xlabel("Average Risk Score")
    plt.ylabel("Attack Type")
    plt.tight_layout()
    plt.savefig(images_path / "average_risk_by_attack_type.png")
    plt.close()

    # Chart 3: Common risk factors
    plt.figure()
    factor_df.sort_values(by="count").plot(
        x="risk_factor",
        y="count",
        kind="barh",
        legend=False
    )
    plt.title("Common Risk Factors")
    plt.xlabel("Count")
    plt.ylabel("Risk Factor")
    plt.tight_layout()
    plt.savefig(images_path / "common_risk_factors.png")
    plt.close()

    # Chart 4: Risk score histogram
    plt.figure()
    df["risk_score"].plot(kind="hist", bins=20)
    plt.title("Risk Score Distribution")
    plt.xlabel("Risk Score")
    plt.ylabel("Number of Logins")
    plt.tight_layout()
    plt.savefig(images_path / "risk_score_histogram.png")
    plt.close()

    print("Charts saved:")
    print("- images/risk_level_distribution.png")
    print("- images/average_risk_by_attack_type.png")
    print("- images/common_risk_factors.png")
    print("- images/risk_score_histogram.png")
    print()


def save_analysis_outputs(attack_summary, factor_df, low_scored_suspicious, attack_level_table):
    """Save analysis tables to CSV files."""
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed"
    output_path.mkdir(parents=True, exist_ok=True)

    attack_summary.to_csv(output_path / "attack_type_risk_summary.csv")
    factor_df.to_csv(output_path / "common_risk_factors.csv", index=False)
    low_scored_suspicious.to_csv(output_path / "low_scored_suspicious_logins.csv", index=False)
    attack_level_table.to_csv(output_path / "attack_type_risk_level_table.csv")

    print("Analysis CSV files saved:")
    print("- data/processed/attack_type_risk_summary.csv")
    print("- data/processed/common_risk_factors.csv")
    print("- data/processed/low_scored_suspicious_logins.csv")
    print("- data/processed/attack_type_risk_level_table.csv")
    print()


def main():
    print("SMART SECURITY OPTIMIZER RISK ANALYSIS")
    print("=" * 50)
    print()

    df = load_scored_data()

    analyze_score_distribution(df)
    attack_summary = analyze_attack_type_averages(df)
    factor_df = analyze_common_risk_factors(df)
    low_scored_suspicious, attack_level_table = identify_weak_rules(df)

    create_risk_analysis_charts(df, attack_summary, factor_df)
    save_analysis_outputs(
        attack_summary,
        factor_df,
        low_scored_suspicious,
        attack_level_table
    )

    print("Risk analysis complete.")


if __name__ == "__main__":
    main()