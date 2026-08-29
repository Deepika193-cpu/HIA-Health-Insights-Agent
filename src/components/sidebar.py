import streamlit as st
from auth.session_manager import SessionManager
from components.footer import show_footer
from config.app_config import ANALYSIS_DAILY_LIMIT
from config.theme import PRIMARY_COLOR, ERROR_COLOR
from agents.model_manager import ModelManager, ModelTier

# Speed/quality preference shown to the user, mapped to a cascade starting tier.
TIER_PREFERENCES = {
    "Auto (recommended)": None,
    "Fastest": ModelTier.TERTIARY,
    "Balanced": ModelTier.SECONDARY,
    "Most Powerful": ModelTier.PRIMARY,
}


def show_sidebar():
    with st.sidebar:
        st.title("💬 Chat Sessions")

        if st.button("+ New Analysis Session", use_container_width=True, type="primary"):
            if st.session_state.user and 'id' in st.session_state.user:
                success, session = SessionManager.create_chat_session()
                if success:
                    st.session_state.current_session = session
                    st.rerun()
                else:
                    st.error("Failed to create session")
            else:
                st.error("Please log in again")
                SessionManager.logout()
                st.rerun()

        render_daily_limit_card()

        st.markdown("---")
        show_session_list()

        st.markdown("---")
        render_model_cascade_panel()

        # Logout button
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            SessionManager.logout()
            st.rerun()

        # Add footer to sidebar
        show_footer(in_sidebar=True)


def render_daily_limit_card():
    if 'analysis_count' not in st.session_state:
        st.session_state.analysis_count = 0

    remaining = ANALYSIS_DAILY_LIMIT - st.session_state.analysis_count
    used_pct = max(0, min(100, int((st.session_state.analysis_count / ANALYSIS_DAILY_LIMIT) * 100)))
    bar_color = PRIMARY_COLOR if remaining > 3 else ERROR_COLOR

    st.markdown(
        f"""
        <div class="hia-soft-card" style="margin: 0.75rem 0;">
            <p style="margin: 0; color: #5B7186; font-size: 0.8em;">Daily Analysis Limit</p>
            <p style="margin: 0.15rem 0 0.4rem 0; color: {bar_color}; font-weight: 700; font-size: 1em;">
                {remaining}/{ANALYSIS_DAILY_LIMIT} remaining
            </p>
            <div style="background: rgba(25,118,210,0.12); border-radius: 999px; height: 6px; overflow: hidden;">
                <div style="width: {used_pct}%; background: {bar_color}; height: 100%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_model_cascade_panel():
    """Extended Multi-model cascade feature: visible cascade status + a
    manual speed/quality preference that controls where the cascade starts."""
    with st.expander("⚙️ AI Engine Settings", expanded=False):
        st.caption("HIA automatically switches to a backup AI if the first one is busy or unavailable, so your analysis still goes through.")
        tiers_used = st.session_state.get("tiers_used", {})
        for tier in [ModelTier.PRIMARY, ModelTier.SECONDARY, ModelTier.TERTIARY, ModelTier.FALLBACK]:
            config = ModelManager.MODEL_CONFIG[tier]
            count = tiers_used.get(tier.value, 0)
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center;
                            padding: 0.35rem 0; border-bottom: 1px solid rgba(25,118,210,0.08); font-size: 0.85em;">
                    <span><b>{tier.value.capitalize()}</b> · {config['model']}</span>
                    <span class="hia-badge hia-badge-{'primary' if count else 'muted'}">{count}x</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
        st.caption("How should a new analysis start?")
        choice = st.selectbox(
            "Model preference",
            list(TIER_PREFERENCES.keys()),
            label_visibility="collapsed",
            key="model_tier_preference_choice",
        )
        selected_tier = TIER_PREFERENCES[choice]
        st.session_state.model_tier_preference = selected_tier.value if selected_tier else None


def show_session_list():
    if st.session_state.user and 'id' in st.session_state.user:
        success, sessions = SessionManager.get_user_sessions()
        if success:
            if sessions:
                st.subheader("Previous Sessions")
                render_session_list(sessions)
            else:
                st.info("No previous sessions")


def render_session_list(sessions):
    # Store deletion state
    if 'delete_confirmation' not in st.session_state:
        st.session_state.delete_confirmation = None

    for session in sessions:
        render_session_item(session)


def render_session_item(session):
    if not session or not isinstance(session, dict) or 'id' not in session:
        return

    session_id = session['id']
    current_session = st.session_state.get('current_session', {})
    current_session_id = current_session.get('id') if isinstance(current_session, dict) else None
    is_active = current_session_id == session_id

    # Create container for each session
    with st.container():
        if is_active:
            st.markdown(
                """<div style="border-left: 3px solid #1976D2; padding-left: 0.5rem; margin-bottom: -0.5rem;"></div>""",
                unsafe_allow_html=True,
            )
        # Session title and delete button side by side
        title_col, delete_col = st.columns([4, 1])

        with title_col:
            if st.button(
                f"📝 {session['title']}",
                key=f"session_{session_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_session = session
                st.rerun()

        with delete_col:
            if st.button("🗑️", key=f"delete_{session_id}", help="Delete this session"):
                if st.session_state.delete_confirmation == session_id:
                    st.session_state.delete_confirmation = None
                else:
                    st.session_state.delete_confirmation = session_id
                st.rerun()

        # Show confirmation below if this session is being deleted
        if st.session_state.delete_confirmation == session_id:
            st.warning("Delete above session?")
            left_btn, right_btn = st.columns(2)
            with left_btn:
                if st.button("Yes", key=f"confirm_delete_{session_id}", type="primary", use_container_width=True):
                    handle_delete_confirmation(session_id, current_session_id)
            with right_btn:
                if st.button("No", key=f"cancel_delete_{session_id}", use_container_width=True):
                    st.session_state.delete_confirmation = None
                    st.rerun()


def handle_delete_confirmation(session_id, current_session_id):
    if not session_id:
        st.error("Invalid session")
        return

    success, error = SessionManager.delete_session(session_id)
    if success:
        st.session_state.delete_confirmation = None
        # Clear current session if it was deleted
        if current_session_id and current_session_id == session_id:
            st.session_state.current_session = None
        st.rerun()
    else:
        st.error(f"Failed to delete: {error}")
