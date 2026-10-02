"""
app.py
Streamlit front-end for the AI Meeting Agent — "Meridian".

Run with:
    python -m streamlit run src/app.py
"""

import sys
import textwrap
from datetime import datetime
from html import escape
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent import MeetingAgent

DEVELOPER = "Hamna Munir"

st.set_page_config(page_title="Meridian | AI Meeting Agent", page_icon="◐", layout="centered")

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
    :root {
        --ink: #0F1218;
        --panel: #171B23;
        --panel-2: #1D222C;
        --border: #262C38;
        --text: #ECE8DE;
        --muted: #8D95A6;
        --brass: #C9A227;
        --brass-soft: rgba(201, 162, 39, 0.14);
        --sage: #6FA787;
    }

    #MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        visibility: hidden;
        height: 0;
    }
    [data-testid="stSidebar"] { display: none; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background:
            radial-gradient(900px 380px at 50% -120px, rgba(201,162,39,0.08), transparent 70%),
            var(--ink);
        color: var(--text);
    }
    .block-container { max-width: 780px; padding-top: 1.6rem; padding-bottom: 9rem; }

    /* Lift the chat composer above the fixed footer */
    [data-testid="stBottom"] > div { padding-top: 1.4rem !important; padding-bottom: 2.9rem !important; background: linear-gradient(180deg, rgba(15,18,24,0) 0, #0F1218 1.2rem) !important; }

    /* ---------------- Header ---------------- */
    .mrd-header {
        display: flex; align-items: center; justify-content: space-between; gap: 1rem;
        padding: 1rem 1.2rem; border: 1px solid var(--border); border-radius: 14px;
        background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
    }
    .mrd-brand { display: flex; align-items: center; gap: 0.75rem; }
    .mrd-mark { width: 36px; height: 36px; flex-shrink: 0; }
    .mrd-wordmark { font-family: 'Fraunces', serif; font-size: 1.4rem; font-weight: 600; line-height: 1.1; }
    .mrd-tagline { font-size: 0.78rem; color: var(--muted); margin-top: 3px; }
    .mrd-pill {
        display: inline-flex; align-items: center; gap: 0.45rem; font-size: 0.78rem; font-weight: 500;
        border: 1px solid var(--border); border-radius: 999px; padding: 0.32rem 0.8rem;
        background: var(--ink); white-space: nowrap;
    }
    .mrd-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--brass); }
    .mrd-dot.done { background: var(--sage); }

    /* ---------------- Progress ---------------- */
    .mrd-steps { display: flex; align-items: center; margin: 1.1rem 0.2rem 1.5rem; }
    .mrd-step { display: flex; align-items: center; gap: 0.5rem; }
    .mrd-step-dot {
        width: 22px; height: 22px; border-radius: 50%; border: 1.5px solid var(--border);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; font-weight: 600; color: var(--muted); background: var(--ink);
    }
    .mrd-step-label { font-size: 0.8rem; color: var(--muted); }
    .mrd-step.active .mrd-step-dot { border-color: var(--brass); color: var(--brass); background: var(--brass-soft); }
    .mrd-step.active .mrd-step-label { color: var(--text); font-weight: 500; }
    .mrd-step.complete .mrd-step-dot { border-color: var(--sage); background: var(--sage); color: var(--ink); }
    .mrd-step.complete .mrd-step-label { color: var(--text); }
    .mrd-bar { flex: 1; height: 1.5px; background: var(--border); margin: 0 0.7rem; min-width: 14px; }
    .mrd-bar.complete { background: var(--sage); }

    /* ---------------- Hero (empty state) ---------------- */
    .mrd-hero {
        display: flex; align-items: center; justify-content: space-between; gap: 1.5rem;
        padding: 1.6rem 1.8rem; border: 1px solid var(--border); border-radius: 16px;
        background:
            radial-gradient(420px 220px at 90% 10%, rgba(201,162,39,0.10), transparent 70%),
            var(--panel);
    }
    .mrd-hero h1 {
        font-family: 'Fraunces', serif; font-weight: 500; font-size: 1.75rem; line-height: 1.2;
        margin: 0 0 0.6rem; padding: 0; color: var(--text);
    }
    .mrd-hero p { font-size: 0.93rem; line-height: 1.6; color: var(--muted); margin: 0; max-width: 360px; }
    .mrd-hero-art { width: 210px; flex-shrink: 0; }

    .mrd-features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 0.9rem 0 1.2rem; }
    .mrd-feature { border: 1px solid var(--border); border-radius: 12px; padding: 0.95rem; background: var(--panel); }
    .mrd-feature svg { width: 30px; height: 30px; margin-bottom: 0.55rem; display: block; }
    .mrd-feature-title { font-size: 0.88rem; font-weight: 600; margin-bottom: 0.2rem; }
    .mrd-feature-text { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }

    /* ---------------- Messages ---------------- */
    .mrd-log { display: flex; flex-direction: column; gap: 1.2rem; }
    .mrd-row { display: flex; gap: 0.7rem; max-width: 86%; align-items: flex-start; }
    .mrd-row.assistant { align-self: flex-start; }
    .mrd-row.user { align-self: flex-end; flex-direction: row-reverse; }
    .mrd-avatar {
        width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
        border: 1px solid var(--border); background: var(--panel);
        display: flex; align-items: center; justify-content: center;
    }
    .mrd-avatar svg { width: 20px; height: 20px; }
    .mrd-row.user .mrd-avatar { background: var(--brass-soft); border-color: rgba(201,162,39,0.35); }
    .mrd-col { display: flex; flex-direction: column; }
    .mrd-row.user .mrd-col { align-items: flex-end; }
    .mrd-who { font-size: 0.74rem; color: var(--muted); margin-bottom: 0.3rem; }
    .mrd-bubble { padding: 0.8rem 1rem; font-size: 0.94rem; line-height: 1.6; color: var(--text); }
    .mrd-row.assistant .mrd-bubble {
        background: var(--panel); border: 1px solid var(--border);
        border-left: 3px solid var(--brass); border-radius: 4px 12px 12px 12px;
    }
    .mrd-row.user .mrd-bubble {
        background: var(--brass-soft); border: 1px solid rgba(201,162,39,0.35); border-radius: 12px 4px 12px 12px;
    }

    /* ---------------- Composer ---------------- */
    [data-testid="stChatInput"] {
        max-width: 780px; margin: 0 auto;
        border: 1px solid var(--border) !important; background: var(--panel) !important; border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea { color: var(--text) !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stChatInput"]:focus-within { border-color: var(--brass) !important; box-shadow: 0 0 0 1px var(--brass) !important; }
    [data-testid="stChatInput"] button { background: var(--brass) !important; }
    [data-testid="stChatInput"] button svg { color: var(--ink) !important; }

    /* ---------------- Buttons ---------------- */
    div[data-testid="stButton"] button {
        background: transparent; color: var(--muted); border: 1px solid var(--border); border-radius: 999px;
        font-family: 'Inter', sans-serif; font-size: 0.78rem; padding: 0.3rem 0.85rem; width: 100%;
    }
    div[data-testid="stButton"] button:hover,
    div[data-testid="stButton"] button:focus-visible { border-color: var(--brass); color: var(--brass); }

    /* ---------------- Footer: pinned to the bottom of the screen ---------------- */
    .mrd-footer {
        position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000;
        display: flex; justify-content: center; align-items: center; gap: 0.7rem;
        padding: 0.6rem 1rem; background: var(--ink); border-top: 1px solid var(--border);
        font-size: 0.78rem; color: var(--muted);
    }
    .mrd-footer-sep { width: 1px; height: 12px; background: var(--border); }
    .mrd-footer strong { color: var(--brass); font-weight: 600; }

    /* ---------------- Hover motion ---------------- */
    .mrd-hero, .mrd-feature { transition: transform .3s ease, border-color .3s ease, box-shadow .3s ease; }
    .mrd-feature:hover { transform: translateY(-5px); border-color: var(--brass); box-shadow: 0 10px 24px rgba(0,0,0,0.35); }
    .mrd-hero:hover { border-color: rgba(201,162,39,0.55); }

    .h-cal, .h-clock, .h-tick, .h-shadow, .ic-cal, .ic-shield, .ic-dot {
        transition: transform .5s cubic-bezier(.3,1.4,.5,1), opacity .4s ease;
    }
    .h-cal { transform-origin: 96px 85px; }
    .h-clock { transform-origin: 158px 124px; }
    .h-hand { transform-origin: 158px 124px; }
    .h-tick { transform-origin: 186px 38px; }
    .h-shadow { transform-origin: 110px 158px; }
    .mrd-hero:hover .h-cal { transform: translateY(-9px) rotate(-2.5deg); }
    .mrd-hero:hover .h-clock { transform: translate(5px, 5px) scale(1.08); }
    .mrd-hero:hover .h-shadow { transform: scaleX(0.85); opacity: 0.6; }
    .mrd-hero:hover .h-hand { animation: mrd-spin 2.4s linear infinite; }
    .mrd-hero:hover .h-tick { animation: mrd-pop .6s ease; }
    .mrd-hero:hover .h-pulse { animation: mrd-blink 1.2s ease-in-out infinite; }

    .ic-cal { transform-origin: 16px 16px; }
    .ic-shield { transform-origin: 16px 16px; }
    .ic-hand { transform-origin: 16px 16px; }
    .ic-dot { opacity: 0; transform-origin: 16px 20px; transform: scale(0.2); }
    .ic-check { stroke-dasharray: 16; stroke-dashoffset: 0; }
    .mrd-feature:hover .ic-cal { transform: translateY(-3px) rotate(-5deg); }
    .mrd-feature:hover .ic-dot { opacity: 1; transform: scale(1); }
    .mrd-feature:hover .ic-shield { transform: scale(1.12); }
    .mrd-feature:hover .ic-check { animation: mrd-draw .6s ease forwards; }
    .mrd-feature:hover .ic-hand { animation: mrd-spin 2s linear infinite; }

    @keyframes mrd-spin { to { transform: rotate(360deg); } }
    @keyframes mrd-pop { 0% { transform: scale(1); } 50% { transform: scale(1.4); } 100% { transform: scale(1); } }
    @keyframes mrd-blink { 0%, 100% { opacity: 0.95; } 50% { opacity: 0.3; } }
    @keyframes mrd-draw { from { stroke-dashoffset: 16; } to { stroke-dashoffset: 0; } }

    /* Suggestion chips: wrap instead of cutting the text off */
    div[data-testid="stButton"] button { height: auto; min-height: 2.2rem; }
    div[data-testid="stButton"] button p { white-space: normal; line-height: 1.3; }

    @media (prefers-reduced-motion: reduce) {
        .mrd-hero *, .mrd-feature, .mrd-feature * { animation: none !important; transition: none !important; }
    }

    @media (max-width: 640px) {
        .mrd-header, .mrd-hero { flex-direction: column; align-items: flex-start; }
        .mrd-hero-art { width: 150px; }
        .mrd-features { grid-template-columns: 1fr; }
        .mrd-step-label { display: none; }
        .mrd-step.active .mrd-step-label { display: inline; }
        .mrd-row { max-width: 96%; }
        .mrd-footer-sep, .mrd-footer-app { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SVG assets
# ---------------------------------------------------------------------------
MARK_SVG = (
    '<svg class="mrd-mark" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="16" cy="16" r="12.5" stroke="#C9A227" stroke-width="1.4"/>'
    '<line x1="16" y1="16" x2="16" y2="6.5" stroke="#C9A227" stroke-width="1.4" stroke-linecap="round"/>'
    '<line x1="16" y1="16" x2="22" y2="19.5" stroke="#8D95A6" stroke-width="1.4" stroke-linecap="round"/>'
    '<circle cx="16" cy="16" r="1.6" fill="#C9A227"/>'
    "</svg>"
)

AVATAR_BOT = (
    '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="16" cy="16" r="11" stroke="#C9A227" stroke-width="1.8"/>'
    '<line x1="16" y1="16" x2="16" y2="9" stroke="#C9A227" stroke-width="1.8" stroke-linecap="round"/>'
    '<line x1="16" y1="16" x2="21" y2="19" stroke="#8D95A6" stroke-width="1.8" stroke-linecap="round"/>'
    "</svg>"
)

AVATAR_USER = (
    '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="16" cy="12" r="5" stroke="#C9A227" stroke-width="1.8"/>'
    '<path d="M6.5 26c1.2-5 5-7.5 9.5-7.5s8.3 2.5 9.5 7.5" stroke="#C9A227" stroke-width="1.8" stroke-linecap="round"/>'
    "</svg>"
)

HERO_SVG = (
    '<svg class="mrd-hero-art" viewBox="0 0 220 170" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse class="h-shadow" cx="110" cy="158" rx="78" ry="7" fill="#C9A227" opacity="0.10"/>'
    '<g class="h-cal">'
    '<rect x="26" y="26" width="140" height="118" rx="14" fill="#1D222C" stroke="#303746" stroke-width="1.5"/>'
    '<path d="M26 40c0-7.7 6.3-14 14-14h112c7.7 0 14 6.3 14 14v18H26V40z" fill="#C9A227"/>'
    '<rect x="52" y="14" width="8" height="24" rx="4" fill="#ECE8DE"/>'
    '<rect x="132" y="14" width="8" height="24" rx="4" fill="#ECE8DE"/>'
    '<g fill="#303746">'
    '<rect x="42" y="72" width="16" height="12" rx="3"/><rect x="66" y="72" width="16" height="12" rx="3"/>'
    '<rect x="90" y="72" width="16" height="12" rx="3"/><rect x="114" y="72" width="16" height="12" rx="3"/>'
    '<rect x="138" y="72" width="16" height="12" rx="3"/>'
    '<rect x="42" y="92" width="16" height="12" rx="3"/><rect x="66" y="92" width="16" height="12" rx="3"/>'
    '<rect x="138" y="92" width="16" height="12" rx="3"/>'
    '<rect x="42" y="112" width="16" height="12" rx="3"/><rect x="90" y="112" width="16" height="12" rx="3"/>'
    "</g>"
    '<rect class="h-pulse" x="90" y="92" width="16" height="12" rx="3" fill="#C9A227" opacity="0.9"/>'
    '<rect class="h-pulse" x="114" y="92" width="16" height="12" rx="3" fill="#6FA787" opacity="0.9"/>'
    "</g>"
    '<g class="h-clock">'
    '<circle cx="158" cy="124" r="32" fill="#12151B" stroke="#C9A227" stroke-width="2.5"/>'
    '<circle cx="158" cy="124" r="25" stroke="#303746" stroke-width="1.2"/>'
    '<line x1="158" y1="124" x2="171" y2="132" stroke="#C9A227" stroke-width="3" stroke-linecap="round"/>'
    '<g class="h-hand"><line x1="158" y1="124" x2="158" y2="106" stroke="#ECE8DE" stroke-width="3" stroke-linecap="round"/></g>'
    '<circle cx="158" cy="124" r="3.2" fill="#C9A227"/>'
    "</g>"
    '<g class="h-tick">'
    '<circle cx="186" cy="38" r="11" fill="#6FA787"/>'
    '<path d="M180.5 38.5l4 4 7-8" stroke="#0F1218" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    "</g>"
    "</svg>"
)

ICON_CALENDAR = (
    '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<g class="ic-cal">'
    '<rect x="5" y="7" width="22" height="19" rx="3.5" stroke="#C9A227" stroke-width="1.8"/>'
    '<line x1="5" y1="13" x2="27" y2="13" stroke="#C9A227" stroke-width="1.8"/>'
    '<line x1="11" y1="4.5" x2="11" y2="9" stroke="#C9A227" stroke-width="1.8" stroke-linecap="round"/>'
    '<line x1="21" y1="4.5" x2="21" y2="9" stroke="#C9A227" stroke-width="1.8" stroke-linecap="round"/>'
    '<circle class="ic-dot" cx="16" cy="20" r="2.2" fill="#C9A227"/>'
    "</g></svg>"
)

ICON_APPROVAL = (
    '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<g class="ic-shield">'
    '<path d="M16 4l9.5 3.5v7.2c0 6.1-4 10.6-9.5 13.3-5.5-2.7-9.5-7.2-9.5-13.3V7.5L16 4z" stroke="#6FA787" stroke-width="1.8" stroke-linejoin="round"/>'
    '<path class="ic-check" d="M11.5 16l3.2 3.2 6-6.4" stroke="#6FA787" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    "</g></svg>"
)

ICON_EVENT = (
    '<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="16" cy="16" r="11.5" stroke="#C9A227" stroke-width="1.8"/>'
    '<path d="M16 16l4.5 2.8" stroke="#C9A227" stroke-width="1.8" stroke-linecap="round"/>'
    '<g class="ic-hand"><path d="M16 9.5V16" stroke="#C9A227" stroke-width="1.8" stroke-linecap="round"/></g>'
    "</svg>"
)


def render_html(fragment: str) -> None:
    """Collapse HTML to a single line so Streamlit's markdown parser never
    mistakes indented tags for a code block."""
    collapsed = " ".join(line.strip() for line in textwrap.dedent(fragment).splitlines())
    st.markdown(collapsed, unsafe_allow_html=True)


STAGE_LABELS = {
    "idle": "Ready",
    "collecting": "Gathering details",
    "offering_slots": "Waiting for your choice",
    "confirming": "Waiting for confirmation",
    "done": "Meeting booked",
}

# The booking flow is a real sequence, so a stepper shows where the user is.
STEPS = ["Details", "Pick a time", "Confirm", "Booked"]
STAGE_TO_STEP = {"idle": 0, "collecting": 0, "offering_slots": 1, "confirming": 2, "done": 3}

SUGGESTIONS = [
    "30-minute meeting with Ali tomorrow afternoon",
    "Team sync on Friday morning",
    "1-hour call with Sara next week",
]


def steps_html(stage: str) -> str:
    current = STAGE_TO_STEP.get(stage, 0)
    all_done = stage == "done"
    parts = []
    for i, label in enumerate(STEPS):
        if all_done or i < current:
            state, mark = "complete", "✓"
        elif i == current:
            state, mark = "active", str(i + 1)
        else:
            state, mark = "", str(i + 1)
        parts.append(
            f'<div class="mrd-step {state}"><span class="mrd-step-dot">{mark}</span>'
            f'<span class="mrd-step-label">{label}</span></div>'
        )
        if i < len(STEPS) - 1:
            bar = "complete" if (all_done or i < current) else ""
            parts.append(f'<div class="mrd-bar {bar}"></div>')
    return f'<div class="mrd-steps">{"".join(parts)}</div>'


def feature(icon: str, title: str, text: str) -> str:
    return (
        f'<div class="mrd-feature">{icon}'
        f'<div class="mrd-feature-title">{title}</div>'
        f'<div class="mrd-feature-text">{text}</div></div>'
    )


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "agent" not in st.session_state:
    with st.spinner("Connecting to Google Calendar…"):
        st.session_state.agent = MeetingAgent()
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": 'Tell me about the meeting you\'d like to schedule, for example: "30-minute meeting with Ali tomorrow afternoon."',
            "time": datetime.now().strftime("%H:%M"),
        }
    ]

agent = st.session_state.agent
stage = agent.state.stage
stage_label = STAGE_LABELS.get(stage, stage)
dot_class = "done" if stage == "done" else ""


def send(text: str) -> None:
    st.session_state.messages.append(
        {"role": "user", "content": text, "time": datetime.now().strftime("%H:%M")}
    )
    with st.spinner("Checking your calendar…"):
        reply = agent.handle_message(text)
    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "time": datetime.now().strftime("%H:%M")}
    )
    st.rerun()


