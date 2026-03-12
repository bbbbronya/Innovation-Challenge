"""
健康管家 HealthPal v2
- 手机界面风格
- 支持 Anthropic / OpenAI / Ollama 三种 LLM
- 适合 Streamlit Community Cloud 托管
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random, base64, io, json
from PIL import Image

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="健康管家",
    page_icon="🩺",
    layout="centered",       # centered = mobile feel
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
# LLM PROVIDER LAYER  ← swap here for different backends
# ═══════════════════════════════════════════════════════════════════════════════

PROVIDERS = {
    "🟣 Anthropic (Claude)": "anthropic",
    "🟢 OpenAI (GPT-4o)":    "openai",
    "🦙 Ollama (本地)":       "ollama",
}

def get_llm_response(messages: list, system: str = "", image_b64: str = None) -> str:
    """Unified LLM call. messages = [{"role":..,"content":..}]"""
    provider = st.session_state.get("provider", "anthropic")
    
    try:
        # ── Anthropic ──────────────────────────────────────────────────────────
        if provider == "anthropic":
            import anthropic
            key = st.session_state.get("api_key") or st.secrets.get("ANTHROPIC_API_KEY", "")
            client = anthropic.Anthropic(api_key=key)
            
            api_messages = []
            for m in messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            # vision support
            if image_b64:
                api_messages[-1]["content"] = [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64}},
                    {"type": "text", "text": messages[-1]["content"]},
                ]
            
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                system=system,
                messages=api_messages,
            )
            return resp.content[0].text
        
        # ── OpenAI ────────────────────────────────────────────────────────────
        elif provider == "openai":
            from openai import OpenAI
            key = st.session_state.get("api_key") or st.secrets.get("OPENAI_API_KEY", "")
            client = OpenAI(api_key=key)
            
            api_messages = [{"role": "system", "content": system}] if system else []
            for m in messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            if image_b64:
                api_messages[-1]["content"] = [
                    {"type": "text", "text": messages[-1]["content"]},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                ]
            
            resp = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=800,
                messages=api_messages,
            )
            return resp.choices[0].message.content
        
        # ── Ollama (本地) ─────────────────────────────────────────────────────
        elif provider == "ollama":
            import requests
            base_url = st.session_state.get("ollama_url", "http://localhost:11434")
            model    = st.session_state.get("ollama_model", "llama3")
            
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system}] + messages if system else messages,
                "stream": False,
            }
            resp = requests.post(f"{base_url}/api/chat", json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json()["message"]["content"]
    
    except Exception as e:
        return f"⚠️ 调用失败：{e}\n\n请在设置中检查 API 密钥或服务地址。"


# ═══════════════════════════════════════════════════════════════════════════════
# MOBILE CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

/* ── Reset & base ─────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif !important;
}
.main .block-container {
    max-width: 430px !important;
    padding: 0 0 90px 0 !important;
    margin: 0 auto !important;
}
.main { background: #f0f4ff; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ── Status bar ───────────────────────────────────── */
.status-bar {
    background: #fff;
    padding: 12px 20px 8px;
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #e8ecf4;
    position: sticky; top: 0; z-index: 100;
}
.app-title { font-size: 18px; font-weight: 800; color: #1a1f3d; }
.status-icons { font-size: 13px; color: #64748b; }

/* ── Bottom Nav ───────────────────────────────────── */
.bottom-nav {
    position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
    width: 430px; max-width: 100vw;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    border-top: 1px solid #e8ecf4;
    display: flex; z-index: 999;
    padding: 8px 0 16px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.06);
}
.nav-item {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; gap: 3px;
    cursor: pointer; padding: 4px 0;
    color: #94a3b8; font-size: 11px; font-weight: 600;
    text-decoration: none;
}
.nav-item.active { color: #4f46e5; }
.nav-icon { font-size: 22px; line-height: 1; }

/* ── Cards ────────────────────────────────────────── */
.card {
    background: white;
    border-radius: 20px;
    padding: 18px 18px;
    margin: 10px 12px;
    box-shadow: 0 2px 12px rgba(99,102,241,0.06);
}
.card-sm {
    background: white;
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* ── Hero metric ──────────────────────────────────── */
.hero-card {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 24px;
    padding: 24px 22px;
    margin: 10px 12px;
    color: white;
    box-shadow: 0 8px 32px rgba(79,70,229,0.35);
}
.hero-label { font-size: 13px; opacity: 0.8; font-weight: 600; }
.hero-value { font-size: 52px; font-weight: 900; line-height: 1; margin: 4px 0; }
.hero-unit { font-size: 16px; opacity: 0.7; }
.hero-status { font-size: 13px; background: rgba(255,255,255,0.2); 
               display: inline-block; padding: 3px 10px; border-radius: 99px; margin-top: 8px; }

/* ── Mini metric grid ─────────────────────────────── */
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 0 12px; }
.metric-mini {
    background: white; border-radius: 16px; padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.metric-mini-label { font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-mini-val { font-size: 26px; font-weight: 800; color: #1a1f3d; line-height: 1.1; margin: 2px 0; }
.metric-mini-unit { font-size: 12px; color: #94a3b8; }
.dot-warn { width: 8px; height: 8px; border-radius: 50%; background: #f59e0b; display: inline-block; margin-right: 4px; }
.dot-ok   { width: 8px; height: 8px; border-radius: 50%; background: #10b981; display: inline-block; margin-right: 4px; }
.dot-bad  { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; display: inline-block; margin-right: 4px; }

/* ── Section header ───────────────────────────────── */
.sec-header { font-size: 17px; font-weight: 800; color: #1a1f3d; 
              padding: 8px 18px 4px; margin-top: 4px; }

/* ── Med row ──────────────────────────────────────── */
.med-row {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 0; border-bottom: 1px solid #f1f5f9;
}
.med-icon-wrap {
    width: 44px; height: 44px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
    flex-shrink: 0;
}
.med-name  { font-size: 15px; font-weight: 700; color: #1a1f3d; }
.med-dose  { font-size: 12px; color: #94a3b8; }
.med-time  { font-size: 12px; color: #6366f1; font-weight: 600; }

/* ── Chat ─────────────────────────────────────────── */
.bubble-user {
    background: #4f46e5; color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 11px 15px; margin: 6px 0 6px 48px;
    font-size: 14px; line-height: 1.5;
    box-shadow: 0 4px 12px rgba(79,70,229,0.25);
}
.bubble-ai {
    background: white; color: #1a1f3d;
    border-radius: 18px 18px 18px 4px;
    padding: 11px 15px; margin: 6px 48px 6px 0;
    font-size: 14px; line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.chat-avatar { font-size: 22px; vertical-align: middle; margin-right: 6px; }

/* ── Points ───────────────────────────────────────── */
.points-hero {
    background: linear-gradient(135deg, #f59e0b, #ef4444);
    border-radius: 24px; padding: 22px; margin: 10px 12px; color: white;
    box-shadow: 0 8px 28px rgba(245,158,11,0.3);
}

/* ── Chip ─────────────────────────────────────────── */
.chip { display: inline-block; padding: 3px 10px; border-radius: 99px; font-size: 12px; font-weight: 700; }
.chip-warn { background:#fef3c7; color:#d97706; }
.chip-ok   { background:#dcfce7; color:#16a34a; }
.chip-bad  { background:#fee2e2; color:#dc2626; }
.chip-blue { background:#dbeafe; color:#2563eb; }

/* ── Fix Streamlit inputs inside card ────────────── */
.stChatInput { position: fixed; bottom: 65px; left: 50%; transform: translateX(-50%); 
               width: 426px; max-width: 100vw; background: white; padding: 0 8px; 
               border-top: 1px solid #e8ecf4; z-index: 998; }
.stButton>button { border-radius: 12px; font-weight: 700; font-family: 'Nunito', sans-serif !important; }
.stTabs [role="tab"] { font-weight: 700; }
.stRadio label { font-weight: 600; }
div[data-testid="stPlotlyChart"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
defaults = {
    "page": "home",
    "messages": [],
    "points": 1280,
    "meds_taken": {},
    "provider": "anthropic",
    "api_key": "",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK DATA
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def gen_data():
    dates = [datetime.now() - timedelta(days=29-i) for i in range(30)]
    rng = random.Random(42)
    return pd.DataFrame({
        "date": dates,
        "bg_fast":   [rng.uniform(5.8, 7.2) for _ in dates],
        "bg_post":   [rng.uniform(7.5, 10.5) for _ in dates],
        "bp_sys":    [rng.uniform(128, 155) for _ in dates],
        "bp_dia":    [rng.uniform(78, 96) for _ in dates],
        "chol":      [rng.uniform(4.8, 6.5) for _ in dates],
        "ldl":       [rng.uniform(2.8, 4.2) for _ in dates],
    })

df = gen_data()

MEDS = [
    {"name": "二甲双胍",   "dose": "0.5g",  "times": ["早餐后", "晚餐后"], "color": "#ede9fe", "icon": "💊"},
    {"name": "氨氯地平",   "dose": "5mg",   "times": ["早餐后"],           "color": "#dcfce7", "icon": "🩵"},
    {"name": "阿托伐他汀", "dose": "20mg",  "times": ["睡前"],             "color": "#fef3c7", "icon": "🌙"},
    {"name": "阿司匹林",   "dose": "100mg", "times": ["早餐后"],           "color": "#fee2e2", "icon": "❤️"},
]

PATIENT = {"name": "张伟", "age": 52, "conditions": ["2型糖尿病", "高血压", "血脂异常"]}

SYSTEM_PROMPT = f"""你是患者{PATIENT['name']}（{PATIENT['age']}岁）的专属AI健康顾问。
患者诊断：{', '.join(PATIENT['conditions'])}，BMI 27.3，HbA1c 7.2%。
当前用药：二甲双胍0.5g bid，氨氯地平5mg qd，阿托伐他汀20mg qn，阿司匹林100mg qd。
请用温和友好的中文回答，给出具体可操作的建议，每次回答不超过150字。"""

COMMUNITY = [
    {"user": "李大妈 👵", "text": "坚持低糖饮食3个月，血糖从8.5→6.8！💪", "likes": 42, "ago": "2小时前"},
    {"user": "王先生 🧑", "text": "推荐：芹菜炒木耳，控血压效果不错～", "likes": 28, "ago": "5小时前"},
    {"user": "陈护士 👩‍⚕️", "text": "高温天血压容易波动，多喝水、少运动🌡️", "likes": 67, "ago": "昨天"},
    {"user": "赵叔叔 🧓", "text": "连续服药30天达标！积分兑了血糖仪耗材🎁", "likes": 55, "ago": "昨天"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def phone_header(title, subtitle=""):
    now = datetime.now()
    st.markdown(f"""
    <div class="status-bar">
        <div>
            <div class="app-title">{title}</div>
            {"<div style='font-size:12px;color:#94a3b8'>" + subtitle + "</div>" if subtitle else ""}
        </div>
        <div class="status-icons">{now.strftime('%H:%M')} 🔋</div>
    </div>
    """, unsafe_allow_html=True)


def bottom_nav():
    nav_items = [
        ("home",      "🏠", "档案"),
        ("meds",      "💊", "用药"),
        ("ai",        "🤖", "AI"),
        ("community", "👥", "社群"),
        ("settings",  "⚙️",  "设置"),
    ]

    # CSS: fix the nav container to bottom of viewport
    st.markdown("""
    <style>
    /* Give page enough bottom padding so content isn't hidden behind nav */
    .main .block-container { padding-bottom: 100px !important; }

    /* Target the nav container by its data-key attribute */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stHorizontalBlock"] button[data-testid^="stBaseButton"]) {
        position: fixed !important;
        bottom: 0 !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 430px !important;
        max-width: 100vw !important;
        background: rgba(255,255,255,0.97) !important;
        backdrop-filter: blur(14px) !important;
        border-top: 1px solid #e8ecf4 !important;
        padding: 6px 8px 16px !important;
        box-shadow: 0 -4px 24px rgba(0,0,0,0.07) !important;
        z-index: 9999 !important;
    }

    /* Style all nav buttons */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stHorizontalBlock"] button[data-testid^="stBaseButton"]) button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        border-radius: 10px !important;
        padding: 6px 4px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #94a3b8 !important;
        line-height: 1.4 !important;
        min-height: 0 !important;
        height: auto !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stHorizontalBlock"] button[data-testid^="stBaseButton"]) button:hover {
        background: #f1f0ff !important;
        color: #4f46e5 !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stHorizontalBlock"] button[data-testid^="stBaseButton"]) button[kind="primary"] {
        color: #4f46e5 !important;
        background: #ede9fe !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(div[data-testid="stHorizontalBlock"] button[data-testid^="stBaseButton"]) button p {
        font-size: 11px !important;
        margin: 0 !important;
        color: inherit !important;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    for col, (key, icon, label) in zip(cols, nav_items):
        is_active = st.session_state.page == key
        with col:
            if st.button(
                f"{icon}\n{label}",
                key=f"nav_{key}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.page = key
                st.rerun()


def mini_chart(y_data, color, height=120, reference=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=y_data[-14:], mode="lines",
        line=dict(color=color, width=2.5, shape="spline"),
        fill="tozeroy", fillcolor=color.replace(")", ",0.12)").replace("rgb", "rgba"),
    ))
    if reference:
        fig.add_hline(y=reference, line_dash="dot", line_color="#ef4444", line_width=1.5)
    fig.update_layout(
        height=height, margin=dict(l=0,r=0,t=4,b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(visible=False), yaxis=dict(visible=False, range=[min(y_data)*0.95, max(y_data)*1.05]),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══════════════════════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════════════════════

# ── HOME ───────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    phone_header("健康档案", f"{'、'.join(PATIENT['conditions'])}")
    
    latest = df.iloc[-1]
    bg_status = "偏高 ⚠️" if latest.bg_fast > 6.1 else "正常 ✅"
    bg_color = "#f59e0b" if latest.bg_fast > 6.1 else "#10b981"
    
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-label">📅 {datetime.now().strftime('%m月%d日')} · 空腹血糖</div>
        <div class="hero-value">{latest.bg_fast:.1f}<span class="hero-unit"> mmol/L</span></div>
        <span class="hero-status">{bg_status}</span>
        <div style="float:right;font-size:13px;opacity:0.7;margin-top:-28px">近14天趋势</div>
    </div>
    """, unsafe_allow_html=True)
    
    # mini chart inside card
    with st.container():
        st.markdown('<div style="margin: -8px 12px 0">', unsafe_allow_html=True)
        mini_chart(df.bg_fast.tolist(), "rgb(79,70,229)", height=100, reference=6.1)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 2x2 metric grid
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    metrics = [
        ("收缩压", f"{latest.bp_sys:.0f}", "mmHg", latest.bp_sys > 140),
        ("总胆固醇", f"{latest.chol:.1f}", "mmol/L", latest.chol > 5.2),
        ("餐后血糖", f"{latest.bg_post:.1f}", "mmol/L", latest.bg_post > 7.8),
        ("HbA1c",   "7.2", "%", True),
    ]
    for label, val, unit, warn in metrics:
        dot = "dot-warn" if warn else "dot-ok"
        st.markdown(f"""
        <div class="metric-mini">
            <div class="metric-mini-label"><span class="{dot}"></span>{label}</div>
            <div class="metric-mini-val">{val}</div>
            <div class="metric-mini-unit">{unit}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detail chart
    st.markdown('<div class="sec-header">📈 详细趋势</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="margin:0 12px">', unsafe_allow_html=True)
        chart_choice = st.selectbox("", ["血糖", "血压", "血脂"], label_visibility="collapsed")
        
        fig = go.Figure()
        if chart_choice == "血糖":
            fig.add_trace(go.Scatter(x=df.date, y=df.bg_fast, name="空腹", line=dict(color="#4f46e5", width=2.5)))
            fig.add_trace(go.Scatter(x=df.date, y=df.bg_post, name="餐后", line=dict(color="#f59e0b", width=2, dash="dot")))
            fig.add_hline(y=6.1, line_dash="dash", line_color="#ef4444", opacity=0.4)
        elif chart_choice == "血压":
            fig.add_trace(go.Scatter(x=df.date, y=df.bp_sys, name="收缩压", line=dict(color="#ef4444", width=2.5)))
            fig.add_trace(go.Scatter(x=df.date, y=df.bp_dia, name="舒张压", line=dict(color="#6366f1", width=2)))
            fig.add_hline(y=140, line_dash="dash", line_color="#ef4444", opacity=0.4)
        else:
            fig.add_trace(go.Scatter(x=df.date, y=df.chol, name="总胆固醇", line=dict(color="#8b5cf6", width=2.5)))
            fig.add_trace(go.Scatter(x=df.date, y=df.ldl, name="LDL", line=dict(color="#ef4444", width=2, dash="dot")))
        
        fig.update_layout(
            height=200, margin=dict(l=0,r=0,t=10,b=0),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.15, x=0),
            xaxis=dict(showgrid=False, tickformat="%m/%d"),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
            font=dict(family="Nunito"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)


# ── MEDS ──────────────────────────────────────────────────────────────────────
elif st.session_state.page == "meds":
    phone_header("今日用药", datetime.now().strftime("%m月%d日"))
    
    total = sum(len(m["times"]) for m in MEDS)
    taken = len(st.session_state.meds_taken)
    
    st.markdown(f"""
    <div class="hero-card" style="background:linear-gradient(135deg,#10b981,#059669)">
        <div class="hero-label">今日服药进度</div>
        <div style="display:flex;align-items:baseline;gap:6px">
            <div class="hero-value">{taken}</div>
            <div class="hero-unit">/ {total} 次</div>
        </div>
        <div style="background:rgba(255,255,255,0.25);border-radius:99px;height:8px;margin-top:10px">
            <div style="background:white;border-radius:99px;height:8px;width:{taken/total*100:.0f}%;transition:width 0.5s"></div>
        </div>
        <div style="font-size:13px;opacity:0.8;margin-top:8px">
            {"🎉 全部完成！今日 +20积分" if taken == total else f"还剩 {total-taken} 次待服用"}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sec-header">💊 用药清单</div>', unsafe_allow_html=True)
    
    for med in MEDS:
        for time_label in med["times"]:
            key = f"{med['name']}_{time_label}"
            done = key in st.session_state.meds_taken
            
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div class="med-row" style="{'opacity:0.45' if done else ''}">
                    <div class="med-icon-wrap" style="background:{med['color']}">{med['icon']}</div>
                    <div>
                        <div class="med-name">{med['name']} <span style="font-size:12px;color:#94a3b8;font-weight:400">{med['dose']}</span></div>
                        <div class="med-time">⏰ {time_label}</div>
                        {"<div style='margin-top:3px'><span class='chip chip-ok'>✓ 已服用</span></div>" if done else ""}
                    </div>
                </div>""", unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div style='padding-top:8px'>", unsafe_allow_html=True)
                if not done:
                    if st.button("✓", key=f"take_{key}", help="标记已服", type="primary"):
                        st.session_state.meds_taken[key] = True
                        st.session_state.points += 5
                        st.rerun()
                else:
                    if st.button("↩", key=f"undo_{key}", help="撤销"):
                        del st.session_state.meds_taken[key]
                        st.session_state.points -= 5
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ── AI ────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "ai":
    phone_header("AI 健康助手", f"使用 {[k for k,v in PROVIDERS.items() if v==st.session_state.provider][0]}")
    
    tab1, tab2 = st.tabs(["💬 问答", "📸 食物识别"])
    
    with tab1:
        # Quick chips
        st.markdown('<div style="padding:8px 14px;display:flex;gap:8px;flex-wrap:wrap">', unsafe_allow_html=True)
        quick_qs = ["今天早餐吃什么？", "血糖偏高怎么办？", "可以喝咖啡吗？", "如何快走降压？"]
        cols = st.columns(2)
        for i, q in enumerate(quick_qs):
            with cols[i % 2]:
                if st.button(q, key=f"qb_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": q})
                    with st.spinner("思考中..."):
                        reply = get_llm_response(st.session_state.messages, SYSTEM_PROMPT)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Message display
        for msg in st.session_state.messages[-20:]:
            if msg["role"] == "user":
                st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
        
        if st.session_state.messages:
            if st.button("清空对话 🗑️"):
                st.session_state.messages = []
                st.rerun()
        
        user_input = st.chat_input("问我任何健康问题...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner(""):
                reply = get_llm_response(st.session_state.messages, SYSTEM_PROMPT)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
    
    with tab2:
        st.markdown('<div style="padding:12px 14px">', unsafe_allow_html=True)
        st.markdown("上传食物图片，AI 分析**升糖指数**和饮食建议 🍱")
        uploaded = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")
        
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, use_container_width=True)
            
            with st.spinner("识别中..."):
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                
                prompt = "分析这张食物图：1)食物名称 2)升糖指数GI及等级（低/中/高）3)建议份量 4)糖尿病患者建议 5)总评（✅适合/⚠️适量/❌不建议）。简洁分点列出，中文。"
                
                result = get_llm_response(
                    [{"role": "user", "content": prompt}],
                    system="你是营养和糖尿病饮食专家。",
                    image_b64=b64,
                )
            
            st.markdown(f"""
            <div class="card">
                <div style="font-weight:800;font-size:15px;margin-bottom:8px">🍽️ 分析结果</div>
                <div style="font-size:14px;line-height:1.7;color:#374151">{result.replace(chr(10), '<br>')}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


# ── COMMUNITY ─────────────────────────────────────────────────────────────────
elif st.session_state.page == "community":
    phone_header("健康社群")
    
    st.markdown(f"""
    <div class="points-hero">
        <div style="font-size:13px;opacity:0.85;font-weight:600">🌟 我的积分</div>
        <div style="font-size:52px;font-weight:900;line-height:1;margin:4px 0">{st.session_state.points}</div>
        <div style="font-size:12px;opacity:0.7">pts · 距下个奖励还差 {max(0,1500-st.session_state.points)} pts</div>
        <div style="background:rgba(255,255,255,0.3);border-radius:99px;height:6px;margin-top:10px">
            <div style="background:white;border-radius:99px;height:6px;width:{min(100,st.session_state.points/1500*100):.0f}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab_feed, tab_shop = st.tabs(["📰 动态", "🎁 积分商城"])
    
    with tab_feed:
        new = st.text_area("💬 分享健康心得...", height=70, placeholder="今天血糖控制得很好！")
        if st.button("发布 +10积分", type="primary", use_container_width=True):
            if new.strip():
                st.session_state.points += 10
                st.success("发布成功 +10积分！🎉")
        
        for p in COMMUNITY:
            st.markdown(f"""
            <div class="card" style="margin:8px 12px">
                <div style="font-weight:700;font-size:14px">{p['user']} <span style="color:#94a3b8;font-size:11px;font-weight:400">· {p['ago']}</span></div>
                <div style="margin:6px 0;font-size:14px;line-height:1.6;color:#374151">{p['text']}</div>
                <div style="color:#94a3b8;font-size:12px">❤️ {p['likes']}  •  💬 回复  •  🔗 分享</div>
            </div>""", unsafe_allow_html=True)
    
    with tab_shop:
        rewards = [
            ("🩸", "血糖试纸（50片）", 500),
            ("📚", "健康食谱书", 800),
            ("💊", "血压计耗材包", 1200),
            ("👨‍⚕️", "在线问诊1次", 2000),
        ]
        for icon, name, cost in rewards:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
                <div style="padding:12px 0;border-bottom:1px solid #f1f5f9">
                    <div style="font-size:22px;display:inline">{icon}</div>
                    <div style="display:inline;margin-left:8px">
                        <span style="font-weight:700;font-size:14px">{name}</span><br>
                        <span style="font-size:13px;color:#6366f1;font-weight:600">{cost} pts</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
                can = st.session_state.points >= cost
                if st.button("兑" if can else "🔒", key=f"r_{name}", 
                             type="primary" if can else "secondary",
                             disabled=not can):
                    st.session_state.points -= cost
                    st.success(f"{icon} 兑换成功！")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ── SETTINGS ──────────────────────────────────────────────────────────────────
elif st.session_state.page == "settings":
    phone_header("设置")
    
    st.markdown('<div class="sec-header">🤖 AI 模型配置</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div style="padding:0 12px">', unsafe_allow_html=True)
        
        prov_name = st.radio(
            "选择 LLM 提供商",
            list(PROVIDERS.keys()),
            index=list(PROVIDERS.values()).index(st.session_state.provider),
        )
        st.session_state.provider = PROVIDERS[prov_name]
        
        st.markdown("---")
        
        if st.session_state.provider == "anthropic":
            st.markdown("**Anthropic API Key**")
            st.markdown("在 [console.anthropic.com](https://console.anthropic.com) 获取")
            key = st.text_input("API Key", value=st.session_state.api_key, type="password", placeholder="sk-ant-...")
            st.session_state.api_key = key
            st.info("💡 **Streamlit Cloud 托管**：将密钥添加到 App Settings → Secrets\n```\nANTHROPIC_API_KEY = 'sk-ant-...'\n```")
        
        elif st.session_state.provider == "openai":
            st.markdown("**OpenAI API Key**")
            st.markdown("在 [platform.openai.com](https://platform.openai.com) 获取")
            key = st.text_input("API Key", value=st.session_state.api_key, type="password", placeholder="sk-...")
            st.session_state.api_key = key
            st.info("💡 **Streamlit Cloud 托管**：\n```\nOPENAI_API_KEY = 'sk-...'\n```")
        
        elif st.session_state.provider == "ollama":
            st.markdown("**Ollama 本地服务**")
            url = st.text_input("服务地址", value=st.session_state.ollama_url, placeholder="http://localhost:11434")
            model = st.text_input("模型名称", value=st.session_state.ollama_model, placeholder="llama3 / qwen2 / mistral")
            st.session_state.ollama_url = url
            st.session_state.ollama_model = model
            st.warning("⚠️ Ollama 仅支持**本地运行**，无法托管到 Streamlit Cloud。")
            st.markdown("""
            **本地启动方式：**
            ```bash
            ollama pull llama3
            ollama serve
            streamlit run app.py
            ```
            """)
        
        st.markdown("---")
        st.markdown('<div class="sec-header" style="padding:0">🚀 Streamlit Cloud 托管指南</div>', unsafe_allow_html=True)
        st.markdown("""
        1. 将代码推到 **GitHub** 仓库
        2. 登录 [share.streamlit.io](https://share.streamlit.io) → New App
        3. 选择仓库和 `app.py`
        4. 在 **Advanced → Secrets** 中填入 API 密钥
        5. Deploy ✅
        
        > **推荐**：Anthropic Claude 3.5 Sonnet 性价比最高，适合长期托管。
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)


# ── BOTTOM NAV — CSS-fixed to viewport bottom ────────────────────────────────
bottom_nav()