"""
HealthPal Data Layer
====================
Simulates a database interface backed by local CSV files.
Each function mirrors what a real DB query would look like,
so swapping in SQLAlchemy / REST calls later is minimal work.

Schema
------
users.csv            → users table
vitals.csv           → vitals (BP, glucose, HR per timestamp)
medications.csv      → medications master list per user
med_logs.csv         → medication intake log (taken / missed / skipped)
lab_results.csv      → lab test results per user
community_posts.csv  → community feed posts
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ── internal helpers ──────────────────────────────────────────────────────────

def _path(f): return os.path.join(DATA_DIR, f)

def _read(filename: str) -> pd.DataFrame:
    p = _path(filename)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

def _write(filename: str, df: pd.DataFrame):
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(_path(filename), index=False)


# ── seed functions ────────────────────────────────────────────────────────────

def _seed_users():
    _write("users.csv", pd.DataFrame([{
        "user_id": "U001", "name": "Sarah Chen", "age": 58,
        "gender": "Female", "email": "sarah.chen@example.com",
        "conditions": "Type 2 Diabetes|Hypertension|Dyslipidemia",
        "avatar_emoji": "👩", "created_at": "2024-01-01",
        "password_hash": "demo",   # placeholder – real auth uses bcrypt
    }]))

def _seed_vitals():
    rows, base = [], datetime(2025, 3, 7)
    for i in range(7):
        for hour in [7, 19]:
            ts = base + timedelta(days=i, hours=hour)
            rows.append({
                "record_id": f"V{len(rows)+1:04d}", "user_id": "U001",
                "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
                "systolic": random.randint(125, 145),
                "diastolic": random.randint(80, 92),
                "heart_rate": random.randint(68, 82),
                "glucose": round(random.uniform(5.0, 7.2), 1),
                "weight_kg": round(random.uniform(72.0, 73.5), 1),
                "notes": "",
            })
    _write("vitals.csv", pd.DataFrame(rows))

def _seed_medications():
    _write("medications.csv", pd.DataFrame([
        {"med_id": "M001", "user_id": "U001", "name": "Metformin",
         "condition": "Type 2 Diabetes", "dose": "1000mg", "frequency": "2x daily",
         "schedule": "08:00|20:00",
         "instructions": "Take with meals to reduce stomach upset", "active": True},
        {"med_id": "M002", "user_id": "U001", "name": "Lisinopril",
         "condition": "Hypertension", "dose": "10mg", "frequency": "1x daily",
         "schedule": "08:00",
         "instructions": "Take in the morning. May cause dizziness.", "active": True},
        {"med_id": "M003", "user_id": "U001", "name": "Atorvastatin",
         "condition": "Dyslipidemia", "dose": "40mg", "frequency": "1x daily at night",
         "schedule": "21:00",
         "instructions": "Take in the evening. Avoid grapefruit juice.", "active": True},
    ]))

def _seed_med_logs():
    rows, base = [], datetime(2025, 3, 7)
    schedule = [("M001","08:00"),("M001","20:00"),("M002","08:00"),("M003","21:00")]
    for i in range(7):
        day = (base + timedelta(days=i)).strftime("%Y-%m-%d")
        for med_id, t in schedule:
            status = "taken" if random.random() > 0.15 else "missed"
            rows.append({
                "log_id": f"L{len(rows)+1:04d}", "user_id": "U001", "med_id": med_id,
                "scheduled_at": f"{day} {t}", "status": status,
                "logged_at": f"{day} {t}" if status == "taken" else "",
            })
    _write("med_logs.csv", pd.DataFrame(rows))

def _seed_lab_results():
    _write("lab_results.csv", pd.DataFrame([
        {"lab_id": "LAB001", "user_id": "U001", "test_name": "Lipid Panel",
         "value": "LDL 3.8", "unit": "mmol/L", "reference_range": "< 3.4",
         "status": "Above Range", "tested_at": "2025-02-28"},
        {"lab_id": "LAB002", "user_id": "U001", "test_name": "HbA1c",
         "value": "7.1", "unit": "%", "reference_range": "< 7.0",
         "status": "Above Range", "tested_at": "2025-02-28"},
        {"lab_id": "LAB003", "user_id": "U001", "test_name": "Creatinine",
         "value": "82", "unit": "μmol/L", "reference_range": "45–90",
         "status": "On Track", "tested_at": "2025-02-28"},
    ]))

def _seed_community_posts():
    posts = [
        {"post_id": "P001", "author_id": "EXT002", "author_name": "Michael T.",
         "author_avatar": "👨", "condition_tag": "Type 2 Diabetes",
         "content": "Just got my HbA1c results back – down to 6.8%! Six months of consistent meal prep and walking 20 mins after dinner made all the difference. Don't give up! 💪",
         "likes": 34, "comments": 8, "posted_at": "2025-03-13 09:15"},
        {"post_id": "P002", "author_id": "EXT003", "author_name": "Linda W.",
         "author_avatar": "👩‍🦳", "condition_tag": "Hypertension",
         "content": "Anyone else struggle with remembering evening meds? I started putting my pill organizer next to my toothbrush – now I never miss it! Small habits = big changes.",
         "likes": 52, "comments": 14, "posted_at": "2025-03-13 14:30"},
        {"post_id": "P003", "author_id": "EXT004", "author_name": "James R.",
         "author_avatar": "🧑", "condition_tag": "Dyslipidemia",
         "content": "Week 3 of the low-saturated-fat diet. My LDL dropped from 4.2 to 3.6 already. My cardiologist was impressed. Sharing the meal plan in comments if anyone wants it!",
         "likes": 61, "comments": 22, "posted_at": "2025-03-12 18:45"},
        {"post_id": "P004", "author_id": "EXT005", "author_name": "Priya N.",
         "author_avatar": "👩‍⚕️", "condition_tag": "Type 2 Diabetes",
         "content": "Question for the community: does anyone else notice their fasting glucose spiking after a bad night of sleep? My CGM shows a clear pattern. Would love to hear your experiences!",
         "likes": 27, "comments": 19, "posted_at": "2025-03-12 08:00"},
        {"post_id": "P005", "author_id": "EXT006", "author_name": "Robert K.",
         "author_avatar": "👴", "condition_tag": "Hypertension",
         "content": "Celebrated my 1-year streak of keeping BP under 130/85 today! Reduced sodium, daily 30-min walks, and meditation. My doctor called it remarkable. Age 71, still going strong!",
         "likes": 88, "comments": 31, "posted_at": "2025-03-11 20:10"},
        {"post_id": "P006", "author_id": "EXT007", "author_name": "Fatima A.",
         "author_avatar": "🧕", "condition_tag": "Type 2 Diabetes",
         "content": "Ramadan and diabetes management – it IS possible. My diabetes nurse and I worked out an adjusted schedule. Happy to share tips with anyone navigating intermittent fasting with T2D.",
         "likes": 45, "comments": 17, "posted_at": "2025-03-11 11:30"},
        {"post_id": "P007", "author_id": "EXT008", "author_name": "Chen Wei",
         "author_avatar": "🧑‍💻", "condition_tag": "Dyslipidemia",
         "content": "For those on statins: talk to your doctor about CoQ10 supplementation. After adding it I noticed a significant reduction in muscle aches. Always consult before adding supplements!",
         "likes": 39, "comments": 12, "posted_at": "2025-03-10 16:00"},
        {"post_id": "P008", "author_id": "EXT009", "author_name": "María G.",
         "author_avatar": "👩‍🦱", "condition_tag": "Hypertension",
         "content": "White coat syndrome is real. My home readings are always 10-15 points lower than at the clinic. My doctor now relies on my home log instead. Track your own data – knowledge is power!",
         "likes": 56, "comments": 9, "posted_at": "2025-03-10 10:20"},
    ]
    _write("community_posts.csv", pd.DataFrame(posts))


def ensure_data_exists():
    """Call at app startup – creates all CSV files if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    for filename, seeder in [
        ("users.csv",           _seed_users),
        ("vitals.csv",          _seed_vitals),
        ("medications.csv",     _seed_medications),
        ("med_logs.csv",        _seed_med_logs),
        ("lab_results.csv",     _seed_lab_results),
        ("community_posts.csv", _seed_community_posts),
    ]:
        if not os.path.exists(_path(filename)):
            seeder()