# ---------------------------------------------------------------------------
# Header + progress
# ---------------------------------------------------------------------------
render_html(
    f"""
    <div class="mrd-header">
        <div class="mrd-brand">
            {MARK_SVG}
            <div>
                <div class="mrd-wordmark">Meridian</div>
                <div class="mrd-tagline">Real calendar. Real approval. Real event.</div>
            </div>
        </div>
        <span class="mrd-pill"><span class="mrd-dot {dot_class}"></span>{stage_label}</span>
    </div>
    """
)
render_html(steps_html(stage))

_, reset_col = st.columns([6, 1])
with reset_col:
    if st.button("Start over", key="reset_btn"):
        del st.session_state["agent"]
        del st.session_state["messages"]
        st.rerun()

# ---------------------------------------------------------------------------
# Empty state: hero illustration, feature cards, example requests
# ---------------------------------------------------------------------------
is_empty = len(st.session_state.messages) == 1

if is_empty:
    render_html(
        f"""
        <div class="mrd-hero">
            <div>
                <h1>Book a meeting in one sentence</h1>
                <p>Describe who, when and how long. Meridian checks your Google Calendar,
                offers open slots and creates the event once you approve.</p>
            </div>
            {HERO_SVG}
        </div>
        <div class="mrd-features">
            {feature(ICON_CALENDAR, "Real calendar", "Reads your actual Google Calendar for free time.")}
            {feature(ICON_APPROVAL, "Real approval", "Nothing is booked until you confirm.")}
            {feature(ICON_EVENT, "Real event", "The confirmed meeting appears on your calendar.")}
        </div>
        """
    )

