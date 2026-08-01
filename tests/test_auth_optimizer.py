import pytest

from src.auth_optimizer import (
    AUTH_STRATEGIES,
    DEFAULT_WEIGHTS,
    ORGANIZATION_PROFILES,
    calculate_optimization_score,
    compare_all_strategies,
    get_allowed_strategies,
    get_weights_for_profile,
    optimize_authentication_strategy,
    validate_weights,
)


def test_validate_default_weights():
    weights = validate_weights(DEFAULT_WEIGHTS)

    assert weights["security"] == 0.50
    assert sum(weights.values()) == 1.0


def test_invalid_weight_total_raises_error():
    bad_weights = {
        "security": 0.60,
        "cost": 0.20,
        "friction": 0.20,
        "complexity": 0.20,
    }

    with pytest.raises(ValueError):
        validate_weights(bad_weights)


def test_negative_weight_raises_error():
    bad_weights = {
        "security": 0.70,
        "cost": -0.10,
        "friction": 0.20,
        "complexity": 0.20,
    }

    with pytest.raises(ValueError):
        validate_weights(bad_weights)


def test_missing_weight_key_raises_error():
    bad_weights = {
        "security": 0.60,
        "cost": 0.20,
        "friction": 0.20,
    }

    with pytest.raises(ValueError):
        validate_weights(bad_weights)


def test_low_risk_allowed_strategies():
    strategies = get_allowed_strategies("Low")

    assert "Password Only" in strategies
    assert "SMS MFA" in strategies
    assert "Passwordless" not in strategies


def test_medium_risk_allowed_strategies():
    strategies = get_allowed_strategies("Medium")

    assert strategies == ["SMS MFA", "App MFA"]


def test_high_risk_allowed_strategies():
    strategies = get_allowed_strategies("High")

    assert strategies == ["App MFA", "Passwordless"]


def test_critical_risk_blocks_login():
    result = optimize_authentication_strategy("Critical")

    assert result["recommended_strategy"] == "Block Login"
    assert "Block login" in result["recommended_action"]
    assert "Critical-risk login detected" in result["explanation"]


def test_invalid_risk_level_raises_error():
    with pytest.raises(ValueError):
        get_allowed_strategies("Extreme")


def test_calculate_optimization_score_returns_number():
    score = calculate_optimization_score(AUTH_STRATEGIES["App MFA"])

    assert isinstance(score, float)


def test_security_heavy_weights_prefer_passwordless_for_high_risk():
    security_heavy_weights = {
        "security": 0.80,
        "cost": 0.05,
        "friction": 0.05,
        "complexity": 0.10,
    }

    result = optimize_authentication_strategy(
        risk_level="High",
        weights=security_heavy_weights,
    )

    assert result["recommended_strategy"] == "Passwordless"


def test_cost_sensitive_weights_can_prefer_app_mfa_for_high_risk():
    cost_sensitive_weights = {
        "security": 0.35,
        "cost": 0.45,
        "friction": 0.10,
        "complexity": 0.10,
    }

    result = optimize_authentication_strategy(
        risk_level="High",
        weights=cost_sensitive_weights,
    )

    assert result["recommended_strategy"] == "App MFA"


def test_organization_profiles_exist():
    assert "small_company" in ORGANIZATION_PROFILES
    assert "bank" in ORGANIZATION_PROFILES
    assert "school" in ORGANIZATION_PROFILES
    assert "technology_company" in ORGANIZATION_PROFILES


def test_bank_profile_prioritizes_security():
    weights = get_weights_for_profile("bank")

    assert weights["security"] == 0.70
    assert weights["security"] > weights["cost"]


def test_unknown_profile_raises_error():
    with pytest.raises(ValueError):
        get_weights_for_profile("hospital")


def test_cannot_use_weights_and_profile_together():
    custom_weights = {
        "security": 0.50,
        "cost": 0.20,
        "friction": 0.20,
        "complexity": 0.10,
    }

    with pytest.raises(ValueError):
        optimize_authentication_strategy(
            risk_level="Medium",
            weights=custom_weights,
            profile_name="bank",
        )


def test_compare_all_strategies_returns_all_auth_methods():
    results_df = compare_all_strategies()

    assert len(results_df) == 4
    assert set(results_df["strategy"]) == {
        "Password Only",
        "SMS MFA",
        "App MFA",
        "Passwordless",
    }


def test_optimizer_returns_explanation_and_rankings():
    result = optimize_authentication_strategy("Medium")

    assert "recommended_strategy" in result
    assert "recommended_action" in result
    assert "explanation" in result
    assert "strategy_rankings" in result
    assert not result["strategy_rankings"].empty