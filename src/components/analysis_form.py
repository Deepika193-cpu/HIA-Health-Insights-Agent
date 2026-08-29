import streamlit as st
from config.prompts import SPECIALIST_PROMPTS, SPECIALIST_INFO
from utils.pdf_extractor import extract_text_from_pdf
from config.sample_data import SAMPLE_REPORT
from config.app_config import MAX_UPLOAD_SIZE_MB


def show_analysis_form():
    # Initialize report source in session state for new sessions
    if (
        "current_session" in st.session_state
        and "report_source" not in st.session_state
    ):
        st.session_state.report_source = "Upload PDF"

    report_source = st.radio(
        "Choose report source",
        ["Upload PDF", "Use Sample PDF"],
        index=0 if st.session_state.get("report_source") == "Upload PDF" else 1,
        horizontal=True,
        key="report_source",
    )

    pdf_contents = get_report_contents(report_source)

    if pdf_contents:  # Only show form if we have report content
        render_patient_form(pdf_contents)


def get_report_contents(report_source):
    if report_source == "Upload PDF":
        uploaded_file = st.file_uploader(
            f"Upload blood report PDF (Max {MAX_UPLOAD_SIZE_MB}MB)",
            type=["pdf"],
            help=f"Maximum file size: {MAX_UPLOAD_SIZE_MB}MB. Only PDF files containing medical reports are supported",
        )
        if uploaded_file:
            # Check file size before processing
            file_size_mb = uploaded_file.size / (1024 * 1024)  # Convert to MB
            if file_size_mb > MAX_UPLOAD_SIZE_MB:
                st.error(
                    f"File size ({file_size_mb:.1f}MB) exceeds the {MAX_UPLOAD_SIZE_MB}MB limit."
                )
                return None

            if uploaded_file.type != "application/pdf":
                st.error("Please upload a valid PDF file.")
                return None

            pdf_contents = extract_text_from_pdf(uploaded_file)
            if isinstance(pdf_contents, str) and (
                pdf_contents.startswith(
                    ("File size exceeds", "Invalid file type", "Error validating")
                )
                or pdf_contents.startswith("The uploaded file")
                or "error" in pdf_contents.lower()
            ):
                st.error(pdf_contents)
                return None
            with st.expander("View Extracted Report"):
                st.text(pdf_contents)
            return pdf_contents
    else:
        with st.expander("View Sample Report"):
            st.text(SAMPLE_REPORT)
        return SAMPLE_REPORT
    return None


def render_specialist_picker():
    """Let the user choose which specialist lens the Analysis Agent should use."""
    st.markdown("**Analysis focus**")
    keys = list(SPECIALIST_PROMPTS.keys())
    labels = [f"{SPECIALIST_INFO[k]['icon']} {SPECIALIST_INFO[k]['label']}" for k in keys]

    default_key = st.session_state.get("specialist_mode", "comprehensive_analyst")
    default_index = keys.index(default_key) if default_key in keys else 0

    selected_label = st.radio(
        "Analysis focus",
        labels,
        index=default_index,
        horizontal=True,
        label_visibility="collapsed",
        key="specialist_mode_radio",
    )
    selected_key = keys[labels.index(selected_label)]
    st.session_state.specialist_mode = selected_key

    info = SPECIALIST_INFO[selected_key]
    st.markdown(
        f"""
        <div class="hia-soft-card" style="margin-bottom: 0.75rem;">
            {info['description']}
        </div>
        """,
        unsafe_allow_html=True,
    )
    return selected_key


def render_patient_form(pdf_contents):
    specialist_key = render_specialist_picker()

    with st.form("analysis_form"):
        patient_name = st.text_input("Patient Name")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        if st.form_submit_button("Analyze Report", type="primary"):
            handle_form_submission(patient_name, age, gender, pdf_contents, specialist_key)


def handle_form_submission(patient_name, age, gender, pdf_contents, specialist_key="comprehensive_analyst"):
    if not all([patient_name, age, gender]):
        st.error("Please fill in all fields")
        return

    # Check rate limit first, outside of spinner
    from services.ai_service import generate_analysis

    can_analyze, error_msg = generate_analysis(None, None, check_only=True)
    if not can_analyze:
        st.error(error_msg)
        st.stop()
        return

    specialist_info = SPECIALIST_INFO.get(specialist_key, SPECIALIST_INFO["comprehensive_analyst"])

    with st.spinner(f"Analyzing report ({specialist_info['label']})..."):
        # Save report content for follow-up chat (session state for immediate use)
        st.session_state.current_report_text = pdf_contents

        # Save user message and proceed with analysis
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"],
            f"Analyzing report for patient: {patient_name} ({specialist_info['label']} analysis)",
        )

        # Generate analysis using the selected specialist prompt and the
        # user's preferred model-cascade starting tier (set from the sidebar).
        result = generate_analysis(
            {
                "patient_name": patient_name,
                "age": age,
                "gender": gender,
                "report": pdf_contents,
            },
            SPECIALIST_PROMPTS[specialist_key],
            preferred_tier=st.session_state.get("model_tier_preference"),
        )

        if result["success"]:
            # Store report text as a system message for persistence
            # This allows us to retrieve it later even after page refresh
            report_metadata = f"__REPORT_TEXT__\n{pdf_contents}\n__END_REPORT_TEXT__"
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], report_metadata, role="system"
            )

            # Add model + specialist info if available
            content = result["content"]
            footer_bits = [f"{specialist_info['icon']} {specialist_info['label']} analysis"]
            if "model_used" in result:
                footer_bits.append(f"generated using {result['model_used']}")
            content += "\n\n*" + " · ".join(footer_bits) + "*"

            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], content, role="assistant"
            )
            st.rerun()
        else:
            st.error(result["error"])
            st.stop()
