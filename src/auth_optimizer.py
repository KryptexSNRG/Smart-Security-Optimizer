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


RISK_LEVEL_ALLOWED_STRATEGIES = {
    "Low": ["Password Only", "SMS MFA"],
    "Medium": ["SMS MFA", "App MFA"],
    "High": ["App MFA", "Passwordless"],
    "Critical": ["Passwordless"],
}


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

    if weights is None:
        weights = DEFAULT_WEIGHTS

    score = (
        weights["security"] * strategy_scores["security"]
        - weights["cost"] * strategy_scores["cost"]
        - weights["friction"] * strategy_scores["friction"]
        - weights["complexity"] * strategy_scores["complexity"]
    )

    return round(score, 4)


def get_allowed_strategies(risk_level):
    """
    Return the authentication strategies allowed for a risk level.
    """

    if risk_level not in RISK_LEVEL_ALLOWED_STRATEGIES:
        raise ValueError(f"Unknown risk level: {risk_level}")

    return RISK_LEVEL_ALLOWED_STRATEGIES[risk_level]


def optimize_authentication_strategy(risk_level, weights=None):
    """
    Select the best authentication strategy for a given risk level.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS

    allowed_strategies = get_allowed_strategies(risk_level)

    results = []

    for strategy_name in allowed_strategies:
        strategy_scores = AUTH_STRATEGIES[strategy_name]
        optimization_score = calculate_optimization_score(strategy_scores, weights)

        results.append({
            "strategy": strategy_name,
            "risk_level": risk_level,
            "security": strategy_scores["security"],
            "cost": strategy_scores["cost"],
            "friction": strategy_scores["friction"],
            "complexity": strategy_scores["complexity"],
            "optimization_score": optimization_score,
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        by="optimization_score",
        ascending=False
    )

    best_strategy = results_df.iloc[0]["strategy"]

    return {
        "risk_level": risk_level,
        "recommended_strategy": best_strategy,
        "strategy_rankings": results_df,
    }


def compare_all_strategies(weights=None):
    """
    Compare all authentication strategies without filtering by risk level.
    """

    if weights is None:
        weights = DEFAULT_WEIGHTS

    results = []

    for strategy_name, strategy_scores in AUTH_STRATEGIES.items():
        optimization_score = calculate_optimization_score(strategy_scores, weights)

        results.append({
            "strategy": strategy_name,
            "security": strategy_scores["security"],
            "cost": strategy_scores["cost"],
            "friction": strategy_scores["friction"],
            "complexity": strategy_scores["complexity"],
            "optimization_score": optimization_score,
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        by="optimization_score",
        ascending=False
    )

    return results_df


def main():
    """
    Test the authentication optimizer.
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
        print(f"Recommended Strategy: {result['recommended_strategy']}")
        print(result["strategy_rankings"])


if __name__ == "__main__":
    main()