import random
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def generate_ip_address():
    """Generate a synthetic IP address."""
    return f"{random.randint(10, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def generate_login_data(num_records=500):
    """Generate synthetic login event data."""

    users = [f"U{str(i).zfill(3)}" for i in range(1, 101)]

    countries = ["United States", "Canada", "United Kingdom", "India", "Germany", "Brazil"]
    cities = {
        "United States": ["New York", "Edison", "Chicago", "San Francisco"],
        "Canada": ["Toronto", "Vancouver"],
        "United Kingdom": ["London", "Manchester"],
        "India": ["Mumbai", "Delhi", "Bangalore"],
        "Germany": ["Berlin", "Munich"],
        "Brazil": ["São Paulo", "Rio de Janeiro"]
    }

    device_types = ["Laptop", "Desktop", "Mobile", "Tablet"]
    browsers = ["Chrome", "Safari", "Edge", "Firefox"]
    mfa_types = ["None", "SMS", "Authenticator App", "Email Code"]

    records = []

    start_date = datetime(2026, 7, 1)

    for i in range(1, num_records + 1):
        user_id = random.choice(users)

        timestamp = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        country = random.choice(countries)
        city = random.choice(cities[country])

        device_type = random.choice(device_types)
        browser = random.choice(browsers)
        ip_address = generate_ip_address()

        failed_attempts = random.choices(
            [0, 1, 2, 3, 4, 5, 6, 7],
            weights=[45, 25, 12, 7, 4, 3, 2, 2]
        )[0]

        mfa_used = random.choice([True, False])
        mfa_type = random.choice(mfa_types) if mfa_used else "None"

        new_device = random.choices([True, False], weights=[20, 80])[0]
        foreign_login = random.choices([True, False], weights=[15, 85])[0]
        unusual_hour = timestamp.hour < 5 or timestamp.hour > 23
        impossible_travel = random.choices([True, False], weights=[5, 95])[0]
        suspicious_ip = random.choices([True, False], weights=[10, 90])[0]

        login_success = random.choices([True, False], weights=[85, 15])[0]

        is_suspicious = (
            failed_attempts >= 5
            or suspicious_ip
            or impossible_travel
            or (new_device and not mfa_used)
            or (foreign_login and failed_attempts >= 3)
        )

        if not is_suspicious:
            attack_type = "Normal"
        elif failed_attempts >= 5:
            attack_type = "Brute Force"
        elif suspicious_ip:
            attack_type = "Suspicious IP Login"
        elif impossible_travel:
            attack_type = "Impossible Travel"
        elif new_device:
            attack_type = "New Device Login"
        elif foreign_login:
            attack_type = "Foreign Login"
        else:
            attack_type = "Unusual Login"

        record = {
            "login_id": f"L{str(i).zfill(6)}",
            "user_id": user_id,
            "timestamp": timestamp,
            "login_hour": timestamp.hour,
            "day_of_week": timestamp.strftime("%A"),
            "country": country,
            "city": city,
            "device_type": device_type,
            "browser": browser,
            "ip_address": ip_address,
            "failed_attempts": failed_attempts,
            "mfa_used": mfa_used,
            "mfa_type": mfa_type,
            "new_device": new_device,
            "foreign_login": foreign_login,
            "unusual_hour": unusual_hour,
            "impossible_travel": impossible_travel,
            "suspicious_ip": suspicious_ip,
            "login_success": login_success,
            "attack_type": attack_type,
            "is_suspicious": int(is_suspicious)
        }

        records.append(record)

    return pd.DataFrame(records)


def save_login_data():
    """Generate and save 500 login records to data/raw."""

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "login_events_sample.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = generate_login_data(500)
    df.to_csv(output_path, index=False)

    print(f"Generated {len(df)} login records.")
    print(f"Saved file to: {output_path}")


if __name__ == "__main__":
    save_login_data()