# ── PUBLIC API  ───────────────────────────────────────────────────────────────

def get_user(user_id: str = "U001") -> dict:
    df = _read("users.csv")
    row = df[df["user_id"] == user_id]
    if row.empty:
        return {}
    r = row.iloc[0].to_dict()
    r["conditions"] = r["conditions"].split("|") if r.get("conditions") else []
    return r

def authenticate_user(email: str, password: str):
    """Returns user dict if credentials match, else None. (Demo: password_hash = 'demo')"""
    df = _read("users.csv")
    row = df[(df["email"] == email) & (df["password_hash"] == password)]
    if row.empty:
        return None
    r = row.iloc[0].to_dict()
    r["conditions"] = r["conditions"].split("|") if r.get("conditions") else []
    return r

def update_user(user_id: str, **fields) -> bool:
    try:
        df = _read("users.csv")
        for k, v in fields.items():
            if k == "conditions" and isinstance(v, list):
                v = "|".join(v)
            df.loc[df["user_id"] == user_id, k] = v
        _write("users.csv", df)
        return True
    except Exception:
        return False

def get_vitals(user_id: str = "U001", days: int = 7) -> pd.DataFrame:
    df = _read("vitals.csv")
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[df["user_id"] == user_id].sort_values("timestamp")
    cutoff = df["timestamp"].max() - timedelta(days=days)
    return df[df["timestamp"] >= cutoff].reset_index(drop=True)

