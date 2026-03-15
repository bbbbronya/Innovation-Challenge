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
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MEDICATION_PLAN_FILE = "medication_plan.csv"
MEDICATION_PLAN_COLUMNS = [
    "medication_id",
    "user_id",
    "medication_name",
    "dosage",
    "time_of_day",
    "frequency_days",
    "start_date",
    "notes",
]
MEDICATION_LOG_FILE = "medication_logs.csv"
MEDICATION_LOG_COLUMNS = [
    "log_id",
    "user_id",
    "medication_id",
    "scheduled_date",
    "scheduled_time",
    "status",
    "logged_at",
]

# ── internal helpers ──────────────────────────────────────────────────────────

def _path(f): return os.path.join(DATA_DIR, f)

def _read(filename: str) -> pd.DataFrame:
    p = _path(filename)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

def _write(filename: str, df: pd.DataFrame):
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(_path(filename), index=False)


def _generate_next_id(prefix: str, existing_ids: list[str], width: int = 4) -> str:
    max_num = 0
    for item_id in existing_ids:
        if not isinstance(item_id, str) or not item_id.startswith(prefix):
            continue
        try:
            max_num = max(max_num, int(item_id[len(prefix):]))
        except Exception:
            continue
    return f"{prefix}{max_num + 1:0{width}d}"


def _normalize_medication_plan_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=MEDICATION_PLAN_COLUMNS)
    out = df.copy()
    if "medication_id" not in out.columns and "med_id" in out.columns:
        out["medication_id"] = out["med_id"]
    if "medication_name" not in out.columns and "name" in out.columns:
        out["medication_name"] = out["name"]
    if "dosage" not in out.columns and "dose" in out.columns:
        out["dosage"] = out["dose"]
    if "time_of_day" not in out.columns:
        if "schedule" in out.columns:
            out["time_of_day"] = out["schedule"].astype(str).str.split("|").str[0].fillna("08:00")
        else:
            out["time_of_day"] = "08:00"
    if "frequency_days" not in out.columns:
        out["frequency_days"] = 1
    if "start_date" not in out.columns:
        out["start_date"] = datetime.now().strftime("%Y-%m-%d")
    if "notes" not in out.columns:
        out["notes"] = ""
    if "user_id" not in out.columns:
        out["user_id"] = "U001"

    out = out[MEDICATION_PLAN_COLUMNS].copy()
    out["medication_id"] = out["medication_id"].astype(str).str.strip()
    out["user_id"] = out["user_id"].astype(str).str.strip().replace("", "U001")
    out["medication_name"] = out["medication_name"].astype(str).str.strip()
    out["dosage"] = out["dosage"].astype(str).str.strip()
    out["time_of_day"] = out["time_of_day"].astype(str).str.strip().replace("", "08:00")
    out["frequency_days"] = pd.to_numeric(out["frequency_days"], errors="coerce").fillna(1).astype(int).clip(lower=1)
    out["start_date"] = out["start_date"].astype(str).str.strip().replace("", datetime.now().strftime("%Y-%m-%d"))
    out["notes"] = out["notes"].astype(str).str.strip()
    out = out[out["medication_name"] != ""].reset_index(drop=True)
    return out


