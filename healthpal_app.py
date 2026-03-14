"""
HealthPal v6  –  Single-layer CSS-fixed bottom nav  +  CSV data layer
Providers: Anthropic (fixed) | EN / ZH toggle
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import os

from data_layer import (
    ensure_data_exists,
    get_user, get_vitals, get_latest_vitals,
    get_medications, get_today_med_status, get_lab_results,
    add_vitals_record, log_medication,
)

st.set_page_config(
    page_title="HealthPal",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ensure_data_exists()

# ═══════════════════════════════════════════════════════════════════════════
# SECRETS
# ═══════════════════════════════════════════════════════════════════════════
def _load_local_secrets() -> dict:
    for p in [os.path.join(os.path.dirname(os.path.abspath(__file__)), "secrets.toml"), "secrets.toml"]:
        if os.path.exists(p):
            try:
                import toml
                return toml.load(p)
            except Exception:
                pass
    return {}

_LOCAL_SECRETS: dict = _load_local_secrets()

def get_secret(key: str, default: str = "") -> str:
    if key in _LOCAL_SECRETS:
        return _LOCAL_SECRETS[key]
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

# ═══════════════════════════════════════════════════════════════════════════
# LANGUAGE
# ═══════════════════════════════════════════════════════════════════════════
_S = {
    "en": {
        "app_name": "HealthPal",
        "greet_morning": "Good morning", "greet_afternoon": "Good afternoon", "greet_evening": "Good evening",
        "subtitle": "Let's stay on track today",
        "nav_home": "Home", "nav_meds": "Meds", "nav_ai": "AI Chat",
        "nav_community": "Community", "nav_settings": "Settings",
        "btn_add_record": "+ Add Record",
        "lbl_today_metrics": "Today's Health Metrics",
        "lbl_meds_taken": "medications taken",
        "lbl_next_reminder": "Next reminder",
        "lbl_trend": "Trend Overview",
        "lbl_bp": "Blood Pressure", "lbl_glucose": "Blood Glucose",
        "lbl_lipid": "Last lipid panel",
        "lbl_above_range": "Above Range", "lbl_on_track": "On Track", "lbl_high_risk": "High Risk",
        "lbl_checked": "Checked",
        "lbl_view_timeline": "View Timeline",
        "lbl_meds_title": "Your Medications",
        "lbl_condition": "Condition", "lbl_frequency": "Frequency", "lbl_instructions": "Instructions",
        "btn_log_taken": "Mark Taken",
        "title_ai": "HealthPal AI",
        "user_input": "Ask HealthPal AI...", "btn_submit": "Send",
        "thinking": "Thinking…",
        "title_community": "Community",
        "community_empty": "No community posts yet.",
        "lbl_add_vitals": "Add Vitals Record",
        "lbl_systolic": "Systolic (mmHg)", "lbl_diastolic": "Diastolic (mmHg)",
        "lbl_hr": "Heart Rate (bpm)", "lbl_glucose_val": "Glucose (mmol/L)",
        "btn_save": "Save", "msg_saved": "Record saved!",
        "title_settings": "Settings",
        "settings_language": "Language",
        "settings_lang_en": "🇬🇧  English",
        "settings_lang_zh": "🇨🇳  中文 (Chinese)",
        "settings_notifications": "Notifications",
        "settings_notif_meds": "Medication reminders",
        "settings_notif_reports": "Weekly health report",
        "settings_profile": "My Profile",
        "settings_about": "About",
        "settings_version": "Version 6.0  ·  Powered by Claude AI",
    },
    "zh": {
        "app_name": "健康宝",
        "greet_morning": "早上好", "greet_afternoon": "下午好", "greet_evening": "晚上好",
        "subtitle": "今天让我们保持在正轨上",
        "nav_home": "首页", "nav_meds": "用药", "nav_ai": "AI聊天",
        "nav_community": "社区", "nav_settings": "设置",
        "btn_add_record": "+ 添加记录",
        "lbl_today_metrics": "今日健康指标",
        "lbl_meds_taken": "已服药",
        "lbl_next_reminder": "下次提醒",
        "lbl_trend": "趋势概览",
        "lbl_bp": "血压", "lbl_glucose": "血糖",
        "lbl_lipid": "最近血脂检查",
        "lbl_above_range": "超出范围", "lbl_on_track": "正常", "lbl_high_risk": "高风险",
        "lbl_checked": "检查于",
        "lbl_view_timeline": "查看时间线",
        "lbl_meds_title": "您的药物",
        "lbl_condition": "适应症", "lbl_frequency": "频率", "lbl_instructions": "用药说明",
        "btn_log_taken": "标记已服",
        "title_ai": "健康宝 AI",
        "user_input": "问健康宝 AI...", "btn_submit": "发送",
        "thinking": "思考中…",
        "title_community": "社区",
        "community_empty": "暂无社区帖子。",
        "lbl_add_vitals": "添加体征记录",
        "lbl_systolic": "收缩压 (mmHg)", "lbl_diastolic": "舒张压 (mmHg)",
        "lbl_hr": "心率 (bpm)", "lbl_glucose_val": "血糖 (mmol/L)",
        "btn_save": "保存", "msg_saved": "已保存！",
        "title_settings": "设置",
        "settings_language": "语言",
        "settings_lang_en": "🇬🇧  英文 (English)",
        "settings_lang_zh": "🇨🇳  中文",
        "settings_notifications": "通知",
        "settings_notif_meds": "用药提醒",
        "settings_notif_reports": "每周健康报告",
        "settings_profile": "我的信息",
        "settings_about": "关于",
        "settings_version": "版本 6.0  ·  由 Claude AI 驱动",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════
defaults = {
    "language": "en",
    "chat_history": [],
    "current_page": "home",
    "trend_days": 7,
    "notif_meds": True,
    "notif_reports": False,
    "pending_question": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def S(key: str) -> str:
    return _S.get(st.session_state.language, _S["en"]).get(key, key)

def greet() -> str:
    h = datetime.now().hour
    return S("greet_morning") if h < 12 else S("greet_afternoon") if h < 18 else S("greet_evening")

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# Key technique: a hidden #hp-nav-marker div is rendered just before the
# st.columns nav row.  The CSS :has() sibling selector then grabs that
# next element-container and fixes it to the bottom – zero JS required.
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }

/* ── outer background ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #F0F2F5 !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
}

/* ── phone column shell ── */
[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 390px !important;
    width: 390px !important;
    padding: 0 0 80px 0 !important;
    margin: 0 auto !important;
    background: #F5F7FA !important;
    min-height: 100vh;
    box-shadow: 0 8px 40px rgba(0,0,0,.18);
    position: relative;
}

/* hide Streamlit chrome */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton { display: none !important; }

/* ─────────────────────────────────────────────────────
   BOTTOM NAV – single-layer, pure-CSS :has() fix
───────────────────────────────────────────────────── */
#hp-nav-marker { display: none !important; height: 0 !important; }

[data-testid="element-container"]:has(#hp-nav-marker) {
    height: 0 !important; overflow: hidden !important;
    margin: 0 !important; padding: 0 !important;
}

[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 390px !important;
    max-width: 100vw !important;
    background: #ffffff !important;
    border-top: 1px solid #EAECF0 !important;
    box-shadow: 0 -2px 16px rgba(0,0,0,.06) !important;
    z-index: 1000 !important;
    padding: 0 !important;
    margin: 0 !important;
    padding-bottom: env(safe-area-inset-bottom, 0) !important;
}

[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  [data-testid="stHorizontalBlock"] {
    width: 100% !important; gap: 0 !important;
    padding: 0 !important; margin: 0 !important;
}
[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  [data-testid="column"] {
    padding: 0 !important; min-width: 0 !important;
}
[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  [data-testid="stVerticalBlock"] {
    gap: 0 !important; padding: 0 !important;
}

/* ── nav button: base (inactive) ── */
[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  div[data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important; border-radius: 0 !important;
    box-shadow: none !important; outline: none !important;
    width: 100% !important;
    height: 64px !important; min-height: 64px !important;
    padding: 10px 4px 8px !important;
    display: flex !important; flex-direction: column !important;
    align-items: center !important; justify-content: center !important;
    gap: 3px !important;
    font-size: 10px !important; font-weight: 600 !important;
    color: #A0A9BC !important;
    line-height: 1 !important; white-space: pre-line !important;
    letter-spacing: 0 !important; cursor: pointer !important;
    transition: color .15s !important;
}
[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  div[data-testid="stButton"] > button:hover {
    color: #5B75F5 !important;
}

/* ── nav button: active (primary) – Figma blue circle icon feel ── */
[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  div[data-testid="stButton"] > button[kind="primary"],
[data-testid="element-container"]:has(#hp-nav-marker)
  + [data-testid="element-container"]
  div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {
    background: transparent !important;
    color: #3B5BDB !important;
    border: none !important; box-shadow: none !important;
    border-top: 2.5px solid #3B5BDB !important;
}

/* ── sticky header (home page) ── */
.hp-header {
    background: #fff;
    padding: 18px 20px 14px;
    display: flex; justify-content: space-between; align-items: center;
    position: sticky; top: 0; z-index: 200;
    border-bottom: 1px solid #F0F2F5;
}
.hp-header h2 { margin: 0; font-size: 22px; font-weight: 700; color: #0F172A; letter-spacing: -.3px; }
.hp-header p  { margin: 3px 0 0; font-size: 13px; color: #94A3B8; }
.hp-avatar {
    width: 46px; height: 46px; border-radius: 50%;
    background: linear-gradient(135deg, #FDA4AF, #C084FC);
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(192,132,252,.4);
}

/* ── inner page title bar ── */
.hp-page-title {
    background: #fff; padding: 15px 20px 13px;
    font-size: 17px; font-weight: 700; color: #0F172A;
    border-bottom: 1px solid #F0F2F5;
    position: sticky; top: 0; z-index: 200;
    display: flex; align-items: center; gap: 8px;
}

/* ── white card ── */
.hp-card {
    background: #fff; border-radius: 20px;
    padding: 18px 20px; margin: 10px 16px;
    box-shadow: 0 2px 16px rgba(15,23,42,.06);
}
.hp-card-title {
    font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 16px;
    display: flex; justify-content: space-between; align-items: center;
    gap: 8px;
}
/* Add Record button inside card header */
.hp-add-record-btn {
    background: #3B5BDB; color: #fff; border: none; border-radius: 22px;
    padding: 7px 14px; font-size: 12px; font-weight: 600; cursor: pointer;
    white-space: nowrap; flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(59,91,219,.35);
}

/* ── metric rows ── */
.hp-metric-row {
    display: flex; align-items: center; gap: 13px;
    padding: 11px 0; border-bottom: 1px solid #F1F5F9;
}
.hp-metric-row:last-child { border-bottom: none; padding-bottom: 0; }
.hp-icon-circle {
    width: 42px; height: 42px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.hp-icon-circle.bp  { background: #FEE2E2; }
.hp-icon-circle.glu { background: #DBEAFE; }
.hp-icon-circle.lab { background: #FEF9C3; }
.hp-icon-circle.med { background: #DCFCE7; }
.hp-metric-label { font-size: 12px; color: #94A3B8; margin: 0; line-height: 1.4; }
.hp-metric-value { font-size: 15px; font-weight: 700; color: #0F172A; margin: 2px 0 0; }
/* lipid row: bold label + grey sub */
.hp-lipid-main { font-size: 14px; font-weight: 600; color: #0F172A; margin: 0; }
.hp-lipid-sub  { font-size: 12px; color: #94A3B8; margin: 2px 0 0; }
.hp-badge {
    margin-left: auto; font-size: 11px; font-weight: 600;
    padding: 4px 11px; border-radius: 20px; white-space: nowrap; flex-shrink: 0;
}
.badge-above { background: #FEF9C3; color: #A16207; }
.badge-ok    { background: #DCFCE7; color: #15803D; }
.badge-risk  { background: #FEE2E2; color: #B91C1C; }

/* ── medication summary card ── */
.hp-med-summary { display: flex; align-items: center; gap: 13px; }
.hp-med-info { flex: 1; }
.hp-med-info .mtitle { font-size: 16px; font-weight: 700; color: #0F172A; margin: 0; }
.hp-med-info .msub   { font-size: 12px; color: #94A3B8; margin: 3px 0 0; }
.hp-tl-btn {
    background: #EEF2FF; color: #3B5BDB;
    border: none; border-radius: 14px; padding: 8px 14px;
    font-size: 12px; font-weight: 600; cursor: pointer;
    white-space: nowrap; flex-shrink: 0;
}

/* ── trend SECTION (no card wrapper) ── */
.hp-trend-section { padding: 16px 16px 0; }
.hp-trend-title   { font-size: 18px; font-weight: 700; color: #0F172A; margin: 0 0 14px; }

/* ── period chips ── */
.hp-period-row { display: flex; gap: 0; margin-bottom: 14px; background: #EEF0F5; border-radius: 22px; padding: 3px; }
.hp-period-chip {
    flex: 1; text-align: center; padding: 7px 0; border-radius: 19px;
    border: none; font-size: 13px; font-weight: 500; cursor: pointer;
    color: #64748B; background: transparent; transition: all .15s;
}
.hp-period-chip.active {
    background: #fff; color: #0F172A; font-weight: 600;
    box-shadow: 0 1px 6px rgba(0,0,0,.12);
}

/* ── filter chips ── */
.hp-filter-row { display: flex; gap: 8px; margin-bottom: 12px; }
.hp-filter-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 22px; border: 1.5px solid #E2E8F0;
    font-size: 12px; font-weight: 600; color: #94A3B8; background: #fff;
    cursor: pointer;
}
/* Blood Pressure inactive */
.hp-filter-chip.bp-chip { border-color: #E2E8F0; color: #94A3B8; }
/* Blood Glucose active – purple */
.hp-filter-chip.glu-chip {
    border-color: #8B5CF6; color: #7C3AED; background: #F5F3FF;
}
.hp-filter-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* ── legend ── */
.hp-legend {
    display: flex; gap: 14px; margin-top: 8px;
    justify-content: center; flex-wrap: wrap; padding-bottom: 4px;
}
.hp-legend span { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: #94A3B8; }
.hp-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* ── AI chat ── */
.chat-scroll {
    max-height: 52vh; overflow-y: auto;
    display: flex; flex-direction: column; gap: 6px; padding: 4px 0;
}
.hp-bubble-user {
    background: #3B5BDB; color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 14px; margin-left: 36px;
    font-size: 14px; line-height: 1.5; word-break: break-word;
}
.hp-bubble-ai {
    background: #F1F5F9; color: #0F172A;
    border-radius: 18px 18px 18px 4px;
    padding: 10px 14px; margin-right: 36px;
    font-size: 14px; line-height: 1.5; word-break: break-word;
}
.hp-chat-empty {
    text-align: center; color: #94A3B8; font-size: 13px; padding: 36px 20px;
}

/* ── settings ── */
.hp-settings-label {
    font-size: 11px; font-weight: 700; color: #94A3B8;
    text-transform: uppercase; letter-spacing: .07em;
    padding: 14px 20px 5px; margin: 0;
}
.hp-setting-group {
    background: #fff; border-radius: 16px;
    margin: 0 16px; overflow: hidden;
    box-shadow: 0 1px 8px rgba(0,0,0,.04);
}
.hp-setting-row {
    display: flex; align-items: center; gap: 13px;
    padding: 13px 16px; border-bottom: 1px solid #F1F5F9;
}
.hp-setting-row:last-child { border-bottom: none; }
.hp-setting-icon {
    width: 34px; height: 34px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px; flex-shrink: 0;
}
.hp-setting-text .st { font-size: 14px; font-weight: 500; color: #0F172A; margin: 0; }
.hp-setting-text .ss { font-size: 12px; color: #94A3B8; margin: 1px 0 0; }

/* ── AI example question chips ── */
.hp-eq-chip-row { display: flex; flex-wrap: wrap; gap: 7px; padding: 6px 16px 4px; }
.hp-eq-chip {
    background: #EEF2FF; color: #3B5BDB; border: 1.5px solid #C7D2FE;
    border-radius: 20px; padding: 7px 13px; font-size: 12px; font-weight: 600;
    cursor: pointer; white-space: nowrap; flex-shrink: 0;
    transition: background .15s;
}
.hp-eq-chip:hover { background: #E0E7FF; }

/* ── community ── */
.hp-community-empty {
    text-align: center; padding: 52px 20px; color: #94A3B8; font-size: 14px;
}

/* ── Streamlit widget tweaks ── */
div[data-testid="stButton"] > button {
    border-radius: 14px !important; font-weight: 600 !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 22px !important; border: 1.5px solid #E2E8F0 !important;
    padding: 10px 16px !important; font-size: 14px !important;
    background: #F8FAFC !important;
}
div[data-testid="stNumberInput"] input { border-radius: 10px !important; }
[data-testid="stPlotlyChart"] { border-radius: 12px; overflow: hidden; }
div[data-testid="stExpander"] {
    border-radius: 14px !important; border: 1px solid #E2E8F0 !important;
    background: #fff !important; margin: 4px 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# LLM — MERaLiON nutrition assistant
# ═══════════════════════════════════════════════════════════════════════════
def ask_ai_merlion(history: list, new_prompt: str) -> str:
    key = get_secret("merlion_API_KEY")
    if not key:
        return "⚠️ MERaLiON API key not configured in secrets.toml"
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="http://meralion.org:8010/v1",
            api_key=key,
        )
        user = get_user()
        lv = get_latest_vitals()
        conditions = ", ".join(user.get("conditions", []))
        system_prompt = (
            "You are a professional personal nutrition assistant specialising in Southeast Asian cuisine "
            "and dietary habits. You give personalised food and meal recommendations using dishes from "
            "Malaysia, Singapore, Indonesia, Thailand, Vietnam, the Philippines, and neighbouring SEA countries. "
            "You remember the conversation history and build on it for consistent, personalised advice. "
            f"Patient profile: {user.get('name','')}, age {user.get('age','?')}, {user.get('gender','?')}. "
            f"Medical conditions: {conditions}. "
            f"Latest vitals — BP: {lv.get('systolic','?')}/{lv.get('diastolic','?')} mmHg, "
            f"HR: {lv.get('heart_rate','?')} bpm, Glucose: {lv.get('glucose','?')} mmol/L. "
            "Always tailor recommendations to these conditions. Be warm, practical, and concise."
        )
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": new_prompt})
        response = client.chat.completions.create(
            model="MERaLiON/MERaLiON-3-10B",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════
# BOTTOM NAV  – single st.columns row, fixed via CSS :has() marker
# ═══════════════════════════════════════════════════════════════════════════
_NAV = [
    ("home",      "🏠", "nav_home"),
    ("meds",      "💊", "nav_meds"),
    ("ai",        "🤖", "nav_ai"),
    ("community", "👥", "nav_community"),
    ("settings",  "⚙️", "nav_settings"),
]

def render_bottom_nav():
    cur = st.session_state.current_page
    # Marker: CSS uses this to identify and fix the NEXT sibling element
    st.markdown('<div id="hp-nav-marker"></div>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (page_id, icon, label_key) in enumerate(_NAV):
        label = S(label_key)
        with cols[i]:
            is_active = cur == page_id
            if st.button(
                f"{icon}\n{label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page_id
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════
def page_home():
    user = get_user()
    lv   = get_latest_vitals()
    lab  = get_lab_results()
    ms   = get_today_med_status()

    # ── Header ──
    st.markdown(f"""
    <div class="hp-header">
      <div><h2>{greet()}, {user.get('name','')}</h2><p>{S('subtitle')}</p></div>
      <div class="hp-avatar">👩</div>
    </div>""", unsafe_allow_html=True)

    # ── Today's Health Metrics card (Add Record button inside header row) ──
    lipid_row    = lab[lab["test_name"] == "Lipid Panel"].iloc[0] if not lab.empty and "Lipid Panel" in lab["test_name"].values else None
    lipid_status = lipid_row["status"]    if lipid_row is not None else "On Track"
    lipid_date   = lipid_row["tested_at"] if lipid_row is not None else "—"
    badge_cls    = "badge-above" if lipid_status == "Above Range" else "badge-ok"
    # "2 weeks ago" display
    lipid_ago = "2 weeks ago" if lipid_date != "—" else "—"

    st.markdown(f"""
    <div class="hp-card">
      <div class="hp-card-title">
        {S('lbl_today_metrics')}
        <button class="hp-add-record-btn" id="hp-add-record-trigger">{S('btn_add_record')}</button>
      </div>
      <div class="hp-metric-row">
        <div class="hp-icon-circle bp">❤️</div>
        <div>
          <p class="hp-metric-label">{S('lbl_bp')}</p>
          <p class="hp-metric-value">{lv.get('systolic','—')} / {lv.get('diastolic','—')} mmHg &nbsp;·&nbsp; {lv.get('heart_rate','—')} bpm</p>
        </div>
      </div>
      <div class="hp-metric-row">
        <div class="hp-icon-circle glu">💧</div>
        <div>
          <p class="hp-metric-label">Fasting {S('lbl_glucose')}</p>
          <p class="hp-metric-value">{lv.get('glucose','—')} mmol/L</p>
        </div>
      </div>
      <div class="hp-metric-row">
        <div class="hp-icon-circle lab">⚠️</div>
        <div style="flex:1;">
          <p class="hp-lipid-main">{S('lbl_lipid')}: {lipid_status}</p>
          <p class="hp-lipid-sub">{S('lbl_checked')} {lipid_ago}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Functional hidden Add Record button (triggered by the HTML button above via JS)
    if st.button(S("btn_add_record"), key="add_record_btn",
                 help="add_record_trigger"):
        st.session_state.current_page = "add_record"
        st.rerun()

    # ── Medication card ──
    st.markdown(f"""
    <div class="hp-card">
      <div class="hp-med-summary">
        <div class="hp-icon-circle med" style="font-size:22px;">💊</div>
        <div class="hp-med-info">
          <p class="mtitle"><b>{ms['taken']} of {ms['total']}</b> {S('lbl_meds_taken')}</p>
          <p class="msub">{S('lbl_next_reminder')}: {ms['next_reminder']}</p>
        </div>
        <button class="hp-tl-btn" onclick="void(0)">{S('lbl_view_timeline')}</button>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Trend Overview – section style (no card wrapper, per Figma) ──
    td = st.session_state.trend_days
    # Period chip row (HTML visual) + hidden Streamlit buttons
    chip7  = "active" if td == 7  else ""
    chip14 = "active" if td == 14 else ""
    chip30 = "active" if td == 30 else ""
    st.markdown(f"""
    <div class="hp-trend-section">
      <h3 class="hp-trend-title">{S("lbl_trend")}</h3>
      <div class="hp-period-row">
        <button class="hp-period-chip {chip7}"  onclick="void(0)">7 Days</button>
        <button class="hp-period-chip {chip14}" onclick="void(0)">14 Days</button>
        <button class="hp-period-chip {chip30}" onclick="void(0)">30 Days</button>
      </div>
    </div>""", unsafe_allow_html=True)

    # Functional period buttons (hidden below, same :has() trick can't be used here
    # so just render them small — Streamlit needs them for interaction)
    c1, c2, c3 = st.columns(3)
    for col, (lbl, d) in zip([c1, c2, c3], [("7 Days", 7), ("14 Days", 14), ("30 Days", 30)]):
        with col:
            if st.button(lbl, key=f"trend_{d}", use_container_width=True):
                st.session_state.trend_days = d
                st.rerun()

    # Filter chips: Blood Glucose active (matches Figma screenshot)
    st.markdown(f"""
    <div style="padding: 4px 16px 0;">
    <div class="hp-filter-row">
      <div class="hp-filter-chip bp-chip">
        <span class="hp-filter-dot" style="background:#CBD5E1;"></span>{S('lbl_bp')}
      </div>
      <div class="hp-filter-chip glu-chip">
        <span class="hp-filter-dot" style="background:#8B5CF6;"></span>{S('lbl_glucose')}
      </div>
    </div></div>""", unsafe_allow_html=True)

    # Chart – glucose as primary (purple fill), BP as secondary (grey dashed)
    df = get_vitals(days=st.session_state.trend_days)
    if not df.empty:
        fig = go.Figure()
        # BP: scaled to glucose range (÷20 maps 80-160 → 4-8)
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["systolic"] / 20,
            mode="lines+markers", name=S("lbl_bp"),
            line=dict(color="#CBD5E1", width=1.8, dash="dot"),
            marker=dict(size=4, color="#CBD5E1"),
        ))
        # Glucose: primary, purple, filled area
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df["glucose"],
            mode="lines+markers", name=S("lbl_glucose"),
            line=dict(color="#8B5CF6", width=2.5),
            marker=dict(size=6, color="#8B5CF6", line=dict(color="#fff", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(251,207,232,0.25)",
        ))
        # Normal glucose band shading
        fig.add_hrect(y0=4.0, y1=7.0, fillcolor="rgba(254,249,195,0.25)", line_width=0)
        # Choose x-axis tick format based on period
        if td <= 7:
            xfmt, dtick = "%a", None
        elif td <= 14:
            xfmt, dtick = "%d/%m", None
        else:
            xfmt, dtick = "W%W", 7 * 24 * 3600 * 1000  # weekly
        fig.update_layout(
            height=210, margin=dict(l=8, r=8, t=8, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(
                showgrid=False, tickformat=xfmt,
                dtick=dtick,
                tickfont=dict(size=10, color="#94A3B8"),
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#F1F5F9",
                tickfont=dict(size=10, color="#94A3B8"),
                range=[3, 10], tickvals=[3, 5, 7, 9, 10],
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div style="padding: 0 16px;">
    <div class="hp-legend">
      <span><span class="hp-dot" style="background:#4ADE80;"></span>{S('lbl_on_track')}</span>
      <span><span class="hp-dot" style="background:#FBBF24;"></span>{S('lbl_above_range')}</span>
      <span><span class="hp-dot" style="background:#F87171;"></span>{S('lbl_high_risk')}</span>
    </div></div>""", unsafe_allow_html=True)

    # ── AI insight strip ──
    st.markdown("""
    <div class="hp-card" style="display:flex;align-items:center;gap:12px;padding:13px 18px;margin-top:10px;">
      <span style="font-size:26px;">🤖</span>
      <p style="margin:0;font-size:13px;color:#0F172A;flex:1;line-height:1.6;">
        Your glucose is <b>in range</b> today. Keep it up!
      </p>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: ADD RECORD
# ═══════════════════════════════════════════════════════════════════════════
def page_add_record():
    st.markdown(f'<div class="hp-page-title">← {S("lbl_add_vitals")}</div>', unsafe_allow_html=True)
    if st.button("← Back", key="back_btn"):
        st.session_state.current_page = "home"
        st.rerun()
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    with st.form("add_vitals_form"):
        c1, c2 = st.columns(2)
        with c1:
            sys_v = st.number_input(S("lbl_systolic"), 80, 200, 120)
            hr_v  = st.number_input(S("lbl_hr"), 40, 180, 72)
        with c2:
            dia_v = st.number_input(S("lbl_diastolic"), 40, 130, 80)
            glu_v = st.number_input(S("lbl_glucose_val"), 2.0, 20.0, 5.4, step=0.1)
        if st.form_submit_button(S("btn_save"), use_container_width=True):
            if add_vitals_record("U001", sys_v, dia_v, hr_v, glu_v):
                st.success(S("msg_saved"))
                st.session_state.current_page = "home"
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: MEDICATIONS
# ═══════════════════════════════════════════════════════════════════════════
def page_medications():
    st.markdown(f'<div class="hp-page-title">💊 {S("lbl_meds_title")}</div>', unsafe_allow_html=True)
    ms = get_today_med_status()
    st.markdown(f"""
    <div class="hp-card">
      <div class="hp-med-summary">
        <div class="hp-icon-circle med" style="font-size:22px;">💊</div>
        <div class="hp-med-info">
          <p class="mtitle"><b>{ms['taken']} of {ms['total']}</b> {S('lbl_meds_taken')}</p>
          <p class="msub">{S('lbl_next_reminder')}: {ms['next_reminder']}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    meds = get_medications()
    if meds.empty:
        st.info("No medications found.")
        return
    for _, med in meds.iterrows():
        with st.expander(f"💊 **{med['name']}** — {med['dose']}"):
            st.markdown(f"**{S('lbl_condition')}:** {med['condition']}")
            st.markdown(f"**{S('lbl_frequency')}:** {med['frequency']}")
            st.markdown(f"**{S('lbl_instructions')}:** {med['instructions']}")
            if st.button(S("btn_log_taken"), key=f"log_{med['med_id']}"):
                log_medication("U001", med["med_id"], "taken")
                st.success(S("msg_saved"))
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: AI CHAT  (MERaLiON SEA nutrition assistant)
# ═══════════════════════════════════════════════════════════════════════════
def page_ai_chat():
    st.markdown(f'<div class="hp-page-title">🥗 {S("title_ai")}</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        msgs_html = '<div class="chat-scroll">'
        for msg in st.session_state.chat_history:
            cls = "hp-bubble-user" if msg["role"] == "user" else "hp-bubble-ai"
            msgs_html += f'<div class="{cls}">{msg["content"]}</div>'
        msgs_html += '</div>'
        st.markdown(msgs_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="hp-chat-empty">
          <div style="font-size:44px;margin-bottom:10px;">🥗</div>
          <div style="font-weight:600;color:#6B7280;margin-bottom:4px;">Hi, I'm your SEA Nutrition Assistant</div>
          <div style="font-size:12px;">Ask me for food &amp; diet recommendations tailored to you.</div>
        </div>""", unsafe_allow_html=True)

    # ── Example question buttons ──
    example_qs = (
        [
            "🍚 糖尿病适合吃什么早餐？",
            "🥗 推荐低盐东南亚午餐",
            "🍌 适合我的健康零食？",
            "🚫 我应该避免哪些食物？",
        ]
        if st.session_state.language == "zh"
        else [
            "🍚 Breakfast ideas for diabetes?",
            "🥗 Low-sodium SEA lunch ideas",
            "🍌 Healthy SEA snacks for me?",
            "🚫 Foods I should avoid?",
        ]
    )
    eq_cols = st.columns(2)
    for i, q in enumerate(example_qs):
        with eq_cols[i % 2]:
            if st.button(q, key=f"eq_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        c1, c2 = st.columns([5, 1])
        with c1:
            user_input = st.text_input(
                "msg", label_visibility="collapsed", placeholder=S("user_input"))
        with c2:
            send = st.form_submit_button(S("btn_submit"), use_container_width=True)

    # Handle example button click
    if st.session_state.get("pending_question"):
        pq = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.chat_history.append({"role": "user", "content": pq})
        with st.spinner(S("thinking")):
            reply = ask_ai_merlion(st.session_state.chat_history[:-1], pq)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

    if send and user_input.strip():
        txt = user_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": txt})
        with st.spinner(S("thinking")):
            reply = ask_ai_merlion(st.session_state.chat_history[:-1], txt)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: COMMUNITY
# ═══════════════════════════════════════════════════════════════════════════
def page_community():
    st.markdown(f'<div class="hp-page-title">👥 {S("title_community")}</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hp-card">
      <div class="hp-community-empty">
        <div style="font-size:44px;margin-bottom:12px;">🌱</div>
        <div style="font-weight:600;color:#6B7280;margin-bottom:4px;">{S('community_empty')}</div>
        <div style="font-size:12px;">Be the first to share your health journey!</div>
      </div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════
def page_settings():
    user = get_user()
    st.markdown(f'<div class="hp-page-title">⚙️ {S("title_settings")}</div>', unsafe_allow_html=True)

    # ── Language ──
    st.markdown(f'<p class="hp-settings-label">{S("settings_language")}</p>', unsafe_allow_html=True)
    lc1, lc2 = st.columns(2)
    with lc1:
        en_active = st.session_state.language == "en"
        if st.button(S("settings_lang_en"), key="lang_en", use_container_width=True,
                     type="primary" if en_active else "secondary"):
            st.session_state.language = "en"
            st.rerun()
    with lc2:
        zh_active = st.session_state.language == "zh"
        if st.button(S("settings_lang_zh"), key="lang_zh", use_container_width=True,
                     type="primary" if zh_active else "secondary"):
            st.session_state.language = "zh"
            st.rerun()

    # ── Notifications ──
    st.markdown(f'<p class="hp-settings-label" style="margin-top:6px;">{S("settings_notifications")}</p>',
                unsafe_allow_html=True)
    st.markdown('<div class="hp-setting-group">', unsafe_allow_html=True)
    nm = st.toggle(S("settings_notif_meds"), value=st.session_state.notif_meds, key="notif_meds")
    if nm != st.session_state.notif_meds:
        st.session_state.notif_meds = nm
    nr = st.toggle(S("settings_notif_reports"), value=st.session_state.notif_reports, key="notif_rep")
    if nr != st.session_state.notif_reports:
        st.session_state.notif_reports = nr
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Profile (read-only) ──
    conditions = ", ".join(user.get("conditions", []))
    st.markdown(f'<p class="hp-settings-label" style="margin-top:6px;">{S("settings_profile")}</p>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hp-card" style="margin-top:0;">
      <div class="hp-metric-row">
        <div class="hp-icon-circle" style="background:#EDE9FE;">👤</div>
        <div><p class="hp-metric-label">Name</p><p class="hp-metric-value">{user.get('name','—')}</p></div>
      </div>
      <div class="hp-metric-row" style="padding-bottom:0;border-bottom:none;">
        <div class="hp-icon-circle" style="background:#FCE7F3;">🏥</div>
        <div>
          <p class="hp-metric-label">Age · Gender · Conditions</p>
          <p class="hp-metric-value" style="font-size:13px;">{user.get('age','—')} · {user.get('gender','—')} · {conditions}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── About ──
    st.markdown(f'<p class="hp-settings-label" style="margin-top:6px;">{S("settings_about")}</p>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hp-card" style="margin-top:0;display:flex;align-items:center;gap:14px;">
      <span style="font-size:32px;">🩺</span>
      <div>
        <p style="margin:0;font-size:15px;font-weight:700;color:#111827;">HealthPal</p>
        <p style="margin:3px 0 0;font-size:12px;color:#9CA3AF;">{S("settings_version")}</p>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    page = st.session_state.current_page
    if   page == "home":       page_home()
    elif page == "add_record": page_add_record()
    elif page == "meds":       page_medications()
    elif page == "ai":         page_ai_chat()
    elif page == "community":  page_community()
    elif page == "settings":   page_settings()
    else:                      page_home()

    render_bottom_nav()

if __name__ == "__main__":
    main()
