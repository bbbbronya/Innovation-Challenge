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
    get_community_posts, like_post, add_community_post,
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
        "community_new_post": "Share Something",
        "community_condition_label": "Condition Tag",
        "community_post_placeholder": "Share your health journey, tips, or questions…",
        "community_btn_post": "Post",
        "community_post_success": "Posted!",
        "community_btn_expand": "Read more",
        "community_btn_collapse": "Show less",
        "community_prev": "Prev",
        "community_next": "Next",
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
        "settings_version": "Version 1.0  ·  Powered by ",
        "ai_tab_patient": "Patient View",
        "ai_tab_doctor": "Doctor Summary",
        "ai_quick_trend": "↗ Trend Summary",
        "ai_quick_meds": "💊 Medication Advice",
        "ai_quick_diet": "🥗 Diet Advice",
        "ai_quick_food": "📷 Food Analysis",
        "ai_greeting_body": "I'm your personal health assistant. I can review your trends, analyze meals, or help with medications. How can I support your wellness today?",
        "ai_doc_generate": "Generate Clinical Summary",
        "ai_doc_generating": "Generating summary…",
        "ai_doc_overview": "Patient Overview",
        "ai_doc_vitals": "Current Vitals",
        "ai_doc_meds": "Medications",
        "ai_doc_summary_title": "AI Clinical Summary",
        "ai_clear": "🗑 Clear",
        "comm_title": "Community & Rewards",
        "comm_subtitle": "Stay motivated and connected",
        "comm_checkin_title": "Daily Check-in",
        "comm_checkin_streak": "day streak",
        "comm_checkin_btn": "Check In",
        "comm_checkin_done": "Checked In ✓",
        "comm_achievement_title": "Recent Achievement",
        "comm_achievement_name": "Perfect Routine",
        "comm_achievement_desc": "On-time medication for 12 consecutive days. Great consistency!",
        "comm_points_title": "Wellness Points",
        "comm_reward_report": "Digital Health Report",
        "comm_reward_dietitian": "Dietitian 1-on-1 Q&A",
        "comm_redeem": "Redeem",
        "comm_redeem_ok": "Redeemed! 🎉",
        "comm_redeem_insufficient": "Not enough points",
        "comm_patient_title": "Patient Community",
        "comm_patient_desc": "Share diet tips, daily habits, and encourage others on the same journey.",
        "comm_tag_diet": "Diet Tips",
        "comm_tag_support": "Support",
        "comm_view_posts": "View Posts",
        "comm_back": "← Back",
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
        "community_new_post": "分享动态",
        "community_condition_label": "病症标签",
        "community_post_placeholder": "分享您的健康经历、小贴士或问题…",
        "community_btn_post": "发布",
        "community_post_success": "已发布！",
        "community_btn_expand": "展开",
        "community_btn_collapse": "收起",
        "community_prev": "上一页",
        "community_next": "下一页",
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
        "settings_version": "版本 1.0  ·  由  驱动",
        "ai_tab_patient": "患者视图",
        "ai_tab_doctor": "医生摘要",
        "ai_quick_trend": "↗ 健康趋势",
        "ai_quick_meds": "💊 用药建议",
        "ai_quick_diet": "🥗 饮食建议",
        "ai_quick_food": "📷 食物分析",
        "ai_greeting_body": "我是您的个人健康助手，可以为您分析健康趋势、饮食和用药情况。今天有什么需要帮助的吗？",
        "ai_doc_generate": "生成临床摘要",
        "ai_doc_generating": "正在生成摘要…",
        "ai_doc_overview": "患者概况",
        "ai_doc_vitals": "当前体征",
        "ai_doc_meds": "用药情况",
        "ai_doc_summary_title": "AI 临床摘要",
        "ai_clear": "🗑 清空",
        "comm_title": "社区与奖励",
        "comm_subtitle": "保持动力，互相鼓励",
        "comm_checkin_title": "每日签到",
        "comm_checkin_streak": "天连续签到",
        "comm_checkin_btn": "立即签到",
        "comm_checkin_done": "已签到 ✓",
        "comm_achievement_title": "近期成就",
        "comm_achievement_name": "完美习惯",
        "comm_achievement_desc": "连续12天按时服药，坚持得很好！",
        "comm_points_title": "健康积分",
        "comm_reward_report": "数字健康报告",
        "comm_reward_dietitian": "营养师一对一问答",
        "comm_redeem": "兑换",
        "comm_redeem_ok": "兑换成功！🎉",
        "comm_redeem_insufficient": "积分不足",
        "comm_patient_title": "病友社区",
        "comm_patient_desc": "分享饮食技巧、日常习惯，鼓励同路上的伙伴。",
        "comm_tag_diet": "饮食贴士",
        "comm_tag_support": "互助支持",
        "comm_view_posts": "查看帖子",
        "comm_back": "← 返回",
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
    "audio_mode": False,
    "community_page": 0,
    "liked_posts": set(),
    "post_form_rev": 0,
    "ai_sub_tab": "patient",
    "doctor_summary": None,
    "comm_streak": 7,
    "comm_last_checkin": None,
    "comm_wellness_pts": 1250,
    "comm_show_posts": False,
    "chat_input_key": 0,
    "show_food_uploader": False,
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
   BOTTOM NAV – JS adds .hp-nav-fixed class at runtime
───────────────────────────────────────────────────── */
#hp-nav-marker { display: none !important; height: 0 !important; }

.hp-nav-fixed {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    transform: none !important;
    width: 100% !important;
    background: #ffffff !important;
    border-top: 1px solid #EAECF0 !important;
    box-shadow: 0 -2px 16px rgba(0,0,0,.06) !important;
    z-index: 1000 !important;
    padding: 0 !important;
    margin: 0 !important;
    padding-bottom: env(safe-area-inset-bottom, 0) !important;
}
.hp-nav-fixed [data-testid="stHorizontalBlock"] {
    width: 100% !important; gap: 0 !important;
    padding: 0 !important; margin: 0 !important;
}
.hp-nav-fixed [data-testid="column"] {
    padding: 0 !important; min-width: 0 !important;
}
.hp-nav-fixed [data-testid="stVerticalBlock"] {
    gap: 0 !important; padding: 0 !important;
}

