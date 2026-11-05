"""Mock Interview Platform - Streamlit Interface."""
import json
import requests
import streamlit as st

BACKEND_API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="AI Mock Interview Platform",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimal Custom CSS for dark monochrome aesthetic
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    h1, h2, h3 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-weight: 600; letter-spacing: -0.02em; }
    .status-badge { display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; border: 1px solid #27272a; background-color: #18181b; color: #a1a1aa; }
    .card-box { background-color: #18181b; border: 1px solid #27272a; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; }
    .metric-value { font-size: 1.75rem; font-weight: 700; color: #f4f4f5; }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 0.25rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def check_backend_health():
    """Verify connectivity to FastAPI backend."""
    try:
        res = requests.get(f"{BACKEND_API_BASE}/api/health", timeout=2)
        if res.status_code == 200:
            return True, res.json()
    except Exception:
        pass
    return False, None


# Session State Initialization
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "interview_plan" not in st.session_state:
    st.session_state.interview_plan = None

# Header Section
is_healthy, health_info = check_backend_health()

col_title, col_status = st.columns([4, 1])
with col_title:
    st.title("AI Mock Interview Platform")
    st.caption("Autonomous multi-agent technical interview simulation and performance evaluation")

with col_status:
    if is_healthy:
        st.markdown(
            f'<div style="text-align: right; padding-top: 1rem;"><span class="status-badge" style="border-color: #059669; color: #34d399;">System Online</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="text-align: right; padding-top: 1rem;"><span class="status-badge" style="border-color: #dc2626; color: #f87171;">System Offline</span></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# Main Intake Form (Split Columns)
col_resume, col_jd = st.columns(2, gap="large")

with col_resume:
    st.subheader("1. Resume Submission")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF format)",
        type=["pdf"],
        help="Upload candidate PDF resume. Max file size: 10MB.",
    )

    if uploaded_file is not None:
        if (
            st.session_state.resume_data is None
            or st.session_state.resume_data.get("filename") != uploaded_file.name
        ):
            with st.spinner("Extracting and sanitizing resume text..."):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }
                    response = requests.post(
                        f"{BACKEND_API_BASE}/api/v1/resume/parse", files=files, timeout=10
                    )
                    if response.status_code == 200:
                        st.session_state.resume_data = response.json()
                        st.success(f"Resume parsed: {uploaded_file.name}")
                    else:
                        st.error(
                            f"Parsing failed: {response.json().get('detail', 'Unknown error')}"
                        )
                except Exception as exc:
                    st.error(f"Failed to reach backend parser: {str(exc)}")

    if st.session_state.resume_data:
        res = st.session_state.resume_data
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown('<div class="metric-label">Pages</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{res["page_count"]}</div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-label">Word Count</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{res["word_count"]}</div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-label">Characters</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{res["character_count"]}</div>', unsafe_allow_html=True)

        with st.expander("View Sanitized Resume Extract", expanded=False):
            st.text_area("Extracted Plain Text", res["extracted_text"], height=200, disabled=True)

with col_jd:
    st.subheader("2. Target Position")
    target_role = st.text_input(
        "Target Role Title",
        value="Senior Backend Engineer",
        placeholder="e.g. Senior Backend Engineer, Fullstack Lead",
    )

    job_description = st.text_area(
        "Job Description & Requirements",
        value=(
            "Looking for a Senior Backend Developer proficient in Python, FastAPI, and PostgreSQL. "
            "Experience with Kubernetes, Redis caching, microservices architecture, and distributed messaging (Kafka/RabbitMQ) is required. "
            "Candidate must have strong problem-solving skills and experience designing resilient, high-throughput systems."
        ),
        height=180,
        placeholder="Paste full job description requirements here...",
    )

st.markdown("---")

# Action Trigger
col_act1, col_act2 = st.columns([1, 4])
with col_act1:
    generate_plan_btn = st.button("Generate Interview Plan", use_container_width=True, type="primary")

if generate_plan_btn:
    if not st.session_state.resume_data:
        st.warning("Please upload a valid PDF resume first.")
    elif not job_description or len(job_description.strip()) < 10:
        st.warning("Please enter a valid job description (minimum 10 characters).")
    else:
        with st.spinner("Analyzing competency alignment and generating syllabus..."):
            try:
                payload = {
                    "resume_text": st.session_state.resume_data["extracted_text"],
                    "job_description": job_description.strip(),
                    "target_role": target_role.strip(),
                    "max_turns": 5,
                }
                plan_res = requests.post(
                    f"{BACKEND_API_BASE}/api/v1/interview/plan", json=payload, timeout=20
                )
                if plan_res.status_code == 200:
                    st.session_state.interview_plan = plan_res.json()
                else:
                    st.error(f"Plan generation failed: {plan_res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Network error: {str(e)}")

# Display Generated Plan
if st.session_state.interview_plan:
    plan = st.session_state.interview_plan
    st.subheader("Interview Plan & Competency Analysis")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("#### Competency Gap Assessment")
        gap = plan.get("gap_analysis", {})

        st.markdown("**Verified Competency Matches:**")
        matched = gap.get("matched_skills", [])
        if matched:
            st.markdown(" ".join([f"`{m}`" for m in matched]))
        else:
            st.caption("No direct keyword matches detected.")

        st.markdown("**Identified Gaps & Weakness Vectors:**")
        missing = gap.get("missing_or_weak_skills", [])
        if missing:
            st.markdown(" ".join([f"`{m}`" for m in missing]))
        else:
            st.caption("No critical gaps detected.")

        st.markdown("**High-Priority Assessment Focus:**")
        for risk in gap.get("primary_risks", []):
            st.markdown(f"- {risk}")

    with c2:
        st.markdown("#### 5-Stage Interview Syllabus")
        syllabus = plan.get("question_syllabus", [])
        for index, stage_desc in enumerate(syllabus, start=1):
            st.markdown(f"**{stage_desc}**")

    st.markdown("---")
    st.button("Proceed to Live Interview Console", use_container_width=False)
