# Threat Model

This document explains the login security threats that the Smart Security Optimizer is designed to detect. Each threat is matched to login-data signals that can be used by the risk scoring engine and machine-learning model.

## 1. Brute Force Attack

A brute force attack happens when an attacker repeatedly guesses a user's password until they get it right.

In login data, this may appear as many failed login attempts for the same user in a short period of time.

Fields to check:
- failed_attempts
- user_id
- timestamp
- login_success
- ip_address

Risk impact:
High risk if failed_attempts is 5 or more.

## 2. Credential Stuffing

Credential stuffing happens when attackers use stolen usernames and passwords from other websites and try them on many accounts.

In login data, this may appear as one IP address attempting logins for many different users.

Fields to check:
- ip_address
- user_id
- failed_attempts
- timestamp
- login_success

Risk impact:
High risk if one IP address targets many users.

## 3. Impossible Travel

Impossible travel happens when a user appears to log in from two far-away locations in a time period that is not physically possible.

For example, a user logs in from New York and then 30 minutes later logs in from London.

Fields to check:
- user_id
- timestamp
- country
- city
- previous_login_country
- previous_login_time

Risk impact:
Critical risk if the travel pattern is impossible.

## 4. New Device Login

A new device login happens when a user signs in from a device they have not used before.

This is not always dangerous, but it becomes suspicious when combined with no MFA, foreign location, or failed attempts.

Fields to check:
- user_id
- device_type
- browser
- new_device
- mfa_used

Risk impact:
Medium risk by itself, higher risk when combined with other factors.

## 5. Unusual Login Hours

Unusual login hours happen when a login occurs at a time that is uncommon, such as very late at night.

This does not automatically mean an attack, but it can be suspicious when combined with a new device, failed attempts, or no MFA.

Fields to check:
- timestamp
- login_hour
- user_id

Risk impact:
Low to medium risk depending on other signals.

## 6. Suspicious IP Address

A suspicious IP address is an IP that appears repeatedly in risky login attempts or attacks.

Since this project uses synthetic data, the system can create a fake list of suspicious IP addresses.

Fields to check:
- ip_address
- suspicious_ip
- failed_attempts
- attack_type

Risk impact:
High risk if the IP is marked suspicious.

## 7. MFA Fatigue

MFA fatigue happens when an attacker repeatedly triggers MFA requests, hoping the user will approve one by mistake.

In login data, this may appear as repeated MFA prompts or failed MFA attempts.

Fields to check:
- mfa_used
- mfa_type
- mfa_failed_attempts
- failed_attempts
- timestamp

Risk impact:
High risk if there are repeated MFA failures or repeated prompts.