def _normalize_medication_logs_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=MEDICATION_LOG_COLUMNS)
    out = df.copy()
    if "medication_id" not in out.columns and "med_id" in out.columns:
        out["medication_id"] = out["med_id"]
    if "scheduled_date" not in out.columns and "scheduled_at" in out.columns:
        dt = pd.to_datetime(out["scheduled_at"], errors="coerce")
        out["scheduled_date"] = dt.dt.strftime("%Y-%m-%d").fillna("")
    if "scheduled_time" not in out.columns and "scheduled_at" in out.columns:
        dt = pd.to_datetime(out["scheduled_at"], errors="coerce")
        out["scheduled_time"] = dt.dt.strftime("%H:%M").fillna("")
    if "user_id" not in out.columns:
        out["user_id"] = "U001"
    if "status" not in out.columns:
        out["status"] = "taken"
    if "logged_at" not in out.columns:
        out["logged_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "log_id" not in out.columns:
        out["log_id"] = [f"L{i+1:04d}" for i in range(len(out))]

    out = out[MEDICATION_LOG_COLUMNS].copy()
    out["log_id"] = out["log_id"].astype(str).str.strip()
    out["user_id"] = out["user_id"].astype(str).str.strip().replace("", "U001")
    out["medication_id"] = out["medication_id"].astype(str).str.strip()
    out["scheduled_date"] = out["scheduled_date"].astype(str).str.strip()
    out["scheduled_time"] = out["scheduled_time"].astype(str).str.strip()
    out["status"] = out["status"].astype(str).str.strip().replace("", "taken")
    out["logged_at"] = out["logged_at"].astype(str).str.strip()
    out = out[(out["medication_id"] != "") & (out["scheduled_date"] != "") & (out["scheduled_time"] != "")].reset_index(drop=True)
    return out


def _ensure_medication_plan_and_logs():
    plan_path = _path(MEDICATION_PLAN_FILE)
    logs_path = _path(MEDICATION_LOG_FILE)

    if os.path.exists(plan_path):
        plan_df = _normalize_medication_plan_df(_read(MEDICATION_PLAN_FILE))
    else:
        legacy = _read("medications.csv")
        rows = []
        if not legacy.empty:
            for _, med in legacy.iterrows():
                schedules = str(med.get("schedule", "08:00")).split("|")
                for t in schedules:
                    tm = str(t).strip() or "08:00"
                    rows.append({
                        "medication_id": str(med.get("med_id", "")).strip(),
                        "user_id": str(med.get("user_id", "U001")).strip() or "U001",
                        "medication_name": str(med.get("name", "")).strip(),
                        "dosage": str(med.get("dose", "")).strip(),
                        "time_of_day": tm,
                        "frequency_days": 1,
                        "start_date": "2025-01-01",
                        "notes": str(med.get("instructions", "")).strip(),
                    })
        plan_df = _normalize_medication_plan_df(pd.DataFrame(rows))
    _write(MEDICATION_PLAN_FILE, plan_df)

    if os.path.exists(logs_path):
        logs_df = _normalize_medication_logs_df(_read(MEDICATION_LOG_FILE))
    else:
        legacy_logs = _read("med_logs.csv")
        logs_df = _normalize_medication_logs_df(legacy_logs)
    _write(MEDICATION_LOG_FILE, logs_df)


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
    _ensure_medication_plan_and_logs()


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
    plan = _read(MEDICATION_PLAN_FILE)
    logs_new = _read(MEDICATION_LOG_FILE)
    if not plan.empty:
        today_items = get_todays_medications(user_id=user_id)
        taken = int(sum(1 for item in today_items if item.get("taken")))
        total = len(today_items)
        next_item = get_next_medication(user_id=user_id)
        next_reminder = f"{next_item['scheduled_date']} {next_item['time_of_day']}" if next_item else "All done!"
        return {"taken": taken, "total": total, "next_reminder": next_reminder}

    if not logs_new.empty:
        logs_new["scheduled_date"] = pd.to_datetime(logs_new["scheduled_date"], errors="coerce")
        today = datetime.now().date()
        today_logs = logs_new[(logs_new["user_id"] == user_id) & (logs_new["scheduled_date"].dt.date == today)]
        taken = int((today_logs["status"] == "taken").sum())
        total = len(today_logs)
        pending = today_logs[today_logs["status"] != "taken"]
        next_reminder = pending["scheduled_time"].min() if not pending.empty else "All done!"
        return {"taken": taken, "total": total, "next_reminder": next_reminder}

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

def add_community_post(author_id: str, author_name: str, author_avatar: str,
                       condition_tag: str, content: str) -> bool:
    try:
        df = _read("community_posts.csv")
        new_id = f"P{len(df)+1:03d}" if not df.empty else "P001"
        new_row = pd.DataFrame([{
            "post_id": new_id, "author_id": author_id, "author_name": author_name,
            "author_avatar": author_avatar, "condition_tag": condition_tag,
            "content": content, "likes": 0, "comments": 0,
            "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }])
        _write("community_posts.csv", pd.concat([df, new_row], ignore_index=True))
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
        plan = _read(MEDICATION_PLAN_FILE)
        if not plan.empty:
            med_row = plan[(plan["user_id"] == user_id) & (plan["medication_id"] == med_id)]
            if not med_row.empty:
                scheduled_time = str(med_row.iloc[0].get("time_of_day", datetime.now().strftime("%H:%M")))
                ok, _ = mark_medication_as_taken(
                    medication_id=med_id,
                    scheduled_date=datetime.now().strftime("%Y-%m-%d"),
                    scheduled_time=scheduled_time,
                    user_id=user_id,
                )
                return ok

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


def load_medications(user_id: str = "U001") -> list[dict]:
    df = _read(MEDICATION_PLAN_FILE)
    if df.empty:
        return []
    df = _normalize_medication_plan_df(df)
    df = df[df["user_id"] == user_id].copy()
    df = df.sort_values(["time_of_day", "medication_name"]).reset_index(drop=True)
    return df.to_dict("records")


def load_medication_logs(user_id: str = "U001") -> list[dict]:
    df = _read(MEDICATION_LOG_FILE)
    if df.empty:
        return []
    df = _normalize_medication_logs_df(df)
    return df[df["user_id"] == user_id].to_dict("records")


def add_medication_record(
    medication_name: str,
    dosage: str = "",
    time_of_day: str = "08:00",
    frequency_days: int = 1,
    start_date: str = "",
    notes: str = "",
    user_id: str = "U001",
) -> dict:
    initialize_date = start_date.strip() if isinstance(start_date, str) else ""
    if not medication_name or not medication_name.strip():
        raise ValueError("medication_name is required")
    try:
        datetime.strptime(time_of_day, "%H:%M")
    except ValueError:
        raise ValueError("time_of_day must follow HH:MM format, e.g. 08:00")
    try:
        frequency_days = int(frequency_days)
    except (TypeError, ValueError):
        raise ValueError("frequency_days must be a positive integer")
    if frequency_days <= 0:
        raise ValueError("frequency_days must be a positive integer")
    if not initialize_date:
        initialize_date = datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(initialize_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date must follow YYYY-MM-DD format, e.g. 2026-03-15")

    planner_df = _normalize_medication_plan_df(_read(MEDICATION_PLAN_FILE))
    existing_ids = planner_df["medication_id"].tolist() if not planner_df.empty else []
    med_id = _generate_next_id("M", existing_ids)
    new_row = pd.DataFrame([{
        "medication_id": med_id,
        "user_id": user_id,
        "medication_name": medication_name.strip(),
        "dosage": (dosage or "").strip(),
        "time_of_day": time_of_day,
        "frequency_days": frequency_days,
        "start_date": initialize_date,
        "notes": (notes or "").strip(),
    }])
    planner_df = pd.concat([planner_df, new_row], ignore_index=True)
    _write(MEDICATION_PLAN_FILE, _normalize_medication_plan_df(planner_df))

    legacy_df = _read("medications.csv")
    if legacy_df.empty:
        legacy_df = pd.DataFrame(columns=["med_id", "user_id", "name", "condition", "dose", "frequency", "schedule", "instructions", "active"])
    legacy_row = pd.DataFrame([{
        "med_id": med_id,
        "user_id": user_id,
        "name": medication_name.strip(),
        "condition": "General",
        "dose": (dosage or "").strip(),
        "frequency": f"Every {frequency_days} day(s)",
        "schedule": time_of_day,
        "instructions": (notes or "").strip(),
        "active": True,
    }])
    _write("medications.csv", pd.concat([legacy_df, legacy_row], ignore_index=True))

    return new_row.iloc[0].to_dict()


def delete_medication(medication_id: str, user_id: str = "U001") -> tuple[bool, str]:
    planner_df = _normalize_medication_plan_df(_read(MEDICATION_PLAN_FILE))
    before = len(planner_df)
    planner_df = planner_df[~((planner_df["medication_id"] == medication_id) & (planner_df["user_id"] == user_id))].reset_index(drop=True)
    if len(planner_df) == before:
        return False, "Medication not found."
    _write(MEDICATION_PLAN_FILE, planner_df)

    log_df = _normalize_medication_logs_df(_read(MEDICATION_LOG_FILE))
    if not log_df.empty:
        log_df = log_df[~((log_df["medication_id"] == medication_id) & (log_df["user_id"] == user_id))].reset_index(drop=True)
        _write(MEDICATION_LOG_FILE, log_df)

    legacy_df = _read("medications.csv")
    if not legacy_df.empty and "med_id" in legacy_df.columns:
        legacy_df = legacy_df[~((legacy_df["med_id"] == medication_id) & (legacy_df["user_id"] == user_id))].reset_index(drop=True)
        _write("medications.csv", legacy_df)

    return True, "Medication deleted successfully."


def is_taken_for_schedule(
    medication_id: str,
    scheduled_date: str,
    scheduled_time: str,
    user_id: str = "U001",
) -> bool:
    logs_df = _normalize_medication_logs_df(_read(MEDICATION_LOG_FILE))
    if logs_df.empty:
        return False
    hit = logs_df[
        (logs_df["user_id"] == user_id)
        & (logs_df["medication_id"] == medication_id)
        & (logs_df["scheduled_date"] == scheduled_date)
        & (logs_df["scheduled_time"] == scheduled_time)
        & (logs_df["status"] == "taken")
    ]
    return not hit.empty


def mark_medication_as_taken(
    medication_id: str,
    scheduled_date: str,
    scheduled_time: str,
    user_id: str = "U001",
) -> tuple[bool, str]:
    if is_taken_for_schedule(medication_id, scheduled_date, scheduled_time, user_id=user_id):
        return False, "This medication is already marked as taken."

    logs_df = _normalize_medication_logs_df(_read(MEDICATION_LOG_FILE))
    existing_ids = logs_df["log_id"].tolist() if not logs_df.empty else []
    log_id = _generate_next_id("L", existing_ids)
    new_row = pd.DataFrame([{
        "log_id": log_id,
        "user_id": user_id,
        "medication_id": medication_id,
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "status": "taken",
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }])
    logs_df = pd.concat([logs_df, new_row], ignore_index=True)
    _write(MEDICATION_LOG_FILE, _normalize_medication_logs_df(logs_df))
    return True, "Medication marked as taken."


def _is_due_on_date(record: dict, target_date: datetime.date) -> bool:
    try:
        start = datetime.strptime(str(record.get("start_date", "")), "%Y-%m-%d").date()
        freq = max(1, int(record.get("frequency_days", 1)))
    except Exception:
        return False
    if target_date < start:
        return False
    return (target_date - start).days % freq == 0


def get_todays_medications(user_id: str = "U001", current_date=None) -> list[dict]:
    target_date = current_date if current_date is not None else datetime.now().date()
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    scheduled_date = target_date.strftime("%Y-%m-%d")

    rows = []
    for record in load_medications(user_id=user_id):
        if _is_due_on_date(record, target_date):
            item = dict(record)
            item["scheduled_date"] = scheduled_date
            item["taken"] = is_taken_for_schedule(
                medication_id=item["medication_id"],
                scheduled_date=scheduled_date,
                scheduled_time=item["time_of_day"],
                user_id=user_id,
            )
            rows.append(item)
    rows.sort(key=lambda x: x.get("time_of_day", ""))
    return rows


def get_due_medications(user_id: str = "U001", current_date=None, current_time=None) -> list[dict]:
    target_date = current_date if current_date is not None else datetime.now().date()
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    if current_time is None:
        target_time = datetime.now().strftime("%H:%M")
    else:
        target_time = current_time.strftime("%H:%M") if hasattr(current_time, "strftime") else str(current_time)
    scheduled_date = target_date.strftime("%Y-%m-%d")

    due_rows = []
    for record in load_medications(user_id=user_id):
        if _is_due_on_date(record, target_date) and str(record.get("time_of_day", "")) == target_time:
            item = dict(record)
            item["scheduled_date"] = scheduled_date
            item["taken"] = is_taken_for_schedule(
                medication_id=item["medication_id"],
                scheduled_date=scheduled_date,
                scheduled_time=item["time_of_day"],
                user_id=user_id,
            )
            due_rows.append(item)
    due_rows.sort(key=lambda x: x.get("time_of_day", ""))
    return due_rows


def get_next_medication(user_id: str = "U001", current_date=None, current_time=None) -> Optional[dict]:
    target_date = current_date if current_date is not None else datetime.now().date()
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

    if current_time is None:
        now_dt = datetime.now()
    elif hasattr(current_time, "hour"):
        now_dt = datetime.combine(target_date, current_time)
    else:
        parsed = datetime.strptime(str(current_time), "%H:%M").time()
        now_dt = datetime.combine(target_date, parsed)

    records = load_medications(user_id=user_id)
    for day_offset in range(0, 8):
        candidate_date = target_date + timedelta(days=day_offset)
        scheduled_date = candidate_date.strftime("%Y-%m-%d")
        candidates = []
        for record in records:
            if not _is_due_on_date(record, candidate_date):
                continue
            try:
                tm = datetime.strptime(str(record.get("time_of_day", "")), "%H:%M").time()
                scheduled_dt = datetime.combine(candidate_date, tm)
            except Exception:
                continue
            if scheduled_dt >= now_dt:
                item = dict(record)
                item["scheduled_date"] = scheduled_date
                item["taken"] = is_taken_for_schedule(
                    medication_id=item["medication_id"],
                    scheduled_date=scheduled_date,
                    scheduled_time=item["time_of_day"],
                    user_id=user_id,
                )
                candidates.append((scheduled_dt, item))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
    return None
