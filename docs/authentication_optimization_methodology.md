# Authentication Optimization Methodology

## Purpose

The Smart Security Optimizer does more than detect risky logins. It also recommends an authentication action based on the login risk level, security benefit, cost, user friction, and implementation complexity.

The optimizer helps decide which authentication strategy should be used for a login event. It balances strong security with practical business concerns such as budget, user convenience, and implementation difficulty.

## Authentication Strategies

The project compares four authentication strategies.

| Strategy | Description |
|---|---|
| Password Only | User logs in with only a password. |
| SMS MFA | User enters a password and verifies with an SMS code. |
| App MFA | User enters a password and verifies using an authenticator app. |
| Passwordless | User logs in using a stronger method such as passkey, biometric, or trusted-device authentication. |

Critical-risk logins are handled separately. Instead of choosing one of the four authentication strategies, the optimizer recommends blocking the login or requiring additional identity verification.

## Strategy Scores

Each authentication strategy is scored from `1` to `10` across four dimensions.

| Score Type | Meaning |
|---|---|
| Security | Higher score means stronger account protection. |
| Cost | Higher score means more expensive to implement or operate. |
| Friction | Higher score means more inconvenience for the user. |
| Complexity | Higher score means harder to implement and maintain. |

## Authentication Strategy Table

| Strategy | Security | Cost | Friction | Complexity | Explanation |
|---|---:|---:|---:|---:|---|
| Password Only | 2 | 1 | 1 | 1 | Easy and cheap, but weakest security. |
| SMS MFA | 5 | 3 | 4 | 3 | Better than password only, but weaker than app-based MFA and passwordless methods. |
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

The weights must add up to `1.0`.

## Adjustable Priorities

The optimizer supports adjustable priorities. This allows different organizations to make different tradeoffs.

For example, a bank may prioritize security more heavily, while a small company may care more about cost and implementation simplicity.

## Organization Profiles

The project includes four organization profiles.

| Profile | Security Weight | Cost Weight | Friction Weight | Complexity Weight | Reasoning |
|---|---:|---:|---:|---:|---|
| Small Company | 0.40 | 0.30 | 0.20 | 0.10 | Balances security with limited budget. |
| Bank | 0.70 | 0.10 | 0.10 | 0.10 | Prioritizes security because account compromise has high impact. |
| School | 0.45 | 0.25 | 0.20 | 0.10 | Balances student usability, cost, and reasonable security. |
| Technology Company | 0.60 | 0.10 | 0.15 | 0.15 | Prioritizes strong security and can handle more technical complexity. |

## Risk-Based Strategy Selection

The optimizer uses the login risk level to limit which strategies are allowed.

| Risk Level | Allowed Options | Recommended Action |
|---|---|---|
| Low | Password Only, SMS MFA | Allow login or use lightweight authentication |
| Medium | SMS MFA, App MFA | Require MFA |
| High | App MFA, Passwordless | Require stronger MFA or passwordless authentication |
| Critical | Block Login | Block login or require additional identity verification |

This makes the optimizer risk-aware. Low-risk logins can use simpler authentication, while high-risk and critical-risk logins require stronger protection.

## Explanatory Outputs

The optimizer returns an explanation with each recommendation. The explanation includes:

- The risk level
- The selected authentication strategy
- The recommended action
- The strategy score
- The weights used
- The reason the selected strategy ranked highest

For critical-risk logins, the explanation states that the login should be blocked or require additional identity verification.

## Scenario Testing

The optimizer is tested across four organization scenarios:

- Small company
- Bank
- School
- Technology company

Each scenario uses different weights to reflect different priorities. The scenario results are saved to:

```text
data/processed/authentication_scenario_results.csv
```

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

The optimizer calculates this score for each allowed strategy and selects the allowed strategy with the highest score.

## Unit Tests

The authentication optimizer includes tests for:

- Risk-level strategy mapping
- Critical-risk blocking
- Weight validation
- Invalid weight totals
- Negative weights
- Missing weight keys
- Organization profiles
- Weighting preferences
- Edge cases
- Explanatory outputs

## Limitations

The current strategy scores are manually defined. They are reasonable assumptions for an educational cybersecurity project, but real organizations may score each method differently depending on their technology stack, security requirements, user population, and budget.

The optimizer does not currently use real financial cost data, live security incident data, or real user feedback. Future versions can improve the optimizer by using real cost estimates, user behavior data, security incident history, and organization-specific risk tolerance.