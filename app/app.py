from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

from src.auth_optimizer import (
    DEFAULT_WEIGHTS,
    compare_all_strategies,
    optimize_authentication_strategy,
)
from src.model_predictor import predict_login
from src.risk_engine import calculate_risk_score


st.set_page_config(
    page_title="Smart Security Optimizer",
    page_icon="🔐",
    layout="wide",
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCORED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "login_events_scored.csv"
MODEL_RESULTS_PATH = PROJECT_ROOT / "data" / "processed" / "model_comparison_results.csv"
FEATURE_IMPORTANCE_PATH = PROJECT_ROOT / "data" / "processed" / "feature_importance.csv"


@st.cache_data
def load_scored_data():
    if not SCORED_DATA_PATH.exists():
        st.error("Scored dataset not found. Run the backend pipeline first.")
        st.stop()

    df = pd.read_csv(SCORED_DATA_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


@st.cache_data
def load_model_results():
    if MODEL_RESULTS_PATH.exists():
        return pd.read_csv(MODEL_RESULTS_PATH)
    return pd.DataFrame()


@st.cache_data
def load_feature_importance():
    if FEATURE_IMPORTANCE_PATH.exists():
        return pd.read_csv(FEATURE_IMPORTANCE_PATH)
    return pd.DataFrame()


def apply_filters(df):
    st.sidebar.header("Filters")

    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    countries = sorted(df["country"].dropna().unique())
    selected_countries = st.sidebar.multiselect(
        "Country",
        countries,
        default=countries,
    )

    devices = sorted(df["device_type"].dropna().unique())
    selected_devices = st.sidebar.multiselect(
        "Device",
        devices,
        default=devices,
    )

    risk_levels = ["Low", "Medium", "High", "Critical"]
    selected_risks = st.sidebar.multiselect(
        "Risk Level",
        risk_levels,
        default=risk_levels,
    )

    attack_types = sorted(df["attack_type"].dropna().unique())
    selected_attacks = st.sidebar.multiselect(
        "Attack Type",
        attack_types,
        default=attack_types,
    )

    mfa_options = sorted(df["mfa_used"].dropna().unique())
    selected_mfa = st.sidebar.multiselect(
        "MFA Used",
        mfa_options,
        default=mfa_options,
    )

    filtered_df = df.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["timestamp"].dt.date >= start_date)
            & (filtered_df["timestamp"].dt.date <= end_date)
        ]

    filtered_df = filtered_df[
        filtered_df["country"].isin(selected_countries)
        & filtered_df["device_type"].isin(selected_devices)
        & filtered_df["risk_level"].isin(selected_risks)
        & filtered_df["attack_type"].isin(selected_attacks)
        & filtered_df["mfa_used"].isin(selected_mfa)
    ]

    return filtered_df


