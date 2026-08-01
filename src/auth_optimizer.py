from pathlib import Path

import pandas as pd


AUTH_STRATEGIES = {
    "Password Only": {
        "security": 2,
        "cost": 1,
        "friction": 1,
        "complexity": 1,
    },
    "SMS MFA": {
        "security": 5,
        "cost": 3,
        "friction": 4,
        "complexity": 3,
    },
    "App MFA": {
        "security": 7,
        "cost": 4,
        "friction": 5,
        "complexity": 4,
    },
    "Passwordless": {
        "security": 9,
        "cost": 6,
        "friction": 3,
        "complexity": 7,
    },
}


DEFAULT_WEIGHTS = {
    "security": 0.50,
    "cost": 0.20,
    "friction": 0.20,
    "complexity": 0.10,
}


ORGANIZATION_PROFILES = {
    "small_company": {
        "security": 0.40,
        "cost": 0.30,
        "friction": 0.20,
        "complexity": 0.10,
    },
    "bank": {
        "security": 0.70,
        "cost": 0.10,
        "friction": 0.10,
        "complexity": 0.10,
    },
    "school": {
        "security": 0.45,
        "cost": 0.25,
        "friction": 0.20,
        "complexity": 0.10,
    },
    "technology_company": {
        "security": 0.60,
        "cost": 0.10,
        "friction": 0.15,
        "complexity": 0.15,
    },
}


RISK_LEVEL_ALLOWED_STRATEGIES = {
    "Low": ["Password Only", "SMS MFA"],
    "Medium": ["SMS MFA", "App MFA"],
    "High": ["App MFA", "Passwordless"],
    "Critical": ["Block Login"],
}


RISK_LEVEL_ACTIONS = {
    "Low": "Allow login or use lightweight authentication",
    "Medium": "Require MFA",
    "High": "Require stronger MFA or passwordless authentication",
    "Critical": "Block login or require additional identity verification",
}


def validate_weights(weights=None):
    """
    Validate optimizer weights.

    Weights must:
    - contain security, cost, friction, and complexity
    - be non-negative
    - add up to 1.0
    """

    if weights is None:
        return DEFAULT_WEIGHTS

    required_keys = {"security", "cost", "friction", "complexity"}

    missing_keys = required_keys - set(weights.keys())
    extra_keys = set(weights.keys()) - required_keys

    if missing_keys:
        raise ValueError(f"Missing weight keys: {missing_keys}")

    if extra_keys:
        raise ValueError(f"Unexpected weight keys: {extra_keys}")

    for key, value in weights.items():
        if value < 0:
            raise ValueError(f"Weight for {key} cannot be negative.")

    total_weight = sum(weights.values())

    if round(total_weight, 4) != 1.0:
        raise ValueError(
            f"Weights must add up to 1.0. Current total: {round(total_weight, 4)}"
        )

    return weights


def get_weights_for_profile(profile_name=None):
    """
    Return default weights or organization-specific weights.
    """

    if profile_name is None:
        return DEFAULT_WEIGHTS

    if profile_name not in ORGANIZATION_PROFILES:
        raise ValueError(f"Unknown organization profile: {profile_name}")

    return ORGANIZATION_PROFILES[profile_name]


def calculate_optimization_score(strategy_scores, weights=None):
    """
    Calculate the optimization score for one authentication strategy.

    Higher scores are better.

    Formula:
    score =
        security_weight * security
        - cost_weight * cost
        - friction_weight * friction
        - complexity_weight * complexity
    """

    weights = validate_weights(weights)

    score = (
        weights["security"] * strategy_scores["security"]
        - weights["cost"] * strategy_scores["cost"]
        - weights["friction"] * strategy_scores["friction"]
        - weights["complexity"] * strategy_scores["complexity"]
    )

    return round(score, 4)


def get_allowed_strategies(risk_level):
    """
    Return authentication strategies allowed for a risk level.
    """

    if risk_level not in RISK_LEVEL_ALLOWED_STRATEGIES:
        raise ValueError(f"Unknown risk level: {risk_level}")

    return RISK_LEVEL_ALLOWED_STRATEGIES[risk_level]


def explain_strategy_choice(
    strategy_name,
    risk_level,
    strategy_scores=None,
    optimization_score=None,
    weights=None,
):
    """
    Create a human-readable explanation for the authentication recommendation.
    """

    if strategy_name == "Block Login":
        return (
            "Critical-risk login detected. The safest action is to block the login "
            "or require additional identity verification before access is allowed."
        )

    return (
        f"{strategy_name} was selected for a {risk_level} risk login because it had "
        f"the best optimization score among the allowed strategies. "
        f"The score balances security={strategy_scores['security']}, "
        f"cost={strategy_scores['cost']}, friction={strategy_scores['friction']}, "
        f"and complexity={strategy_scores['complexity']} using weights "
        f"security={weights['security']}, cost={weights['cost']}, "
        f"friction={weights['friction']}, complexity={weights['complexity']}. "
        f"Final optimization score: {optimization_score}."
    )