def get_latest_vitals(user_id: str = "U001") -> dict:
    df = get_vitals(user_id, days=30)
    return df.iloc[-1].to_dict() if not df.empty else {}

def get_medications(user_id: str = "U001", active_only: bool = True) -> pd.DataFrame:
    df = _read("medications.csv")
    if df.empty:
        return df
    df = df[df["user_id"] == user_id]
    if active_only:
        df = df[df["active"] == True]
    return df.reset_index(drop=True)

def get_today_med_status(user_id: str = "U001") -> dict:
    logs = _read("med_logs.csv")
    if logs.empty:
        return {"taken": 0, "total": 0, "next_reminder": "--"}
    logs["scheduled_at"] = pd.to_datetime(logs["scheduled_at"], errors="coerce")
    today = datetime.now().date()
    today_logs = logs[(logs["user_id"] == user_id) & (logs["scheduled_at"].dt.date == today)]
    if today_logs.empty:
        last_day = logs[logs["user_id"] == user_id]["scheduled_at"].dt.date.max()
        today_logs = logs[(logs["user_id"] == user_id) & (logs["scheduled_at"].dt.date == last_day)]
    taken = int((today_logs["status"] == "taken").sum())
    total = len(today_logs)
    pending = today_logs[today_logs["status"] != "taken"]
    next_reminder = pending["scheduled_at"].min().strftime("%I:%M %p") if not pending.empty else "All done!"
    return {"taken": taken, "total": total, "next_reminder": next_reminder}

def get_lab_results(user_id: str = "U001") -> pd.DataFrame:
    df = _read("lab_results.csv")
    return df[df["user_id"] == user_id].reset_index(drop=True) if not df.empty else df

def get_community_posts(limit: int = 20) -> pd.DataFrame:
    df = _read("community_posts.csv")
    if df.empty:
        return df
    df["posted_at"] = pd.to_datetime(df["posted_at"])
    return df.sort_values("posted_at", ascending=False).head(limit).reset_index(drop=True)

def like_post(post_id: str) -> bool:
    try:
        df = _read("community_posts.csv")
        df.loc[df["post_id"] == post_id, "likes"] += 1
        _write("community_posts.csv", df)
        return True
    except Exception:
        return False

def add_vitals_record(user_id: str, systolic: int, diastolic: int,
                      heart_rate: int, glucose: float, weight_kg: float = None, notes: str = "") -> bool:
    try:
        df = _read("vitals.csv")
        new_id = f"V{len(df)+1:04d}" if not df.empty else "V0001"
        new_row = pd.DataFrame([{
            "record_id": new_id, "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "systolic": systolic, "diastolic": diastolic,
            "heart_rate": heart_rate, "glucose": glucose,
            "weight_kg": weight_kg or "", "notes": notes,
        }])
        _write("vitals.csv", pd.concat([df, new_row], ignore_index=True))
        return True
    except Exception:
        return False

def log_medication(user_id: str, med_id: str, status: str = "taken") -> bool:
    try:
        df = _read("med_logs.csv")
        new_id = f"L{len(df)+1:04d}" if not df.empty else "L0001"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_row = pd.DataFrame([{
            "log_id": new_id, "user_id": user_id, "med_id": med_id,
            "scheduled_at": now, "status": status, "logged_at": now,
        }])
        _write("med_logs.csv", pd.concat([df, new_row], ignore_index=True))
        return True
    except Exception:
        return False
