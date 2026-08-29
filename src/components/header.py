import streamlit as st


def show_header():
    if st.session_state.user:
        display_name = st.session_state.user.get('name') or st.session_state.user.get('email', '')
        st.markdown(
            f"""
            <div style='text-align: right; padding: 0.75rem 0.25rem; color: #1976D2; font-size: 1.05em; font-weight: 600;'>
                👋 Hi, {display_name}
            </div>
        """,
            unsafe_allow_html=True,
        )
