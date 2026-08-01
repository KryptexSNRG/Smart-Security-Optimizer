# Authentication Optimization Methodology

## Purpose

The Smart Security Optimizer does more than detect risky logins. It also recommends an authentication strategy based on risk, security strength, cost, user friction, and implementation complexity.

The goal is to choose an authentication method that improves security while keeping cost and user inconvenience reasonable.

## Authentication Strategies

The project compares four authentication strategies:

| Strategy | Description |
|---|---|
| Password Only | User logs in with only a password. |
| SMS MFA | User enters a password and verifies with an SMS code. |
| App MFA | User enters a password and verifies using an authenticator app. |
| Passwordless | User logs in using a stronger method such as passkey, biometric, or device-based authentication. |

## Strategy Scores

Each strategy is scored from `1` to `10` across four dimensions.

| Score Type | Meaning |
|---|---|
| Security | Higher score means stronger protection. |
| Cost | Higher score means more expensive to implement or operate. |
| Friction | Higher score means more inconvenience for the user. |
| Complexity | Higher score means harder to implement and maintain. |

## Authentication Strategy Table

| Strategy | Security | Cost | Friction | Complexity | Explanation |
|---|---:|---:|---:|---:|---|
| Password Only | 2 | 1 | 1 | 1 | Easy and cheap, but weakest security. |
| SMS MFA | 5 | 3 | 4 | 3 | Better than password only, but vulnerable to SIM-swapping and phishing. |
| App MFA | 7 | 4 | 5 | 4 | Stronger than SMS MFA and commonly used in enterprise environments. |
| Passwordless | 9 | 6 | 3 | 7 | Strong security and lower user friction after setup, but more complex to implement. |

## Optimization Formula

The optimizer calculates a weighted score for each authentication strategy.

The formula is:

```text
optimization_score =
    (security_weight * security)
    - (cost_weight * cost)
    - (friction_weight * friction)
    - (complexity_weight * complexity)
```

Higher optimization scores are better.

## Default Weights

The default weights are:

| Factor | Weight |
|---|---:|
| Security | 0.50 |
| Cost | 0.20 |
| Friction | 0.20 |
| Complexity | 0.10 |

These weights prioritize security while still considering cost, convenience, and implementation difficulty.

## Why Security Has the Highest Weight

Security receives the highest weight because the purpose of the system is to prevent suspicious or dangerous logins. However, cost and friction are still included because the strongest security option is not always the best choice for every login.

For example, requiring passwordless authentication for every low-risk login may be unnecessary and inconvenient. But requiring stronger authentication for high-risk or critical-risk logins makes sense.

## Risk-Based Strategy Selection

The optimizer can also use the login risk level to narrow the available authentication options.

| Risk Level | Allowed Strategy Options |
|---|---|
| Low | Password Only, SMS MFA |
| Medium | SMS MFA, App MFA |
| High | App MFA, Passwordless |
| Critical | Passwordless |

This makes the optimizer risk-aware. Low-risk logins can use simpler authentication, while high-risk and critical-risk logins require stronger protection.

## Example Calculation

Example strategy:

```text
Strategy: App MFA
Security: 7
Cost: 4
Friction: 5
Complexity: 4
```

Using the default formula:

```text
optimization_score =
    (0.50 * 7)
    - (0.20 * 4)
    - (0.20 * 5)
    - (0.10 * 4)
```

Calculation:

```text
optimization_score = 3.5 - 0.8 - 1.0 - 0.4
optimization_score = 1.3
```

The optimizer calculates this score for each allowed strategy and selects the strategy with the highest score.

## Limitations

The current strategy scores are manually defined. They are reasonable assumptions for an educational cybersecurity project, but real organizations may assign different scores depending on their technology stack, security requirements, user population, and budget.

Future versions can improve the optimizer by using real cost data, user behavior data, security incident history, and organization-specific risk tolerance.