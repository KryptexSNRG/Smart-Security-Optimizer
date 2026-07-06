# Risk Scoring Methodology

## Purpose

The Smart Security Optimizer uses a point-based risk scoring system to evaluate each login attempt. The goal is to assign every login a score from **0 to 100** based on suspicious behavior.

A higher score means the login is more risky. The final risk score will be used to classify logins as **Low**, **Medium**, **High**, or **Critical** risk.

## Risk Score Scale

| Risk Score | Risk Level | Meaning |
|---:|------------|---|
| 0–29 | Low        | Login appears normal |
| 30–59 | Medium     | Some suspicious signals are present |
| 60–79 | High       | Strong signs of suspicious behavior |
| 80–100 | Criti cal  | Login is highly suspicious or dangerous |

## Point-Based Risk Rules

Each suspicious condition adds points to the login’s risk score.

| Risk Factor | Condition | Points |
|---|---|---:|
| New device | `new_device == True` | +15 |
| Foreign login | `foreign_login == True` | +20 |
| Unusual login hour | `unusual_hour == True` | +10 |
| Multiple failed attempts | `failed_attempts >= 3` | +20 |
| High failed attempts | `failed_attempts >= 5` | +35 |
| MFA not used | `mfa_used == False` | +10 |
| Impossible travel | `impossible_travel == True` | +30 |
| Suspicious IP address | `suspicious_ip == True` | +25 |
| MFA fatigue risk | `mfa_failed_attempts >= 3` | +25 |
| Login success after high failures | `failed_attempts >= 5 and login_success == True` | +15 |

## Score Cap

The total risk score must be capped at **100**.

This means that even if multiple risk factors add up to more than 100, the final score should still be:

```text
100
```

Example:

```text
New device: +15
Foreign login: +20
High failed attempts: +35
No MFA: +10
Suspicious IP: +25

Raw score = 105
Final score = 100
```

## Example Risk Calculations

### Example 1: Normal Login

```text
Known device
Usual country
MFA used
0 failed attempts
Normal login hour
```

Risk score:

```text
0
```

Risk level:

```text
Low
```

Recommended action:

```text
Allow login
```

---

### Example 2: Medium-Risk Login

```text
New device
No MFA
1 failed attempt
```

Risk score:

```text
15 + 10 = 25
```

Risk level:

```text
Low
```

This login is still low risk, but close to medium. If another suspicious factor is added, it could become medium risk.

---

### Example 3: High-Risk Login

```text
Foreign login
New device
No MFA
3 failed attempts
```

Risk score:

```text
20 + 15 + 10 + 20 = 65
```

Risk level:

```text
High
```

Recommended action:

```text
Require stronger MFA
```

---

### Example 4: Critical-Risk Login

```text
Impossible travel
Suspicious IP address
5 failed attempts
No MFA
```

Risk score:

```text
30 + 25 + 35 + 10 = 100
```

Risk level:

```text
Critical
```

Recommended action:

```text
Block login or require additional identity verification
```

## Recommended Actions by Risk Level

| Risk Level | Recommended Action |
|---|---|
| Low | Allow login |
| Medium | Require MFA |
| High | Require stronger MFA |
| Critical | Block login or require additional identity verification |

## Why This Method Was Used

A point-based risk scoring system is easy to understand and explain. Each risk factor contributes to the final score, making the decision more transparent.

This is important because cybersecurity systems should not only classify a login as risky, but also explain why the login is risky.

## Limitations

This scoring system is rule-based, so it depends on manually chosen point values. The weights may not perfectly match real-world cybersecurity risk.

For example, a suspicious IP address may be more dangerous in some environments than others. Similarly, a new device may be normal for some users but risky for others.

Future versions of the project can improve the scoring system by using real-world data, user-specific behavior patterns, or machine-learning-based risk weighting.

## Summary

The risk scoring system converts login behavior into a clear score from **0 to 100**. It checks for suspicious signals such as failed attempts, no MFA, new devices, foreign logins, impossible travel, suspicious IPs, and MFA fatigue. The final score is capped at 100 and converted into a risk level that determines the recommended security response.