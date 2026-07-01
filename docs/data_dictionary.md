# Data Dictionary

This document defines the login-event data schema for the Smart Security Optimizer project. Each row in the dataset represents one login attempt.

## Login Event Schema

| Field Name | Data Type | Variable Type | Example | Description |
|---|---|---|---|---|
| login_id | string | Identifier | L000001 | Unique ID for each login event |
| user_id | string | Identifier | U104 | Unique ID for each user |
| timestamp | datetime | Date/Time | 2026-07-06 09:42:00 | Date and time of the login attempt |
| login_hour | integer | Numeric | 9 | Hour of the day extracted from timestamp |
| day_of_week | string | Categorical | Monday | Day of the week when login occurred |
| country | string | Categorical | United States | Country where the login came from |
| city | string | Categorical | New York | City where the login came from |
| usual_country | string | Categorical | United States | User’s normal login country |
| device_type | string | Categorical | Laptop | Type of device used for login |
| browser | string | Categorical | Chrome | Browser used for login |
| ip_address | string | Categorical | 192.0.2.15 | Synthetic IP address used for login |
| failed_attempts | integer | Numeric | 3 | Number of failed attempts before this login |
| mfa_used | boolean | Boolean | True | Whether multi-factor authentication was used |
| mfa_type | string | Categorical | Authenticator App | Type of MFA used |
| new_device | boolean | Boolean | False | Whether the login came from a new device |
| foreign_login | boolean | Boolean | False | Whether login came from outside the user's usual country |
| unusual_hour | boolean | Boolean | False | Whether login occurred at an unusual time |
| impossible_travel | boolean | Boolean | False | Whether the login location changed too quickly to be realistic |
| suspicious_ip | boolean | Boolean | True | Whether the IP address is marked suspicious |
| login_success | boolean | Boolean | True | Whether the login attempt succeeded |
| attack_type | string | Categorical | Brute Force | Type of simulated login behavior |
| is_suspicious | integer | Target Variable | 1 | Machine-learning target: 1 = suspicious, 0 = normal |
| risk_score | integer | Numeric / Output | 75 | Rule-based risk score from 0 to 100 |
| risk_level | string | Categorical / Output | High | Risk category based on risk score |
| recommended_action | string | Categorical / Output | Require stronger MFA | Security response recommended by the system |

## Variable Type Groups

### Numeric Variables

Numeric variables are fields that contain numbers and can be used directly in calculations or model training.

- login_hour
- failed_attempts
- risk_score

### Categorical Variables

Categorical variables represent labels or groups.

- day_of_week
- country
- city
- usual_country
- device_type
- browser
- ip_address
- mfa_type
- attack_type
- risk_level
- recommended_action

### Boolean Variables

Boolean variables are true/false fields.

- mfa_used
- new_device
- foreign_login
- unusual_hour
- impossible_travel
- suspicious_ip
- login_success

### Identifier Variables

Identifier variables are used to track records but should usually not be used directly for machine-learning predictions.

- login_id
- user_id

### Target Variable

The target variable is what the machine-learning model will try to predict.

- is_suspicious

Values:

| Value | Meaning |
|---:|---|
| 0 | Normal login |
| 1 | Suspicious login |

## Attack Type Categories

The `attack_type` field will describe the type of login event.

Possible values:

- Normal
- Brute Force
- Credential Stuffing
- Impossible Travel
- New Device Login
- Suspicious IP Login
- MFA Fatigue
- Foreign Login
- Unusual Hour Login

## Risk Level Categories

The `risk_level` field will be based on the `risk_score`.

| Risk Score | Risk Level |
|---:|---|
| 0–29 | Low |
| 30–59 | Medium |
| 60–79 | High |
| 80–100 | Critical |

## Notes

This dataset will be synthetic and will not contain real user information. The purpose of the schema is to create realistic login-security data that can be used for risk scoring, machine-learning classification, optimization, and dashboard visualization.