def show_overview_page(df):
    st.title("🔐 Smart Security Optimizer")
    st.subheader("Overview")

    total_logins = len(df)
    suspicious_events = int(df["is_suspicious"].sum())
    critical_risk = int((df["risk_level"] == "Critical").sum())
    average_risk = round(df["risk_score"].mean(), 2)
    mfa_rate = round(df["mfa_used"].mean() * 100, 2)

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Logins", f"{total_logins:,}")
    col2.metric("Suspicious Events", f"{suspicious_events:,}")
    col3.metric("Critical Risk", f"{critical_risk:,}")
    col4.metric("Average Risk", average_risk)
    col5.metric("MFA Usage", f"{mfa_rate}%")

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        risk_counts = df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["risk_level", "count"]

        fig = px.bar(
            risk_counts,
            x="risk_level",
            y="count",
            title="Risk Level Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        attack_counts = df["attack_type"].value_counts().reset_index()
        attack_counts.columns = ["attack_type", "count"]

        fig = px.bar(
            attack_counts,
            x="attack_type",
            y="count",
            title="Attack Type Distribution",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


def show_login_analysis_page(df):
    st.title("📊 Login Analysis")

    st.subheader("Activity Timeline")
    timeline_df = (
        df.groupby(df["timestamp"].dt.date)
        .size()
        .reset_index(name="login_count")
    )
    timeline_df.columns = ["date", "login_count"]

    fig = px.line(
        timeline_df,
        x="date",
        y="login_count",
        title="Login Activity Timeline",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        country_df = df["country"].value_counts().reset_index()
        country_df.columns = ["country", "count"]

        fig = px.bar(
            country_df,
            x="country",
            y="count",
            title="Logins by Country",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        failed_df = df["failed_attempts"].value_counts().sort_index().reset_index()
        failed_df.columns = ["failed_attempts", "count"]

        fig = px.bar(
            failed_df,
            x="failed_attempts",
            y="count",
            title="Failed Attempts Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Filtered Login Records")
    st.dataframe(df.head(500), use_container_width=True)


def show_risk_predictor_page(df):
    st.title("🧠 Individual Login Risk Predictor")

    st.write(
        "Enter a login scenario below. The system will calculate a rule-based risk score "
        "and generate an ML suspicious-login prediction."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        login_hour = st.slider("Login Hour", 0, 23, 2)
        failed_attempts = st.slider("Failed Attempts", 0, 10, 3)
        mfa_failed_attempts = st.slider("MFA Failed Attempts", 0, 10, 0)
        mfa_used = st.selectbox("MFA Used", [True, False])

    with col2:
        new_device = st.selectbox("New Device", [False, True])
        foreign_login = st.selectbox("Foreign Login", [False, True])
        unusual_hour = st.selectbox("Unusual Hour", [False, True])
        impossible_travel = st.selectbox("Impossible Travel", [False, True])

    with col3:
        suspicious_ip = st.selectbox("Suspicious IP", [False, True])
        login_success = st.selectbox("Login Success", [True, False])
        device_type = st.selectbox("Device Type", sorted(df["device_type"].dropna().unique()))
        browser = st.selectbox("Browser", sorted(df["browser"].dropna().unique()))
        country = st.selectbox("Country", sorted(df["country"].dropna().unique()))
        mfa_type = st.selectbox("MFA Type", sorted(df["mfa_type"].dropna().unique()))

    login_event = {
        "login_hour": login_hour,
        "failed_attempts": failed_attempts,
        "mfa_failed_attempts": mfa_failed_attempts,
        "mfa_used": mfa_used,
        "new_device": new_device,
        "foreign_login": foreign_login,
        "unusual_hour": unusual_hour,
        "impossible_travel": impossible_travel,
        "suspicious_ip": suspicious_ip,
        "login_success": login_success,
        "device_type": device_type,
        "browser": browser,
        "country": country,
        "mfa_type": mfa_type,
    }

    if st.button("Analyze Login"):
        rule_result = calculate_risk_score(login_event)

        st.subheader("Rule-Based Risk Result")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Risk Score", rule_result["risk_score"])
        col_b.metric("Risk Level", rule_result["risk_level"])
        col_c.metric("Recommended Action", rule_result["recommended_action"])

        st.write("Risk Reasons:")
        st.info(rule_result["risk_reasons"])

        st.subheader("Machine Learning Prediction")

        try:
            ml_result = predict_login(login_event)

            col_x, col_y, col_z = st.columns(3)
            col_x.metric("Prediction", ml_result["prediction_label"])
            col_y.metric("Suspicious Probability", ml_result["suspicious_probability"])
            col_z.metric("Model Used", ml_result["model_used"])

        except Exception as error:
            st.warning(f"ML prediction unavailable: {error}")


def show_optimizer_page():
    st.title("⚙️ Authentication Optimizer")

    st.write(
        "Adjust the priority sliders to change how the optimizer balances security, "
        "cost, user friction, and implementation complexity."
    )

    risk_level = st.selectbox(
        "Risk Level",
        ["Low", "Medium", "High", "Critical"],
    )

    st.subheader("Priority Sliders")

    security = st.slider("Security Priority", 0.0, 1.0, DEFAULT_WEIGHTS["security"], 0.05)
    cost = st.slider("Cost Priority", 0.0, 1.0, DEFAULT_WEIGHTS["cost"], 0.05)
    friction = st.slider("Convenience / Low-Friction Priority", 0.0, 1.0, DEFAULT_WEIGHTS["friction"], 0.05)
    complexity = st.slider("Low-Complexity Priority", 0.0, 1.0, DEFAULT_WEIGHTS["complexity"], 0.05)

    total = round(security + cost + friction + complexity, 2)

    st.write(f"Current total weight: **{total}**")

    if total != 1.0:
        st.warning("Weights must add up to 1.0 before optimization can run.")
        return

    weights = {
        "security": security,
        "cost": cost,
        "friction": friction,
        "complexity": complexity,
    }

    result = optimize_authentication_strategy(
        risk_level=risk_level,
        weights=weights,
    )

    st.subheader("Recommendation")

    col1, col2 = st.columns(2)
    col1.metric("Recommended Strategy", result["recommended_strategy"])
    col2.metric("Optimization Score", result["optimization_score"])

    st.write("Recommended Action:")
    st.success(result["recommended_action"])

    st.write("Tradeoff Explanation:")
    st.info(result["explanation"])

    st.subheader("Strategy Comparison Table")
    st.dataframe(result["strategy_rankings"], use_container_width=True)

    st.subheader("All Strategy Scores Under These Priorities")
    all_scores = compare_all_strategies(weights=weights)
    st.dataframe(all_scores, use_container_width=True)


def show_model_performance_page():
    st.title("📈 Model Performance")

    results_df = load_model_results()
    importance_df = load_feature_importance()

    if results_df.empty:
        st.warning("Model results not found. Run model training first.")
    else:
        st.subheader("Model Comparison Results")
        st.dataframe(results_df, use_container_width=True)

        fig = px.bar(
            results_df,
            x="model",
            y=["accuracy", "precision", "recall", "f1_score"],
            barmode="group",
            title="Model Metric Comparison",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    if importance_df.empty:
        st.warning("Feature importance file not found.")
    else:
        st.subheader("Top Feature Importance")

        top_features = importance_df.head(15)

        fig = px.bar(
            top_features.sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            title="Top 15 ML Features",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(top_features, use_container_width=True)


def show_about_page():
    st.title("ℹ️ About")

    st.write(
        """
        Smart Security Optimizer is a cybersecurity analytics project that uses
        synthetic login data, rule-based risk scoring, machine learning, and
        authentication optimization to recommend safer login decisions.
        """
    )

    st.subheader("Main Components")

    st.write(
        """
        - Synthetic login data generator
        - Data validation and preprocessing
        - Rule-based risk scoring engine
        - Machine-learning suspicious login classifier
        - Authentication optimization engine
        - Streamlit dashboard
        """
    )

    st.subheader("Limitations")

    st.write(
        """
        This project uses synthetic data and is intended for educational purposes.
        It is not connected to real authentication systems, real user accounts,
        or live IP reputation services.
        """
    )

    st.subheader("Author")

    st.write("Atharv Sharma")


def main():
    df = load_scored_data()
    filtered_df = apply_filters(df)

    page = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "Login Analysis",
            "Risk Predictor",
            "Optimizer",
            "Model Performance",
            "About",
        ],
    )

    if page == "Overview":
        show_overview_page(filtered_df)

    elif page == "Login Analysis":
        show_login_analysis_page(filtered_df)

    elif page == "Risk Predictor":
        show_risk_predictor_page(df)

    elif page == "Optimizer":
        show_optimizer_page()

    elif page == "Model Performance":
        show_model_performance_page()

    elif page == "About":
        show_about_page()


if __name__ == "__main__":
    main()