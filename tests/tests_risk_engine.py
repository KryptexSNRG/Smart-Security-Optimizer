import pytest

from src.risk_engine import calculate_risk_score, get_risk_level, get_recommended_action


def make_login_event(
    new_device=False,
    foreign_login=False,
    unusual_hour=False,
    failed_attempts=0,
    mfa_used=True,
    impossible_travel=False,
    suspicious_ip=False,
    mfa_failed_attempts=0,
    login_success=True,
):
    """
    Helper function to create a fake login event for testing.
    """

    return {
        "new_device": new_device,
        "foreign_login": foreign_login,
        "unusual_hour": unusual_hour,
        "failed_attempts": failed_attempts,
        "mfa_used": mfa_used,
        "impossible_travel": impossible_travel,
        "suspicious_ip": suspicious_ip,
        "mfa_failed_attempts": mfa_failed_attempts,
        "login_success": login_success,
    }


def test_normal_login_scores_low():
    """
    A normal login should receive a low risk score.
    """

    login_event = make_login_event()

    result = calculate_risk_score(login_event)

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"
    assert result["recommended_action"] == "Allow login"
    assert "No major suspicious risk factors" in result["risk_reasons"]


def test_new_device_login_scores_medium():
    """
    A new-device login should receive at least Medium risk under the tuned rules.
    """

    login_event = make_login_event(new_device=True)

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 30
    assert result["risk_level"] in ["Medium", "High", "Critical"]
    assert "new device" in result["risk_reasons"].lower()


def test_foreign_login_scores_medium():
    """
    A foreign login should receive at least Medium risk.
    """

    login_event = make_login_event(foreign_login=True)

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 30
    assert result["risk_level"] in ["Medium", "High", "Critical"]
    assert "foreign" in result["risk_reasons"].lower()


def test_brute_force_login_scores_high_or_critical():
    """
    A brute-force style login with many failed attempts should receive High or Critical risk.
    """

    login_event = make_login_event(
        failed_attempts=7,
        login_success=True,
        mfa_used=False,
    )

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 60
    assert result["risk_level"] in ["High", "Critical"]
    assert "failed attempts" in result["risk_reasons"].lower()


def test_no_mfa_login_scores_medium():
    """
    A login without MFA should receive at least Medium risk under the tuned rules.
    """

    login_event = make_login_event(mfa_used=False)

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 30
    assert result["risk_level"] in ["Medium", "High", "Critical"]
    assert "multi-factor authentication was not used" in result["risk_reasons"].lower()


def test_impossible_travel_scores_high_or_critical():
    """
    Impossible travel should create a high-risk or critical-risk login.
    """

    login_event = make_login_event(
        foreign_login=True,
        impossible_travel=True,
    )

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 60
    assert result["risk_level"] in ["High", "Critical"]
    assert "impossible travel" in result["risk_reasons"].lower()


def test_suspicious_ip_scores_medium_or_higher():
    """
    A suspicious IP should receive at least Medium risk.
    """

    login_event = make_login_event(suspicious_ip=True)

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 30
    assert result["risk_level"] in ["Medium", "High", "Critical"]
    assert "suspicious ip" in result["risk_reasons"].lower()


def test_mfa_fatigue_scores_medium_or_higher():
    """
    Repeated MFA failures should receive at least Medium risk.
    """

    login_event = make_login_event(
        mfa_used=True,
        mfa_failed_attempts=5,
    )

    result = calculate_risk_score(login_event)

    assert result["risk_score"] >= 30
    assert result["risk_level"] in ["Medium", "High", "Critical"]
    assert "mfa" in result["risk_reasons"].lower()


def test_score_is_capped_at_100():
    """
    A login with many risk factors should not exceed a score of 100.
    """

    login_event = make_login_event(
        new_device=True,
        foreign_login=True,
        unusual_hour=True,
        failed_attempts=10,
        mfa_used=False,
        impossible_travel=True,
        suspicious_ip=True,
        mfa_failed_attempts=8,
        login_success=True,
    )

    result = calculate_risk_score(login_event)

    assert result["risk_score"] == 100
    assert result["risk_level"] == "Critical"


def test_get_risk_level_boundaries():
    """
    Test score boundaries for Low, Medium, High, and Critical.
    """

    assert get_risk_level(0) == "Low"
    assert get_risk_level(29) == "Low"

    assert get_risk_level(30) == "Medium"
    assert get_risk_level(59) == "Medium"

    assert get_risk_level(60) == "High"
    assert get_risk_level(79) == "High"

    assert get_risk_level(80) == "Critical"
    assert get_risk_level(100) == "Critical"


def test_recommended_actions():
    """
    Test that each risk level maps to the correct recommendation.
    """

    assert get_recommended_action("Low") == "Allow login"
    assert get_recommended_action("Medium") == "Require MFA"
    assert get_recommended_action("High") == "Require stronger MFA"
    assert (
        get_recommended_action("Critical")
        == "Block login or require additional identity verification"
    )