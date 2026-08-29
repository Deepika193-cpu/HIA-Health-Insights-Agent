"""
Centralized design system for HIA.

Every screen (login/signup, welcome, sidebar, analysis form, chat) pulls its
colors, spacing, and component styles from here so the app reads as one
consistent product instead of a set of ad-hoc st.markdown() blocks.

Usage: call `inject_global_css()` once, as early as possible in the run
(right after st.set_page_config), and it applies to every screen for the
rest of the session.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PRIMARY_COLOR = "#1976D2"       # deep blue - primary actions, links
PRIMARY_LIGHT = "#64B5F6"       # light blue - accents, secondary text
PRIMARY_SOFT = "rgba(100, 181, 246, 0.10)"   # tint for cards/badges
PRIMARY_SOFT_BORDER = "rgba(100, 181, 246, 0.28)"

BG_GRADIENT = "linear-gradient(135deg, #F4F9FF 0%, #FFFFFF 45%, #F0F6FF 100%)"
CARD_BG = "#FFFFFF"
CARD_BORDER = "rgba(25, 118, 210, 0.12)"
CARD_SHADOW = "0 4px 18px rgba(25, 118, 210, 0.08)"

TEXT_MAIN = "#173049"
TEXT_MUTED = "#5B7186"

SUCCESS_COLOR = "#2E9E6B"
SUCCESS_SOFT = "rgba(46, 158, 107, 0.10)"
WARNING_COLOR = "#E0952B"
WARNING_SOFT = "rgba(224, 149, 43, 0.12)"
ERROR_COLOR = "#E0524B"
ERROR_SOFT = "rgba(224, 82, 75, 0.10)"

RADIUS = "14px"
RADIUS_SM = "10px"

FONT_STACK = "'Source Sans Pro', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"

# Ordered so the UI can render a consistent "cascade" step list.
MODEL_TIER_LABELS = {
    "primary": "Primary",
    "secondary": "Secondary",
    "tertiary": "Tertiary",
    "fallback": "Fallback",
}


def inject_global_css():
    """Inject one shared stylesheet used by every screen in the app."""
    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: {FONT_STACK};
        }}

        /* App background */
        [data-testid="stAppViewContainer"] {{
            background: {BG_GRADIENT};
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}

        /* Hide native Streamlit form helper captions everywhere */
        div[data-testid="InputInstructions"] > span:nth-child(1) {{
            visibility: hidden;
        }}

        h1, h2, h3 {{
            color: {TEXT_MAIN};
            font-weight: 700;
        }}
        p, span, label {{
            color: {TEXT_MAIN};
        }}

        /* ---------- Buttons ---------- */
        .stButton > button {{
            border-radius: {RADIUS_SM};
            border: 1px solid {PRIMARY_SOFT_BORDER};
            font-weight: 600;
            transition: all 0.15s ease;
        }}
        .stButton > button[kind="primary"] {{
            background: {PRIMARY_COLOR};
            border: none;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.25);
        }}
        .stButton > button[kind="primary"]:hover {{
            background: #145ea8;
            box-shadow: 0 4px 12px rgba(25, 118, 210, 0.32);
            transform: translateY(-1px);
        }}
        .stButton > button:hover {{
            border-color: {PRIMARY_COLOR};
            color: {PRIMARY_COLOR};
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input, .stNumberInput input, .stTextArea textarea {{
            border-radius: {RADIUS_SM} !important;
            border: 1px solid {CARD_BORDER} !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus {{
            border-color: {PRIMARY_LIGHT} !important;
            box-shadow: 0 0 0 2px {PRIMARY_SOFT} !important;
        }}
        div[data-baseweb="select"] > div {{
            border-radius: {RADIUS_SM} !important;
            border-color: {CARD_BORDER} !important;
        }}

        /* Radio pills (report source, specialist mode, etc.) */
        div[role="radiogroup"] {{
            gap: 0.4rem;
        }}
        div[role="radiogroup"] label {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            margin-right: 0.4rem;
        }}

        /* ---------- Cards ---------- */
        .hia-card {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: {RADIUS};
            box-shadow: {CARD_SHADOW};
            padding: 1.5rem;
        }}
        .hia-soft-card {{
            background: {PRIMARY_SOFT};
            border: 1px solid {PRIMARY_SOFT_BORDER};
            border-radius: {RADIUS_SM};
            padding: 0.85rem 1rem;
        }}

        /* ---------- Badges ---------- */
        .hia-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .hia-badge-primary {{ background: {PRIMARY_SOFT}; color: {PRIMARY_COLOR}; }}
        .hia-badge-success {{ background: {SUCCESS_SOFT}; color: {SUCCESS_COLOR}; }}
        .hia-badge-warning {{ background: {WARNING_SOFT}; color: {WARNING_COLOR}; }}
        .hia-badge-muted {{ background: rgba(91, 113, 134, 0.10); color: {TEXT_MUTED}; }}

        /* ---------- Expanders / uploader ---------- */
        [data-testid="stExpander"] {{
            border: 1px solid {CARD_BORDER};
            border-radius: {RADIUS_SM};
            background: {CARD_BG};
        }}
        [data-testid="stFileUploaderDropzone"] {{
            border-radius: {RADIUS_SM};
            border: 1.5px dashed {PRIMARY_SOFT_BORDER};
            background: {PRIMARY_SOFT};
        }}

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: #FBFDFF;
            border-right: 1px solid {CARD_BORDER};
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            text-align: left;
            justify-content: flex-start;
        }}

        /* ---------- Chat bubbles ---------- */
        .hia-chat-row {{
            display: flex;
            margin: 0.5rem 0;
        }}
        .hia-chat-row.user {{ justify-content: flex-end; }}
        .hia-chat-row.assistant {{ justify-content: flex-start; }}
        .hia-bubble {{
            max-width: 78%;
            padding: 0.75rem 1rem;
            border-radius: {RADIUS};
            line-height: 1.5;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.06);
        }}
        .hia-bubble.user {{
            background: {PRIMARY_COLOR};
            color: white;
            border-bottom-right-radius: 4px;
        }}
        .hia-bubble.assistant {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            color: {TEXT_MAIN};
            border-bottom-left-radius: 4px;
        }}
        .hia-bubble-label {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 0.25rem;
            display: block;
        }}

        /* ---------- Alerts: soften Streamlit defaults to match palette ---------- */
        div[data-testid="stAlertContentInfo"] {{ color: {TEXT_MAIN}; }}
        .stAlert {{
            border-radius: {RADIUS_SM};
        }}

        /* ---------- Divider ---------- */
        hr {{
            border-color: {CARD_BORDER};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_chat_bubble(role: str, content: str, label: str = None):
    """Render one chat message as a styled bubble instead of st.info/success."""
    css_role = "user" if role == "user" else "assistant"
    default_label = "You" if css_role == "user" else "HIA"
    label = label or default_label
    st.markdown(
        f"""
        <div class="hia-chat-row {css_role}">
            <div class="hia-bubble {css_role}">
                <span class="hia-bubble-label">{label}</span>
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge(text: str, kind: str = "primary"):
    st.markdown(
        f'<span class="hia-badge hia-badge-{kind}">{text}</span>',
        unsafe_allow_html=True,
    )
