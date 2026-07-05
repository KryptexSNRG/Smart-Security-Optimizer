# Synthetic Data Methodology

## Purpose of Synthetic Data

The **Smart Security Optimizer** uses synthetic login data instead of real user data. Real login data can contain sensitive information such as usernames, locations, IP addresses, devices, and account behavior. Using synthetic data allows this project to simulate realistic cybersecurity scenarios without exposing private or personal information.

Synthetic data is also useful because it allows specific attack scenarios to be created intentionally. This makes it easier to test whether the system can detect suspicious login patterns such as brute-force attacks, foreign logins, impossible travel, new-device logins, no-MFA logins, unusual-hour activity, suspicious IP usage, credential stuffing, and MFA fatigue.

## How the Data Was Generated

The dataset was generated using a Python script located at:

```text
src/data_generator.py
```

The script creates synthetic user profiles. Each user is assigned a usual country, usual city, primary device, primary browser, and typical MFA behavior. Normal login events are generated based on these user profiles so that most users log in from familiar locations, devices, and browsers.

The generator then creates **10,000 login records**. Each record represents one login attempt and includes fields such as:

- User ID
- Timestamp
- Login hour
- Country
- City
- Device type
- Browser
- IP address
- Failed attempts
- MFA usage
- Login success
- Attack type
- Suspicious label

Most generated logins are normal, while a smaller percentage are suspicious. Suspicious events are created by modifying login fields in ways that match common cybersecurity threats. For example, brute-force attacks have many failed login attempts, foreign logins use a country different from the user’s usual country, no-MFA logins disable MFA, and unusual-hour logins occur between midnight and early morning.

## Simulated Threat Scenarios

The dataset includes the following simulated login scenarios:

| Scenario | How It Appears in the Data |
|---|---|
| Normal Login | Usual country, usual device, normal time, low failed attempts |
| Brute Force | High number of failed login attempts |
| Foreign Login | Login country differs from the user’s usual country |
| Impossible Travel | Login is marked as foreign and physically unrealistic |
| New Device Login | Login comes from a new or different device/browser |
| No MFA Login | MFA is not used and MFA type is set to `None` |
| Unusual Hour Login | Login occurs between 12 AM and 4 AM |
| Suspicious IP Login | Login uses an IP address marked as suspicious |
| Credential Stuffing | Suspicious IP address with multiple failed attempts |
| MFA Fatigue | Multiple MFA failures or repeated MFA attempts |

## Why This Approach Was Used

This approach was used because the project needs a dataset that is realistic enough to test cybersecurity logic but safe enough to share publicly on GitHub. Since the project is educational, synthetic data provides a controlled way to create both normal and suspicious login behavior.

The generated data supports multiple parts of the project, including:

- Data validation
- Data preprocessing
- Rule-based risk scoring
- Machine-learning classification
- Authentication optimization
- Dashboard visualization

## Current Limitations

The dataset is synthetic, so it does not perfectly represent real-world login behavior. Some attack labels are scenario-based, meaning the generator intentionally creates an attack type and then changes related fields to match that scenario.

For example, an impossible-travel event is currently simulated by marking the login as foreign and impossible. A more advanced version would calculate impossible travel by comparing a user’s previous login time and location with the current login time and location.

Other limitations include:

- No real IP reputation data is used.
- No real user behavior history is included.
- Some threat labels are generated rather than discovered.
- Geographic distance is not fully calculated yet.
- Login patterns are simplified compared to real enterprise systems.
- The dataset should not be used for production cybersecurity decisions.

## Future Improvements

Future versions of the dataset can be improved by making more threat indicators calculated directly from the data.

Possible improvements include:

- Calculating `foreign_login` from whether `country != usual_country`
- Calculating `unusual_hour` directly from the login timestamp
- Calculating `no_mfa` directly from the MFA fields
- Calculating `new_device` by comparing the login device to the user’s known device history
- Calculating `impossible_travel` by comparing previous and current login locations and timestamps
- Adding geographic distance calculations between cities or countries
- Adding more user-specific behavior patterns over time

These improvements would make the dataset more realistic and make the model stronger for final presentation.

## Summary

The current dataset is a **Version 1 synthetic dataset**. It uses user profiles and scenario-based attack simulation to create realistic login-security data. While it is not fully equivalent to real enterprise login data, it is strong enough to support the early stages of this project, including validation, preprocessing, risk scoring, machine learning, optimization, and dashboard development.