def optimize_authentication_strategy(risk_level, weights=None, profile_name=None):
    """
    Select the best authentication strategy for a given risk level.

    Supports:
    - default weights
    - custom weights
    - organization-specific profiles
    - blocking critical-risk logins
    - explanatory outputs
    """

    if weights is not None and profile_name is not None:
        raise ValueError("Use either custom weights or profile_name, not both.")

    if profile_name is not None:
        weights = get_weights_for_profile(profile_name)

    weights = validate_weights(weights)

    allowed_strategies = get_allowed_strategies(risk_level)

    if allowed_strategies == ["Block Login"]:
        explanation = explain_strategy_choice(
            strategy_name="Block Login",
            risk_level=risk_level,
            weights=weights,
        )

        strategy_rankings = pd.DataFrame(
            [
                {
                    "strategy": "Block Login",
                    "risk_level": risk_level,
                    "security": None,
                    "cost": None,
                    "friction": None,
                    "complexity": None,
                    "optimization_score": None,
                    "explanation": explanation,
                }
            ]
        )

        return {
            "risk_level": risk_level,
            "recommended_action": RISK_LEVEL_ACTIONS[risk_level],
            "recommended_strategy": "Block Login",
            "optimization_score": None,
            "weights_used": weights,
            "explanation": explanation,
            "strategy_rankings": strategy_rankings,
        }

    results = []

    for strategy_name in allowed_strategies:
        strategy_scores = AUTH_STRATEGIES[strategy_name]
        optimization_score = calculate_optimization_score(strategy_scores, weights)

        explanation = explain_strategy_choice(
            strategy_name=strategy_name,
            risk_level=risk_level,
            strategy_scores=strategy_scores,
            optimization_score=optimization_score,
            weights=weights,
        )

        results.append(
            {
                "strategy": strategy_name,
                "risk_level": risk_level,
                "security": strategy_scores["security"],
                "cost": strategy_scores["cost"],
                "friction": strategy_scores["friction"],
                "complexity": strategy_scores["complexity"],
                "optimization_score": optimization_score,
                "explanation": explanation,
            }
        )

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        by="optimization_score",
        ascending=False,
    )

    best_row = results_df.iloc[0]

    return {
        "risk_level": risk_level,
        "recommended_action": RISK_LEVEL_ACTIONS[risk_level],
        "recommended_strategy": best_row["strategy"],
        "optimization_score": best_row["optimization_score"],
        "weights_used": weights,
        "explanation": best_row["explanation"],
        "strategy_rankings": results_df,
    }


def compare_all_strategies(weights=None, profile_name=None):
    """
    Compare all authentication strategies without filtering by risk level.
    """

    if weights is not None and profile_name is not None:
        raise ValueError("Use either custom weights or profile_name, not both.")

    if profile_name is not None:
        weights = get_weights_for_profile(profile_name)

    weights = validate_weights(weights)

    results = []

    for strategy_name, strategy_scores in AUTH_STRATEGIES.items():
        optimization_score = calculate_optimization_score(strategy_scores, weights)

        results.append(
            {
                "strategy": strategy_name,
                "security": strategy_scores["security"],
                "cost": strategy_scores["cost"],
                "friction": strategy_scores["friction"],
                "complexity": strategy_scores["complexity"],
                "optimization_score": optimization_score,
            }
        )

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        by="optimization_score",
        ascending=False,
    )

    return results_df


def test_organization_scenarios():
    """
    Test authentication recommendations for different organization types.
    """

    scenarios = []

    for profile_name in ORGANIZATION_PROFILES:
        for risk_level in ["Low", "Medium", "High", "Critical"]:
            result = optimize_authentication_strategy(
                risk_level=risk_level,
                profile_name=profile_name,
            )

            scenarios.append(
                {
                    "organization_profile": profile_name,
                    "risk_level": risk_level,
                    "recommended_strategy": result["recommended_strategy"],
                    "recommended_action": result["recommended_action"],
                    "optimization_score": result["optimization_score"],
                    "explanation": result["explanation"],
                }
            )

    return pd.DataFrame(scenarios)


def save_scenario_results():
    """
    Save organization scenario results to data/processed/authentication_scenario_results.csv.
    """

    project_root = Path(__file__).resolve().parents[1]
    output_path = (
        project_root
        / "data"
        / "processed"
        / "authentication_scenario_results.csv"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    scenario_df = test_organization_scenarios()
    scenario_df.to_csv(output_path, index=False)

    print(f"Authentication scenario results saved to: {output_path}")

    return scenario_df


def main():
    """
    Run the authentication optimizer.
    """

    print("AUTHENTICATION STRATEGY SCORES")
    print("=" * 50)
    print(compare_all_strategies())

    print()
    print("RISK-BASED AUTHENTICATION RECOMMENDATIONS")
    print("=" * 50)

    for risk_level in ["Low", "Medium", "High", "Critical"]:
        result = optimize_authentication_strategy(risk_level)

        print()
        print(f"Risk Level: {risk_level}")
        print(f"Recommended Action: {result['recommended_action']}")
        print(f"Recommended Strategy: {result['recommended_strategy']}")
        print(f"Explanation: {result['explanation']}")

    print()
    print("ORGANIZATION SCENARIOS")
    print("=" * 50)

    scenario_df = save_scenario_results()
    print(scenario_df)


if __name__ == "__main__":
    main()