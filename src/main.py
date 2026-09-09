import streamlit as st
from auth.session_manager import SessionManager
from components.auth_pages import show_login_page
from components.sidebar import show_sidebar
from components.analysis_form import show_analysis_form
from components.footer import show_footer
from config.app_config import APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_ICON
from config.theme import inject_global_css, render_chat_bubble
from services.ai_service import get_chat_response

# Must be the first Streamlit command
st.set_page_config(
    page_title="HIA - Health Insights Agent", page_icon="🩺", layout="wide"
)

# Apply one shared stylesheet to every screen (login, welcome, sidebar, chat, ...)
inject_global_css()



def show_welcome_screen():
    st.markdown(
        f"""
        <div style='text-align: center; padding: 3rem 1rem 1rem 1rem;'>
            <div style="font-size: 2.8rem;">{APP_ICON}</div>
            <h1 style="margin: 0.4rem 0 0 0;">{APP_NAME}</h1>
            <h3 style="font-weight: 500; color: #5B7186;">Understand your blood test results, explained in plain language</h3>
            <p style='font-size: 1.1em; color: #5B7186;'>Upload your report and get clear, easy-to-follow guidance — no medical background needed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        if st.button(
            "➕ Get Started — Analyze My Report", use_container_width=True, type="primary"
        ):
            success, session = SessionManager.create_chat_session()
            if success:
                st.session_state.current_session = session
                st.rerun()
            else:
                st.error("Failed to create session")

    render_how_it_works()
    render_feature_highlights()


def render_how_it_works():
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    steps = [
        ("1️⃣", "Upload your report", "Add a PDF of your blood test, or try our sample report first."),
        ("2️⃣", "Get a plain-language explanation", "We highlight what's normal, what to keep an eye on, and why."),
        ("3️⃣", "Ask follow-up questions", "Not sure what something means? Just ask — like texting a knowledgeable friend."),
    ]
    cols = st.columns(3)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem;">
                    <div style="font-size: 1.6rem;">{num}</div>
                    <h4 style="margin: 0.3rem 0;">{title}</h4>
                    <p style="color: #5B7186; font-size: 0.88em;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

def render_feature_highlights():
    """Showcase what the app can do, in everyday language (no technical jargon)."""
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    cards = [
        (
            "🎯",
            "Made for you",
            "See a full overview, or a closer look at your heart, sugar, or diet.",
        ),
        (
            "⚡",
            "Never stuck waiting",
            "If one AI is busy, we switch to another right away.",
        ),
        (
            "💬",
            "Ask us anything",
            "Confused by a term? Just ask, and we'll explain it simply.",
        ),
    ]
    cols = st.columns(3)
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="hia-card" style="height: 100%; box-sizing: border-box; display: flex; flex-direction: column;">
                    <div style="font-size: 1.6rem;">{icon}</div>
                    <h4 style="margin: 0.4rem 0;">{title}</h4>
                    <p style="color: #5B7186; font-size: 0.9em; margin: 0;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown(
        """
        <p style="text-align:center; color:#5B7186; font-size:0.8em; margin-top:1rem;">
            ⚕️ HIA gives general health information, not medical advice. Always check important results with a doctor.
        </p>
        """,
        unsafe_allow_html=True,
    )

def show_chat_history():
    success, messages = st.session_state.auth_service.get_session_messages(
        st.session_state.current_session["id"]
    )

    if success:
        for msg in messages:
            # Skip system messages (they contain report text metadata)
            if msg.get("role") == "system":
                continue
            render_chat_bubble(msg["role"], msg["content"])
        return messages
    return []


def handle_chat_input(messages):
    if prompt := st.chat_input("Ask a follow-up question about the report..."):
        # Display user message immediately
        render_chat_bubble("user", prompt)

        # Save user message
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"], prompt, role="user"
        )

        # Get context (report text)
        # We try to get it from session state first (for immediate use)
        context_text = st.session_state.get("current_report_text", "")

        # If not in session state, try to retrieve from stored system message
        if not context_text and messages:
            for msg in messages:
                if msg.get("role") == "system" and "__REPORT_TEXT__" in msg.get(
                    "content", ""
                ):
                    # Extract report text from system message
                    content = msg.get("content", "")
                    start_idx = content.find("__REPORT_TEXT__\n") + len(
                        "__REPORT_TEXT__\n"
                    )
                    end_idx = content.find("\n__END_REPORT_TEXT__")
                    if start_idx > len("__REPORT_TEXT__\n") - 1 and end_idx > start_idx:
                        context_text = content[start_idx:end_idx]
                        # Also restore to session state for future use
                        st.session_state.current_report_text = context_text
                        break

        with st.spinner("Thinking..."):
            response = get_chat_response(prompt, context_text, messages)

            render_chat_bubble("assistant", response)

            # Save AI response
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], response, role="assistant"
            )
            # Rerun to update history display properly
            st.rerun()


def show_user_greeting():
    if st.session_state.user:
        # Get name from user data, fallback to email if name is empty
        display_name = st.session_state.user.get("name") or st.session_state.user.get(
            "email", ""
        )
        st.markdown(
            f"""
            <div style='text-align: right; padding: 0.75rem 0.25rem; color: #1976D2; font-size: 1.05em; font-weight: 600;'>
                👋 Hi, {display_name}
            </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        show_login_page()
        show_footer()
        return

    # Show user greeting at the top
    show_user_greeting()

    # Show sidebar
    show_sidebar()

    # Main chat area
    if st.session_state.get("current_session"):
        st.title(f"📊 {st.session_state.current_session['title']}")
        messages = show_chat_history()

        # If we have messages (meaning analysis is done), show chat input
        # Otherwise show analysis form
        if messages:
            # We can still show the analysis form collapsed or just hide it
            # For better UX, if analysis is done, we might not want to show the form again
            # unless the user wants to re-analyze/start over.
            # But the current form design allows re-analysis.
            # Let's put the analysis form in an expander if analysis is done.
            with st.expander("New Analysis / Update Report", expanded=False):
                show_analysis_form()

            handle_chat_input(messages)
        else:
            show_analysis_form()
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()