# ---------------------------------------------------------------------------
# Message log
# ---------------------------------------------------------------------------
log_html = ['<div class="mrd-log">']
for msg in st.session_state.messages:
    role = msg["role"]
    who = "Meridian" if role == "assistant" else "You"
    avatar = AVATAR_BOT if role == "assistant" else AVATAR_USER
    safe_content = escape(msg["content"]).replace("\n", "<br>")
    log_html.append(
        f'<div class="mrd-row {role}">'
        f'<div class="mrd-avatar">{avatar}</div>'
        f'<div class="mrd-col"><div class="mrd-who">{who}, {msg["time"]}</div>'
        f'<div class="mrd-bubble">{safe_content}</div></div>'
        f"</div>"
    )
log_html.append("</div>")
st.markdown("".join(log_html), unsafe_allow_html=True)

if is_empty:
    st.write("")
    cols = st.columns(len(SUGGESTIONS))
    for i, (col, text) in enumerate(zip(cols, SUGGESTIONS)):
        with col:
            if st.button(text, key=f"suggest_{i}"):
                send(text)

# ---------------------------------------------------------------------------
# Footer (fixed to the bottom of the screen, below the message box)
# ---------------------------------------------------------------------------
render_html(
    f"""
    <div class="mrd-footer">
        <span class="mrd-footer-app">Meridian AI Meeting Agent</span>
        <span class="mrd-footer-sep"></span>
        <span>Developed by <strong>{DEVELOPER}</strong></span>
    </div>
    """
)

# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------
user_input = st.chat_input("Describe your meeting request…")

if user_input:
    send(user_input)