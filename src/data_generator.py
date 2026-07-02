import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def generate_ip_address():
    """Generate a synthetic IP address."""
    return f"{random.randint(10, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def create_user_profiles(num_users=250):
    """Create realistic user profiles with usual country, city, device, browser, and MFA behavior."""

    countries_and_cities = {
        "United States": ["New York", "Edison", "Chicago", "San Francisco", "Boston"],
        "Canada": ["Toronto", "Vancouver"],
        "United Kingdom": ["London", "Manchester"],
        "India": ["Mumbai", "Delhi", "Bangalore"],
        "Germany": ["Berlin", "Munich"],
        "Brazil": ["São Paulo", "Rio de Janeiro"],
    }

    device_types = ["Laptop", "Desktop", "Mobile", "Tablet"]
    browsers = ["Chrome", "Safari", "Edge", "Firefox"]

    users = {}

    for i in range(1, num_users + 1):
        user_id = f"U{str(i).zfill(4)}"

        usual_country = random.choices(
            list(countries_and_cities.keys()),
            weights=[65, 8, 7, 8, 6, 6]
        )[0]

        usual_city = random.choice(countries_and_cities[usual_country])

        primary_device = random.choices(
            device_types,
            weights=[55, 20, 20, 5]
        )[0]

        primary_browser = random.choices(
            browsers,
            weights=[60, 18, 12, 10]
        )[0]

        mfa_adoption = random.choices(
            [True, False],
            weights=[75, 25]
        )[0]

        users[user_id] = {
            "usual_country": usual_country,
            "usual_city": usual_city,
            "primary_device": primary_device,
            "primary_browser": primary_browser,
            "mfa_adoption": mfa_adoption,
        }

    return users, countries_and_cities


def choose_attack_type():
    """Choose whether the login is normal or one of several suspicious event types."""

    return random.choices(
        [
            "Normal",
            "Brute Force",
            "Credential Stuffing",
            "Impossible Travel",
            "New Device Login",
            "Suspicious IP Login",
            "Foreign Login",
            "Unusual Hour Login",
            "MFA Fatigue",
        ],
        weights=[82, 4, 3, 2, 3, 2, 2, 1, 1]
    )[0]


def generate_login_data(num_records=10000):
    """Generate realistic synthetic login event data."""

    user_profiles, countries_and_cities = create_user_profiles()
    users = list(user_profiles.keys())

    records = []
    start_date = datetime(2026, 7, 1)

    suspicious_ips = [generate_ip_address() for _ in range(25)]

    for i in range(1, num_records + 1):
        user_id = random.choice(users)
        profile = user_profiles[user_id]

        attack_type = choose_attack_type()

        # Normal login time is usually during the day.
        if attack_type == "Unusual Hour Login":
            hour = random.choice([0, 1, 2, 3, 4])
        else:
            hour = random.choices(
                list(range(24)),
                weights=[
                    1, 1, 1, 1, 1, 2,
                    4, 7, 9, 10, 10, 9,
                    8, 8, 8, 8, 7, 7,
                    6, 5, 4, 3, 2, 1
                ]
            )[0]

        timestamp = start_date + timedelta(
            days=random.randint(0, 30),
            hours=hour,
            minutes=random.randint(0, 59)
        )

        # Default normal behavior
        country = profile["usual_country"]
        city = profile["usual_city"]
        device_type = profile["primary_device"]
        browser = profile["primary_browser"]
        ip_address = generate_ip_address()
        failed_attempts = random.choices([0, 1, 2], weights=[75, 20, 5])[0]
        mfa_used = profile["mfa_adoption"]
        mfa_type = random.choice(["SMS", "Authenticator App", "Email Code"]) if mfa_used else "None"
        new_device = False
        foreign_login = False
        impossible_travel = False
        suspicious_ip = False
        mfa_failed_attempts = 0

        # Modify fields based on attack type
        if attack_type == "Brute Force":
            failed_attempts = random.randint(5, 10)
            new_device = random.choice([True, False])
            mfa_used = random.choices([True, False], weights=[35, 65])[0]
            mfa_type = random.choice(["SMS", "Authenticator App", "Email Code"]) if mfa_used else "None"

        elif attack_type == "Credential Stuffing":
            failed_attempts = random.randint(3, 8)
            ip_address = random.choice(suspicious_ips)
            suspicious_ip = True
            mfa_used = random.choices([True, False], weights=[30, 70])[0]
            mfa_type = random.choice(["SMS", "Authenticator App", "Email Code"]) if mfa_used else "None"

        elif attack_type == "Impossible Travel":
            foreign_country_options = [c for c in countries_and_cities.keys() if c != profile["usual_country"]]
            country = random.choice(foreign_country_options)
            city = random.choice(countries_and_cities[country])
            foreign_login = True
            impossible_travel = True
            failed_attempts = random.randint(1, 5)

        elif attack_type == "New Device Login":
            device_type = random.choice(["Laptop", "Desktop", "Mobile", "Tablet"])
            browser = random.choice(["Chrome", "Safari", "Edge", "Firefox"])
            new_device = True
            failed_attempts = random.randint(0, 4)

        elif attack_type == "Suspicious IP Login":
            ip_address = random.choice(suspicious_ips)
            suspicious_ip = True
            failed_attempts = random.randint(1, 6)

        elif attack_type == "Foreign Login":
            foreign_country_options = [c for c in countries_and_cities.keys() if c != profile["usual_country"]]
            country = random.choice(foreign_country_options)
            city = random.choice(countries_and_cities[country])
            foreign_login = True
            failed_attempts = random.randint(0, 4)

        elif attack_type == "MFA Fatigue":
            mfa_used = True
            mfa_type = random.choice(["SMS", "Authenticator App"])
            mfa_failed_attempts = random.randint(3, 8)
            failed_attempts = random.randint(1, 4)

        unusual_hour = timestamp.hour < 5

        login_success = random.choices(
            [True, False],
            weights=[85, 15] if attack_type == "Normal" else [45, 55]
        )[0]

        is_suspicious = attack_type != "Normal"

        record = {
            "login_id": f"L{str(i).zfill(6)}",
            "user_id": user_id,
            "timestamp": timestamp,
            "login_hour": timestamp.hour,
            "day_of_week": timestamp.strftime("%A"),
            "country": country,
            "city": city,
            "usual_country": profile["usual_country"],
            "usual_city": profile["usual_city"],
            "device_type": device_type,
            "browser": browser,
            "ip_address": ip_address,
            "failed_attempts": failed_attempts,
            "mfa_used": mfa_used,
            "mfa_type": mfa_type,
            "mfa_failed_attempts": mfa_failed_attempts,
            "new_device": new_device,
            "foreign_login": foreign_login,
            "unusual_hour": unusual_hour,
            "impossible_travel": impossible_travel,
            "suspicious_ip": suspicious_ip,
            "login_success": login_success,
            "attack_type": attack_type,
            "is_suspicious": int(is_suspicious),
        }

        records.append(record)

    return pd.DataFrame(records)


def save_login_data():
    """Generate and save 10,000 realistic login records."""

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "login_events.csv"

    df = generate_login_data(10000)
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} login records.")
    print(f"Saved file to: {output_path}")
    print()
    print("Attack type distribution:")
    print(df["attack_type"].value_counts())
    print()
    print("Suspicious login distribution:")
    print(df["is_suspicious"].value_counts())


if __name__ == "__main__":
    save_login_data()