/* ── nav button: base (inactive) ── */
.hp-nav-fixed div[data-testid="stButton"] > button {
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
.hp-nav-fixed div[data-testid="stButton"] > button:hover {
    color: #5B75F5 !important;
}

/* ── nav button: active (primary) – color only, no border ── */
.hp-nav-fixed div[data-testid="stButton"] > button[kind="primary"],
.hp-nav-fixed div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {
    background: transparent !important;
    color: #3B5BDB !important;
    border: none !important; box-shadow: none !important;
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

/* ── AI sub-tab bar ── */
[data-testid="element-container"]:has(#hp-ai-subtab-marker) {
    height: 0 !important; overflow: hidden !important;
    margin: 0 !important; padding: 0 !important;
}
[data-testid="element-container"]:has(#hp-ai-subtab-marker)
  + [data-testid="element-container"] {
    background: #fff !important;
    border-bottom: 1px solid #F0F2F5 !important;
    padding: 10px 16px 10px !important;
}
[data-testid="element-container"]:has(#hp-ai-subtab-marker)
  + [data-testid="element-container"]
  div[data-testid="stButton"] > button[kind="secondary"] {
    background: #F0F4FF !important; color: #64748B !important;
    border: 1.5px solid #E2E8F0 !important; border-radius: 22px !important;
    height: 38px !important; min-height: 38px !important;
    font-size: 13px !important; font-weight: 600 !important; box-shadow: none !important;
}
[data-testid="element-container"]:has(#hp-ai-subtab-marker)
  + [data-testid="element-container"]
  div[data-testid="stButton"] > button[kind="primary"] {
    background: #3B5BDB !important; color: #fff !important;
    border: none !important; border-radius: 22px !important;
    height: 38px !important; min-height: 38px !important;
    font-size: 13px !important; font-weight: 600 !important;
    box-shadow: 0 3px 10px rgba(59,91,219,.28) !important;
}

/* ── AI greeting card ── */
.hp-ai-greeting {
    margin: 14px 16px 10px; background: #fff; border-radius: 18px;
    padding: 14px 16px; display: flex; gap: 12px; align-items: flex-start;
    box-shadow: 0 2px 12px rgba(59,91,219,.07); border: 1px solid #EEF2FF;
}
.hp-ai-avatar {
    width: 40px; height: 40px; border-radius: 50%;
    background: linear-gradient(135deg, #3B5BDB, #7C8FF5);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0; box-shadow: 0 3px 10px rgba(59,91,219,.3);
}
.hp-ai-greeting-text .greet-name { font-size: 15px; font-weight: 700; color: #0F172A; margin: 0 0 5px; }
.hp-ai-greeting-text .greet-body { font-size: 13px; color: #64748B; line-height: 1.55; margin: 0; }

/* ── AI chat ── */
.chat-scroll {
    max-height: 48vh; overflow-y: auto;
    display: flex; flex-direction: column; gap: 8px; padding: 8px 16px 4px;
}
.hp-bubble-user {
    background: #3B5BDB; color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 14px; margin-left: 36px;
    font-size: 14px; line-height: 1.5; word-break: break-word;
}
.hp-bubble-ai {
    background: #fff; color: #0F172A;
    border-radius: 4px 18px 18px 18px;
    padding: 12px 15px; margin-right: 36px;
    font-size: 14px; line-height: 1.6; word-break: break-word;
    border: 1px solid #E8EEF4; box-shadow: 0 1px 6px rgba(0,0,0,.05);
}
.hp-chat-empty {
    text-align: center; color: #94A3B8; font-size: 13px; padding: 36px 20px;
}

/* ── doctor summary view ── */
.hp-doc-section { padding: 10px 16px 4px; }
.hp-doc-section-title {
    font-size: 11px; font-weight: 700; color: #94A3B8;
    text-transform: uppercase; letter-spacing: .07em; margin-bottom: 8px;
}
.hp-doc-stat-row { display: flex; gap: 10px; margin-bottom: 10px; }
.hp-doc-stat {
    flex: 1; background: #fff; border-radius: 14px; padding: 12px;
    text-align: center; box-shadow: 0 1px 8px rgba(0,0,0,.05); border: 1px solid #F1F5F9;
}
.hp-doc-stat .ds-val { font-size: 17px; font-weight: 700; color: #0F172A; }
.hp-doc-stat .ds-lbl { font-size: 10px; color: #94A3B8; margin-top: 2px; }
.hp-doc-summary-box {
    background: #fff; border-radius: 16px; padding: 16px; margin: 0 16px 12px;
    box-shadow: 0 2px 12px rgba(59,91,219,.07); border: 1px solid #EEF2FF;
    font-size: 13px; color: #374151; line-height: 1.65;
}
.hp-doc-summary-box strong { color: #0F172A; }

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
/* Card shell: style the st.container() that follows the hidden marker */
:has(> .hp-post-marker) + div[data-testid="stVerticalBlock"],
:has(> .hp-post-marker) + div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fff !important; border-radius: 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.07) !important;
    border: 1px solid #F1F5F9 !important; margin-bottom: 10px !important;
    overflow: hidden !important; padding: 0 !important;
}
/* Flatten inner gap so content + footer sit flush */
:has(> .hp-post-marker) + div[data-testid="stVerticalBlock"] > div,
:has(> .hp-post-marker) + div[data-testid="stVerticalBlockBorderWrapper"] > div {
    gap: 0 !important; padding: 0 !important;
}
/* Action footer row */
:has(> .hp-post-marker) + div[data-testid="stVerticalBlock"] [data-testid="stColumns"],
:has(> .hp-post-marker) + div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stColumns"] {
    border-top: 1px solid #F1F5F9; padding: 0 8px; margin: 0 !important;
}
/* Flat ghost buttons inside the card footer */
:has(> .hp-post-marker) + div[data-testid="stVerticalBlock"] [data-testid="stColumns"] button,
:has(> .hp-post-marker) + div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stColumns"] button {
    background: transparent !important; border: none !important;
    box-shadow: none !important; color: #64748B !important;
    font-size: 12px !important; font-weight: 500 !important;
    padding: 6px 4px !important; height: 32px !important;
    min-height: 0 !important; border-radius: 6px !important;
}
:has(> .hp-post-marker) + div[data-testid="stVerticalBlock"] [data-testid="stColumns"] button:hover,
:has(> .hp-post-marker) + div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stColumns"] button:hover {
    background: #F8FAFC !important; color: #374151 !important;
}
/* Card content classes */
.hp-post-inner {
    padding: 14px 16px 10px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,.08);
    border: 1px solid #E8EEF4;
    margin-bottom: 2px;
}
.hp-post-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.hp-post-avatar { font-size: 26px; line-height: 1; flex-shrink: 0; }
.hp-post-meta { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.hp-post-name { font-weight: 700; font-size: 14px; color: #1E293B; }
.hp-post-date { font-size: 11px; color: #94A3B8; margin-top: 1px; }
.hp-post-tag {
    border-radius: 20px; padding: 4px 10px; font-size: 11px; font-weight: 600;
    white-space: nowrap; flex-shrink: 0;
}
.hp-post-content { font-size: 13px; color: #374151; line-height: 1.55; }
.hp-post-accent { height: 4px; border-radius: 4px; margin-bottom: 12px; }

/* ── Community & Rewards page ── */
.hp-comm-header {
    background: #fff; padding: 20px 20px 14px;
    border-bottom: 1px solid #F0F2F5;
}
.hp-comm-header h2 {
    margin: 0; font-size: 22px; font-weight: 700; color: #0F172A; letter-spacing: -.3px;
}
.hp-comm-header p { margin: 3px 0 0; font-size: 13px; color: #94A3B8; }

/* Check-in card row */
.hp-checkin-row {
    display: flex; align-items: center; gap: 13px;
}
.hp-checkin-icon {
    width: 44px; height: 44px; border-radius: 50%;
    background: #FEF3C7; display: flex; align-items: center;
    justify-content: center; font-size: 22px; flex-shrink: 0;
}
.hp-checkin-info { flex: 1; }
.hp-checkin-info .ci-title { font-size: 15px; font-weight: 700; color: #0F172A; margin: 0; }
.hp-checkin-info .ci-sub   { font-size: 12px; color: #94A3B8; margin: 2px 0 0; }
.hp-checkin-btn {
    background: #3B5BDB; color: #fff; border: none; border-radius: 22px;
    padding: 9px 18px; font-size: 13px; font-weight: 700; cursor: pointer;
    white-space: nowrap; flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(59,91,219,.35);
}
.hp-checkin-btn.done {
    background: #DCFCE7; color: #15803D; box-shadow: none;
}

/* Achievement card */
.hp-achievement-inner {
    background: #EEF2FF; border-radius: 14px; padding: 14px 16px;
    display: flex; align-items: center; gap: 14px;
}
.hp-achievement-badge {
    width: 46px; height: 46px; border-radius: 50%;
    background: #fff; display: flex; align-items: center;
    justify-content: center; font-size: 24px; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(59,91,219,.15);
}
.hp-achievement-text .at-title { font-size: 15px; font-weight: 700; color: #0F172A; margin: 0; }
.hp-achievement-text .at-desc  { font-size: 12px; color: #475569; margin: 3px 0 0; line-height: 1.5; }

/* Wellness points */
.hp-points-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 14px;
}
.hp-points-header .pt-label { font-size: 15px; font-weight: 700; color: #0F172A; display: flex; align-items: center; gap: 7px; }
.hp-points-header .pt-value { font-size: 18px; font-weight: 800; color: #0F172A; }
.hp-points-header .pt-unit  { font-size: 13px; font-weight: 500; color: #94A3B8; margin-left: 3px; }
.hp-reward-grid { display: flex; gap: 10px; }
.hp-reward-item {
    flex: 1; background: #F8FAFC; border-radius: 12px;
    padding: 12px; border: 1px solid #E2E8F0;
}
.hp-reward-item .ri-name { font-size: 13px; font-weight: 600; color: #0F172A; margin: 0 0 5px; line-height: 1.4; }
.hp-reward-item .ri-pts  { font-size: 13px; font-weight: 700; color: #3B5BDB; margin: 0; }

/* Patient community card */
.hp-patcomm-row {
    display: flex; align-items: center; gap: 13px;
}
.hp-patcomm-icon {
    width: 44px; height: 44px; border-radius: 50%;
    background: #DCFCE7; display: flex; align-items: center;
    justify-content: center; font-size: 22px; flex-shrink: 0;
}
.hp-patcomm-info { flex: 1; min-width: 0; }
.hp-patcomm-info .pc-title { font-size: 15px; font-weight: 700; color: #0F172A; margin: 0 0 3px; }
.hp-patcomm-info .pc-desc  { font-size: 12px; color: #64748B; margin: 0; line-height: 1.5; }
.hp-patcomm-arrow { font-size: 18px; color: #94A3B8; flex-shrink: 0; }
.hp-tag-row { display: flex; gap: 7px; margin-top: 10px; }
.hp-tag-pill {
    border: 1px solid #E2E8F0; border-radius: 20px;
    padding: 4px 12px; font-size: 12px; font-weight: 500; color: #475569;
    background: #fff;
}

/* ── Community marker-card containers ── */
[data-testid="element-container"]:has(#hp-ci-marker),
[data-testid="element-container"]:has(#hp-pts-marker),
[data-testid="element-container"]:has(#hp-patcomm-marker) {
    height: 0 !important; overflow: hidden !important;
    margin: 0 !important; padding: 0 !important;
}
[data-testid="element-container"]:has(#hp-ci-marker) + [data-testid="element-container"],
[data-testid="element-container"]:has(#hp-pts-marker) + [data-testid="element-container"],
[data-testid="element-container"]:has(#hp-patcomm-marker) + [data-testid="element-container"] {
    background: #fff !important;
    border-radius: 20px !important;
    margin: 0 16px 10px !important;
    box-shadow: 0 2px 16px rgba(15,23,42,.06) !important;
    padding: 14px 14px !important;
}
/* Remove inner vertical gap */
[data-testid="element-container"]:has(#hp-ci-marker) + [data-testid="element-container"] [data-testid="stVerticalBlock"],
[data-testid="element-container"]:has(#hp-pts-marker) + [data-testid="element-container"] [data-testid="stVerticalBlock"],
[data-testid="element-container"]:has(#hp-patcomm-marker) + [data-testid="element-container"] [data-testid="stVerticalBlock"] {
    gap: 4px !important;
}
/* Remove column padding inside community cards */
[data-testid="element-container"]:has(#hp-ci-marker) + [data-testid="element-container"] [data-testid="column"],
[data-testid="element-container"]:has(#hp-pts-marker) + [data-testid="element-container"] [data-testid="column"],
[data-testid="element-container"]:has(#hp-patcomm-marker) + [data-testid="element-container"] [data-testid="column"] {
    padding: 0 4px !important;
}
/* Check-in button: small blue pill on the right */
[data-testid="element-container"]:has(#hp-ci-marker) + [data-testid="element-container"]
  div[data-testid="stButton"] > button[kind="primary"] {
    border-radius: 22px !important;
    height: 38px !important; min-height: 38px !important;
    font-size: 13px !important; padding: 0 14px !important;
    box-shadow: 0 3px 10px rgba(59,91,219,.3) !important;
}
/* Redeem buttons: small outline style */
[data-testid="element-container"]:has(#hp-pts-marker) + [data-testid="element-container"]
  div[data-testid="stButton"] > button {
    height: 32px !important; min-height: 32px !important;
    font-size: 12px !important; padding: 0 10px !important;
    border-radius: 10px !important;
    background: #EEF2FF !important; color: #3B5BDB !important;
    border: 1.5px solid #C7D2FE !important; box-shadow: none !important;
}
/* View Posts button: full-width blue */
[data-testid="element-container"]:has(#hp-patcomm-marker) + [data-testid="element-container"]
  div[data-testid="stButton"] > button[kind="primary"] {
    border-radius: 14px !important;
    height: 42px !important; min-height: 42px !important;
    font-size: 14px !important;
    background: #3B5BDB !important; color: #fff !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(59,91,219,.28) !important;
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
/* hide the 0-height iframe injected by components.html for JS execution */
iframe[height="0"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# LLM — MERaLiON nutrition assistant
# ═══════════════════════════════════════════════════════════════════════════
def ask_ai_merlion_audio(audio_bytes: bytes, history: list) -> tuple[str, str]:
    """Send audio to MERaLiON. Returns (transcribed_text, ai_reply)."""
    key = get_secret("merlion_API_KEY")
    if not key:
        return "🎤 Voice message", "⚠️ MERaLiON API key not configured in secrets.toml"
    try:
        from openai import OpenAI
        import base64
        client = OpenAI(base_url="http://meralion.org:8010/v1", api_key=key)
        user = get_user()
        lv = get_latest_vitals()
        conditions = ", ".join(user.get("conditions", []))
        system_prompt = (
            "You ONLY answer questions related to healthcare, health, nutrition, medications, medical conditions, "
            "and general wellness. If the user asks about anything unrelated to health topics, politely decline "
            "and redirect them to ask a health-related question instead. "
            "You are a professional personal nutrition assistant specialising in Southeast Asian cuisine. "
            "The user sent a voice message — understand their spoken question and respond with personalised "
            "food and diet recommendations using SEA dishes (Malaysian, Singaporean, Indonesian, Thai, etc.). "
            f"Patient: {user.get('name','')}, age {user.get('age','?')}, {user.get('gender','?')}. "
            f"Conditions: {conditions}. "
            f"BP: {lv.get('systolic','?')}/{lv.get('diastolic','?')} mmHg, "
            f"Glucose: {lv.get('glucose','?')} mmol/L. "
            "IMPORTANT: Detect the language the user spoke and reply in that same language. Be warm and concise."
        )
        audio_b64 = base64.b64encode(audio_bytes).decode()
        # Step 1: transcribe so we can show it in the chat bubble
        transcribe_msgs = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Transcribe this audio exactly as spoken, no extra text."},
                {"type": "audio_url", "audio_url": {"url": f"data:audio/wav;base64,{audio_b64}"}},
            ],
        }]
        t_resp = client.chat.completions.create(
            model="MERaLiON/MERaLiON-3-10B",
            messages=transcribe_msgs,
        )
        transcription = t_resp.choices[0].message.content.strip()
        # Step 2: answer as nutrition assistant using full history + transcription
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            role = "assistant" if msg["role"] == "assistant" else "user"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": transcription},
                {"type": "audio_url", "audio_url": {"url": f"data:audio/wav;base64,{audio_b64}"}},
            ],
        })
        a_resp = client.chat.completions.create(
            model="MERaLiON/MERaLiON-3-10B",
            messages=messages,
        )
        return f"🎤 {transcription}", a_resp.choices[0].message.content
    except Exception as e:
        return "🎤 Voice message", f"Error: {e}"


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
            "You ONLY answer questions related to healthcare, health, nutrition, medications, medical conditions, "
            "and general wellness. If the user asks about anything unrelated to health topics, politely decline "
            "and redirect them to ask a health-related question instead. "
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


def _preprocess_image(image_bytes: bytes) -> tuple[bytes, str]:
    """Resize and compress image to ≤800px / JPEG q70 to keep API payload small."""
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > 800:
        ratio = 800 / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70, optimize=True)
    return buf.getvalue(), "jpeg"


def ask_ai_gemini_image(image_bytes: bytes, image_type: str, extra_text: str, history: list) -> str:
    """Analyse a food photo via Gemini 2.5 Flash Lite (google-genai SDK)."""
    key = get_secret("gemini_API_KEY")
    if not key:
        return "⚠️ gemini_API_KEY not configured in secrets.toml"
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        user = get_user()
        lv = get_latest_vitals()
        conditions = ", ".join(user.get("conditions", []))
        system_text = (
            "You ONLY answer questions related to healthcare, health, nutrition, medications, medical conditions, "
            "and general wellness. If the user asks about anything unrelated to health topics, politely decline "
            "and redirect them to ask a health-related question instead. "
            "You are a professional nutrition assistant specialising in Southeast Asian cuisine. "
            "Analyse the food photo the user sent. Identify the dish/food items visible, estimate portion size "
            "if possible, and give personalised dietary advice based on the patient's health profile. Do not use markdown formatting in your response."
            "Be warm, practical, and concise. "
            f"Patient: {user.get('name','')}, age {user.get('age','?')}, {user.get('gender','?')}. "
            f"Conditions: {conditions}. "
            f"BP: {lv.get('systolic','?')}/{lv.get('diastolic','?')} mmHg, "
            f"HR: {lv.get('heart_rate','?')} bpm, Glucose: {lv.get('glucose','?')} mmol/L."
        )
        question = extra_text.strip() if extra_text.strip() else \
            "Please analyse this food and advise me based on my health conditions."
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(system_instruction=system_text),
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                question,
            ],
        )
        return response.text
    except Exception as e:
        return f"Error analysing image: {e}"


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
    import streamlit.components.v1 as components
    cur = st.session_state.current_page
    # Marker: JS uses this to locate and fix the NEXT sibling element
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
    # Inject JS via iframe (st.markdown scripts are blocked by React; iframe srcdoc executes reliably)
    components.html("""
<script>
(function() {
    var pd = window.parent.document;
    function fixNav() {
        var marker = pd.getElementById('hp-nav-marker');
        if (!marker) return;
        // Walk UP until we find a direct child of stVerticalBlock,
        // then take ITS nextElementSibling — works regardless of wrapper layers
        var el = marker;
        while (el && el !== pd.body) {
            var par = el.parentElement;
            if (par && par.getAttribute && par.getAttribute('data-testid') === 'stVerticalBlock') {
                var navContainer = el.nextElementSibling;
                if (navContainer && !navContainer.classList.contains('hp-nav-fixed')) {
                    navContainer.classList.add('hp-nav-fixed');
                }
                return;
            }
            el = par;
        }
    }
    fixNav();
    new window.parent.MutationObserver(fixNav).observe(pd.body, { childList: true, subtree: true });
})();
</script>
""", height=0)


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
# AI HELPER – doctor clinical summary
# ═══════════════════════════════════════════════════════════════════════════
def ask_ai_doctor_summary() -> str:
    key = get_secret("merlion_API_KEY")
    if not key:
        return "⚠️ MERaLiON API key not configured in secrets.toml"
    try:
        from openai import OpenAI
        client = OpenAI(base_url="http://meralion.org:8010/v1", api_key=key)
        user = get_user()
        lv = get_latest_vitals()
        meds = get_medications()
        ms = get_today_med_status()
        lab = get_lab_results()
        conditions = ", ".join(user.get("conditions", []))
        med_list = ", ".join(meds["name"].tolist()) if not meds.empty else "None"
        lab_summary = ""
        if not lab.empty:
            for _, row in lab.iterrows():
                lab_summary += f"{row.get('test_name','')}: {row.get('status','')} ({row.get('tested_at','')}); "
        system_prompt = (
            "You are a clinical assistant generating a structured patient summary for a physician. "
            "Be concise, factual, and use clinical language. "
            "Use **bold** for section headers."
        )
        user_msg = (
            f"Generate a clinical summary for:\n"
            f"Patient: {user.get('name','')}, Age: {user.get('age','?')}, Gender: {user.get('gender','?')}\n"
            f"Conditions: {conditions}\n"
            f"Latest vitals — BP: {lv.get('systolic','?')}/{lv.get('diastolic','?')} mmHg, "
            f"HR: {lv.get('heart_rate','?')} bpm, Fasting Glucose: {lv.get('glucose','?')} mmol/L\n"
            f"Medications: {med_list}\n"
            f"Medication adherence today: {ms['taken']}/{ms['total']} taken\n"
            f"Lab results: {lab_summary if lab_summary else 'No recent labs'}\n\n"
            "Structure with: **Patient Overview**, **Vitals Assessment**, "
            "**Medication Status**, **Key Concerns**, **Recommendations**"
        )
        response = client.chat.completions.create(
            model="MERaLiON/MERaLiON-3-10B",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}"


# ═══════════════════════════════════════════════════════════════════════════
# AI SUB-VIEWS
# ═══════════════════════════════════════════════════════════════════════════
def _ai_patient_view(user: dict):
    """Patient-facing AI chat."""
    # ── Greeting or chat history ──
    if st.session_state.chat_history:
        msgs_html = '<div class="chat-scroll">'
        for msg in st.session_state.chat_history:
            cls = "hp-bubble-user" if msg["role"] == "user" else "hp-bubble-ai"
            txt = msg["content"].replace("\n", "<br>")
            if "image_b64" in msg:
                img_tag = (f'<img src="data:{msg["image_mime"]};base64,{msg["image_b64"]}" '
                           f'style="max-width:100%;border-radius:10px;margin-bottom:6px;display:block;">')
                msgs_html += f'<div class="{cls}">{img_tag}{txt}</div>'
            else:
                msgs_html += f'<div class="{cls}">{txt}</div>'
        msgs_html += '</div>'
        st.markdown(msgs_html, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="hp-ai-greeting">
          <div class="hp-ai-avatar">✨</div>
          <div class="hp-ai-greeting-text">
            <p class="greet-name">Hello {user.get('name', '')}! 👋</p>
            <p class="greet-body">{S('ai_greeting_body')}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Quick action chips (2×2 grid) ──
    if True:
        if st.session_state.language == "zh":
            quick_actions = [
                (S("ai_quick_trend"),
                 "请给我一个本周健康趋势摘要，包括血压、血糖和任何值得注意的变化。"),
                (S("ai_quick_meds"),
                 "我的用药情况如何？有什么关于坚持服药或需要注意的副作用的建议吗？"),
                (S("ai_quick_diet"),
                 "根据我的健康状况和最新体征，给我一些个性化的饮食建议。"),
                (S("ai_quick_food"),
                 "鉴于我的病症，我应该避免哪些食物，应该多吃哪些食物？"),
            ]
        else:
            quick_actions = [
                (S("ai_quick_trend"),
                 "Give me a summary of my health trends this week, including blood pressure, glucose, and any notable changes."),
                (S("ai_quick_meds"),
                 "How am I doing with my medications? Any advice on adherence or side effects to watch for?"),
                (S("ai_quick_diet"),
                 "Give me personalized diet advice based on my health conditions and latest vitals."),
                (S("ai_quick_food"),
                 "What foods should I avoid and what should I eat more of given my conditions?"),
            ]
        qa_cols = st.columns(2)
        # First 3 chips: text quick actions; 4th chip: photo upload trigger
        text_actions = quick_actions[:-1]
        for i, (label, prompt) in enumerate(text_actions):
            with qa_cols[i % 2]:
                if st.button(label, key=f"qa_{i}", use_container_width=True):
                    st.session_state.pending_question = prompt
                    st.rerun()
        with qa_cols[1]:
            photo_label = quick_actions[-1][0]
            photo_active = st.session_state.show_food_uploader
            if st.button(photo_label, key="qa_photo", use_container_width=True,
                         type="primary" if photo_active else "secondary"):
                st.session_state.show_food_uploader = not photo_active
                st.rerun()

    # ── Food photo uploader (revealed when chip is active) ──
    uploaded_img = None
    if st.session_state.show_food_uploader:
        uploaded_img = st.file_uploader(
            "Upload a food photo", type=["jpg", "jpeg", "png"],
            key="food_photo", label_visibility="collapsed")
        # Auto-analyse as soon as a file is selected
        if uploaded_img is not None:
            import base64 as _b64
            raw_bytes = uploaded_img.read()
            img_bytes, _ = _preprocess_image(raw_bytes)
            st.session_state.show_food_uploader = False
            st.session_state.chat_history.append({
                "role": "user",
                "content": "📷 Food photo",
                "image_b64": _b64.b64encode(img_bytes).decode(),
                "image_mime": "image/jpeg",
            })
            with st.spinner(S("thinking")):
                reply = ask_ai_gemini_image(
                    img_bytes, "jpeg",
                    "Is this food suitable for my health conditions? Please analyse it.",
                    st.session_state.chat_history[:-1],
                )
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # ── Text + voice input row ──
    c1, c2, c3 = st.columns([5, 1, 1])
    with c1:
        user_input = st.text_input(
            "msg", key=f"chat_text_{st.session_state.chat_input_key}",
            label_visibility="collapsed", placeholder=S("user_input"))
    with c2:
        mic_icon = "⏹" if st.session_state.audio_mode else "🎤"
        if st.button(mic_icon, key="toggle_mic", use_container_width=True,
                     type="primary" if st.session_state.audio_mode else "secondary"):
            st.session_state.audio_mode = not st.session_state.audio_mode
            st.rerun()
    with c3:
        send_clicked = st.button(S("btn_submit"), key="send_btn",
                                  use_container_width=True, type="primary")

    # Clear button
    if st.button(S("ai_clear"), key="clear_chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    # ── Voice recording (shown when audio mode active) ──
    if st.session_state.audio_mode:
        st.markdown('<div style="font-size:12px;color:#6B7280;margin-top:4px;">🌏 Malay · Indonesian · Thai · Vietnamese · Tamil · English · 中文</div>',
                    unsafe_allow_html=True)
        audio_val = st.audio_input("Record", key="voice_input", label_visibility="collapsed")
    else:
        audio_val = None

    # ── Handle send (text / voice only) ──
    if send_clicked:
        if audio_val is not None and st.session_state.audio_mode:
            audio_bytes = audio_val.read()
            if audio_bytes:
                with st.spinner(S("thinking")):
                    transcription, reply = ask_ai_merlion_audio(audio_bytes, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "user", "content": transcription})
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()
        else:
            txt = user_input.strip()
            if txt:
                st.session_state.chat_history.append({"role": "user", "content": txt})
                with st.spinner(S("thinking")):
                    reply = ask_ai_merlion(st.session_state.chat_history[:-1], txt)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.session_state.chat_input_key += 1
                st.rerun()

    # Handle quick-action / pending question
    if st.session_state.get("pending_question"):
        pq = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.chat_history.append({"role": "user", "content": pq})
        with st.spinner(S("thinking")):
            reply = ask_ai_merlion(st.session_state.chat_history[:-1], pq)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()


def _ai_doctor_view(user: dict):
    """Doctor-facing clinical summary view."""
    import re
    lv  = get_latest_vitals()
    ms  = get_today_med_status()
    conditions = ", ".join(user.get("conditions", []))

    # ── Patient overview ──
    st.markdown(f'<div class="hp-doc-section"><p class="hp-doc-section-title">{S("ai_doc_overview")}</p></div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hp-card" style="margin-top:0;">
      <div class="hp-metric-row">
        <div class="hp-icon-circle" style="background:#EDE9FE;">👤</div>
        <div>
          <p class="hp-metric-label">Name · Age · Gender</p>
          <p class="hp-metric-value" style="font-size:14px;">
            {user.get('name','—')} · {user.get('age','—')} · {user.get('gender','—')}
          </p>
        </div>
      </div>
      <div class="hp-metric-row" style="border-bottom:none;padding-bottom:0;">
        <div class="hp-icon-circle" style="background:#FEE2E2;">🏥</div>
        <div>
          <p class="hp-metric-label">Conditions</p>
          <p class="hp-metric-value" style="font-size:13px;">{conditions}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Vitals stats ──
    bp_color  = "#EF4444" if int(lv.get("systolic", 0) or 0) > 140 else "#22C55E"
    glu_color = "#F59E0B" if float(lv.get("glucose", 0) or 0) > 6.0 else "#22C55E"
    st.markdown(f'<div class="hp-doc-section"><p class="hp-doc-section-title">{S("ai_doc_vitals")}</p>'
                f'<div class="hp-doc-stat-row">'
                f'<div class="hp-doc-stat"><div class="ds-val" style="color:{bp_color};">'
                f'{lv.get("systolic","—")}/{lv.get("diastolic","—")}</div><div class="ds-lbl">mmHg (BP)</div></div>'
                f'<div class="hp-doc-stat"><div class="ds-val" style="color:{glu_color};">'
                f'{lv.get("glucose","—")}</div><div class="ds-lbl">mmol/L (Glucose)</div></div>'
                f'<div class="hp-doc-stat"><div class="ds-val">{lv.get("heart_rate","—")}</div>'
                f'<div class="ds-lbl">bpm (HR)</div></div>'
                f'</div></div>', unsafe_allow_html=True)

    # ── Medication adherence ──
    adh_pct   = int(ms['taken'] / ms['total'] * 100) if ms['total'] > 0 else 0
    adh_color = "#22C55E" if adh_pct >= 80 else "#F59E0B" if adh_pct >= 50 else "#EF4444"
    st.markdown(f'<div class="hp-doc-section"><p class="hp-doc-section-title">{S("ai_doc_meds")}</p></div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hp-card" style="margin-top:0;">
      <div class="hp-med-summary">
        <div class="hp-icon-circle med">💊</div>
        <div class="hp-med-info">
          <p class="mtitle"><b>{ms['taken']}/{ms['total']}</b> medications taken today</p>
          <p class="msub" style="color:{adh_color};font-weight:600;">{adh_pct}% adherence</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Generate summary button ──
    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
    if st.button(S("ai_doc_generate"), key="gen_doc_summary", use_container_width=True, type="primary"):
        with st.spinner(S("ai_doc_generating")):
            st.session_state.doctor_summary = ask_ai_doctor_summary()
        st.rerun()

    # ── Display AI summary ──
    if st.session_state.doctor_summary:
        st.markdown(f'<p class="hp-doc-section-title" style="padding:10px 16px 4px;">'
                    f'{S("ai_doc_summary_title")}</p>', unsafe_allow_html=True)
        summary_html = st.session_state.doctor_summary.replace("\n", "<br>")
        summary_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", summary_html)
        st.markdown(f'<div class="hp-doc-summary-box">{summary_html}</div>', unsafe_allow_html=True)
        if st.button("🔄 Regenerate", key="regen_doc_summary"):
            st.session_state.doctor_summary = None
            st.rerun()

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: AI CHAT  (MERaLiON SEA nutrition assistant)
# ═══════════════════════════════════════════════════════════════════════════
def page_ai_chat():
    user = get_user()
    # ── Page title ──
    st.markdown(f'<div class="hp-page-title">✨ {S("title_ai")}</div>', unsafe_allow_html=True)

    # ── Sub-tab switcher (Patient View / Doctor Summary) ──
    st.markdown('<div id="hp-ai-subtab-marker"></div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    patient_active = st.session_state.ai_sub_tab == "patient"
    with sc1:
        if st.button(S("ai_tab_patient"), key="ai_tab_pt", use_container_width=True,
                     type="primary" if patient_active else "secondary"):
            st.session_state.ai_sub_tab = "patient"
            st.rerun()
    with sc2:
        if st.button(S("ai_tab_doctor"), key="ai_tab_dr", use_container_width=True,
                     type="primary" if not patient_active else "secondary"):
            st.session_state.ai_sub_tab = "doctor"
            st.rerun()

    if patient_active:
        _ai_patient_view(user)
    else:
        _ai_doctor_view(user)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE: COMMUNITY
# ═══════════════════════════════════════════════════════════════════════════
def _render_community_posts(user: dict):
    """Renders the post feed (posts view inside Community tab)."""
    if st.button(S("comm_back"), key="comm_back_btn"):
        st.session_state.comm_show_posts = False
        st.rerun()

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    # New post form
    with st.expander("✏️ " + S("community_new_post")):
        cond_options = ["Type 2 Diabetes", "Hypertension", "Dyslipidemia", "Other"]
        sel_cond = st.selectbox(S("community_condition_label"), cond_options, key="new_post_cond")
        rev = st.session_state.post_form_rev
        post_text = st.text_area(
            S("community_post_placeholder"),
            key=f"new_post_text_{rev}", height=100, label_visibility="collapsed",
        )
        if st.button(S("community_btn_post"), key="submit_post"):
            if post_text.strip():
                add_community_post(
                    author_id=user.get("user_id", "U001"),
                    author_name=user.get("name", "You"),
                    author_avatar=user.get("avatar_emoji", "👤"),
                    condition_tag=sel_cond,
                    content=post_text.strip(),
                )
                st.session_state.post_form_rev += 1
                st.session_state.community_page = 0
                st.success(S("community_post_success"))
                st.rerun()

    df = get_community_posts(limit=100)
    if df.empty:
        st.markdown(f"""<div class="hp-card"><div class="hp-community-empty">
          <div style="font-size:44px;margin-bottom:12px;">🌱</div>
          <div style="font-weight:600;color:#6B7280;">{S('community_empty')}</div>
        </div></div>""", unsafe_allow_html=True)
        return

    POSTS_PER_PAGE = 4
    total_pages = max(1, -(-len(df) // POSTS_PER_PAGE))
    page_num = min(st.session_state.get("community_page", 0), total_pages - 1)
    start = page_num * POSTS_PER_PAGE
    page_posts = df.iloc[start: start + POSTS_PER_PAGE]
    liked_set = st.session_state.get("liked_posts", set())

    _TAG_COLORS = {
        "Type 2 Diabetes": ("#FEF3C7", "#92400E"),
        "Hypertension":    ("#FEE2E2", "#991B1B"),
        "Dyslipidemia":    ("#EDE9FE", "#5B21B6"),
    }
    _ACCENT_COLORS = {
        "Type 2 Diabetes": "#F59E0B",
        "Hypertension":    "#EF4444",
        "Dyslipidemia":    "#8B5CF6",
    }

    for _, post in page_posts.iterrows():
        pid = str(post["post_id"])
        is_expanded = st.session_state.get(f"exp_{pid}", False)
        content = str(post["content"])
        content_display = content if is_expanded else (content[:120] + "…" if len(content) > 120 else content)
        tag_bg, tag_fg = _TAG_COLORS.get(str(post["condition_tag"]), ("#F1F5F9", "#475569"))
        accent = _ACCENT_COLORS.get(str(post["condition_tag"]), "#94A3B8")
        posted_dt = post["posted_at"]
        posted_str = posted_dt.strftime("%b %d") if hasattr(posted_dt, "strftime") else str(posted_dt)[:10]
        already_liked = pid in liked_set

        st.markdown('<div class="hp-post-marker" style="display:none"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown(f"""
            <div class="hp-post-inner">
              <div class="hp-post-accent" style="background:{accent};"></div>
              <div class="hp-post-header">
                <span class="hp-post-avatar">{post['author_avatar']}</span>
                <div class="hp-post-meta">
                  <span class="hp-post-name">{post['author_name']}</span>
                  <span class="hp-post-date">{posted_str}</span>
                </div>
                <span class="hp-post-tag" style="background:{tag_bg};color:{tag_fg};">{post['condition_tag']}</span>
              </div>
              <div class="hp-post-content">{content_display}</div>
            </div>""", unsafe_allow_html=True)

            col1, col2, _ = st.columns([2, 2, 4])
            with col1:
                expand_label = S("community_btn_collapse") if is_expanded else S("community_btn_expand")
                if st.button(expand_label, key=f"toggle_{pid}", use_container_width=True):
                    st.session_state[f"exp_{pid}"] = not is_expanded
                    st.rerun()
            with col2:
                like_label = f"❤️ {int(post['likes'])}" if already_liked else f"🤍 {int(post['likes'])}"
                if st.button(like_label, key=f"like_{pid}", use_container_width=True, disabled=already_liked):
                    like_post(pid)
                    liked_set.add(pid)
                    st.session_state.liked_posts = liked_set
                    st.rerun()

    if total_pages > 1:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
        with pcol1:
            if page_num > 0 and st.button("← " + S("community_prev"), key="prev_page", use_container_width=True):
                st.session_state.community_page = page_num - 1
                st.rerun()
        with pcol2:
            st.markdown(
                f"<div style='text-align:center;font-size:13px;color:#6B7280;padding-top:8px;'>"
                f"{page_num+1} / {total_pages}</div>", unsafe_allow_html=True)
        with pcol3:
            if page_num < total_pages - 1 and st.button(S("community_next") + " →", key="next_page", use_container_width=True):
                st.session_state.community_page = page_num + 1
                st.rerun()


def page_community():
    user = get_user()

    # ── Header ──
    st.markdown(f"""
    <div class="hp-comm-header">
      <h2>{S("comm_title")}</h2>
      <p>{S("comm_subtitle")}</p>
    </div>""", unsafe_allow_html=True)

    # ── Posts sub-view ──
    if st.session_state.comm_show_posts:
        _render_community_posts(user)
        return

    # ─────────────────────────────────────────────────────────────────────
    # MAIN COMMUNITY & REWARDS DASHBOARD
    # ─────────────────────────────────────────────────────────────────────

    today_str = datetime.now().strftime("%Y-%m-%d")
    already_checked_in = st.session_state.comm_last_checkin == today_str
    streak = st.session_state.comm_streak
    pts    = st.session_state.comm_wellness_pts

    # ── 1. Daily Check-in card ──
    # Marker → next container styled as card; columns: info left, button right
    st.markdown('<div id="hp-ci-marker" style="display:none"></div>', unsafe_allow_html=True)
    with st.container():
        ci_l, ci_r = st.columns([5, 2])
        with ci_l:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:4px 0;">
              <div class="hp-checkin-icon">🔥</div>
              <div>
                <p style="margin:0;font-size:15px;font-weight:700;color:#0F172A;">{S("comm_checkin_title")}</p>
                <p style="margin:3px 0 0;font-size:12px;color:#94A3B8;">{streak}-{S("comm_checkin_streak")}</p>
              </div>
            </div>""", unsafe_allow_html=True)
        with ci_r:
            if not already_checked_in:
                if st.button(S("comm_checkin_btn"), key="comm_checkin_go",
                             type="primary", use_container_width=True):
                    st.session_state.comm_last_checkin = today_str
                    st.session_state.comm_streak += 1
                    st.session_state.comm_wellness_pts += 50
                    st.rerun()
            else:
                st.markdown(
                    f'<div style="text-align:center;background:#DCFCE7;border-radius:12px;'
                    f'padding:9px 4px;font-size:11px;font-weight:700;color:#15803D;">'
                    f'{S("comm_checkin_done")}</div>',
                    unsafe_allow_html=True,
                )

    # ── 2. Recent Achievement card (pure HTML — no interactive elements) ──
    st.markdown(f"""
    <div class="hp-card">
      <div class="hp-card-title" style="margin-bottom:12px;">🏅 {S("comm_achievement_title")}</div>
      <div class="hp-achievement-inner">
        <div class="hp-achievement-badge">🏆</div>
        <div class="hp-achievement-text">
          <p class="at-title">{S("comm_achievement_name")}</p>
          <p class="at-desc">{S("comm_achievement_desc")}</p>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── 3. Wellness Points card ──
    # Marker → card container; two reward columns each with info + redeem button
    st.markdown('<div id="hp-pts-marker" style="display:none"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
        <div class="hp-points-header">
          <span class="pt-label">🎁 {S("comm_points_title")}</span>
          <span><span class="pt-value">{pts:,}</span><span class="pt-unit"> pts</span></span>
        </div>""", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"""
            <div class="hp-reward-item">
              <p class="ri-name">{S("comm_reward_report")}</p>
              <p class="ri-pts">500 pts</p>
            </div>""", unsafe_allow_html=True)
            if st.button(S("comm_redeem"), key="redeem_report", use_container_width=True):
                if pts >= 500:
                    st.session_state.comm_wellness_pts -= 500
                    st.success(S("comm_redeem_ok"))
                    st.rerun()
                else:
                    st.warning(S("comm_redeem_insufficient"))
        with r2:
            st.markdown(f"""
            <div class="hp-reward-item">
              <p class="ri-name">{S("comm_reward_dietitian")}</p>
              <p class="ri-pts">2,000 pts</p>
            </div>""", unsafe_allow_html=True)
            if st.button(S("comm_redeem"), key="redeem_dietitian", use_container_width=True):
                if pts >= 2000:
                    st.session_state.comm_wellness_pts -= 2000
                    st.success(S("comm_redeem_ok"))
                    st.rerun()
                else:
                    st.warning(S("comm_redeem_insufficient"))

    # ── 4. Patient Community card ──
    # Marker → card container; info HTML then view-posts button at bottom
    st.markdown('<div id="hp-patcomm-marker" style="display:none"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:13px;margin-bottom:8px;">
          <div class="hp-patcomm-icon">👥</div>
          <div class="hp-patcomm-info">
            <p class="pc-title">{S("comm_patient_title")}</p>
            <p class="pc-desc">{S("comm_patient_desc")}</p>
          </div>
        </div>
        <div class="hp-tag-row" style="margin-bottom:10px;">
          <span class="hp-tag-pill">{S("comm_tag_diet")}</span>
          <span class="hp-tag-pill">{S("comm_tag_support")}</span>
        </div>""", unsafe_allow_html=True)
        if st.button(S("comm_view_posts"), key="go_posts",
                     use_container_width=True, type="primary"):
            st.session_state.comm_show_posts = True
            st.rerun()


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
