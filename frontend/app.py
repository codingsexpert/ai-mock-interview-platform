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

# Minimal Custom CSS for crisp modern light aesthetic
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1100px; }
    h1, h2, h3 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-weight: 600; letter-spacing: -0.02em; color: #0f172a; }
    .status-badge { display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; border: 1px solid #e2e8f0; background-color: #f8fafc; color: #475569; }
    .card-box { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04); }
    .question-box { background-color: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #0f172a; border-radius: 6px; padding: 1.25rem; margin: 1rem 0; font-size: 1.1rem; line-height: 1.6; color: #0f172a; }
    .metric-value { font-size: 1.75rem; font-weight: 700; color: #0f172a; }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 0.25rem; }
    .chat-bubble-ai { background-color: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; color: #0f172a; }
    .chat-bubble-user { background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; color: #0f172a; }
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
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "setup"  # "setup" | "interview" | "report" | "history"
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "interview_plan" not in st.session_state:
    st.session_state.interview_plan = None
if "active_session" not in st.session_state:
    st.session_state.active_session = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "is_interview_completed" not in st.session_state:
    st.session_state.is_interview_completed = False
if "current_audio_bytes" not in st.session_state:
    st.session_state.current_audio_bytes = None
if "last_voiced_question" not in st.session_state:
    st.session_state.last_voiced_question = None
if "view_history_session_id" not in st.session_state:
    st.session_state.view_history_session_id = None

# Header Bar
is_healthy, _ = check_backend_health()

col_title, col_nav, col_status = st.columns([3, 2, 1])
with col_title:
    st.title("AI Mock Interview Platform")
    st.caption("Autonomous multi-agent technical interview simulation and performance evaluation")

with col_nav:
    st.markdown('<div style="padding-top: 1rem;">', unsafe_allow_html=True)
    c_n1, c_n2 = st.columns(2)
    with c_n1:
        if st.button("Intake & Setup", use_container_width=True, type="primary" if st.session_state.app_mode == "setup" else "secondary"):
            st.session_state.app_mode = "setup"
            st.rerun()
    with c_n2:
        if st.button("Past History", use_container_width=True, type="primary" if st.session_state.app_mode == "history" else "secondary"):
            st.session_state.app_mode = "history"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_status:
    if is_healthy:
        st.markdown(
            '<div style="text-align: right; padding-top: 1.2rem;"><span class="status-badge" style="border-color: #059669; color: #34d399;">System Online</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align: right; padding-top: 1.2rem;"><span class="status-badge" style="border-color: #dc2626; color: #f87171;">System Offline</span></div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ==========================================
# MODE 1: SETUP & INTAKE
# ==========================================
if st.session_state.app_mode == "setup":
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

            with st.expander("View Extracted Text", expanded=False):
                st.text_area("Resume Plain Text", res["extracted_text"], height=160, disabled=True)

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

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
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
            for stage_desc in syllabus:
                st.markdown(f"**{stage_desc}**")

        st.markdown("---")
        start_interview_btn = st.button("Launch Live Interview Session", type="primary", use_container_width=False)
        if start_interview_btn:
            with st.spinner("Initializing conversational session and opening calibration question..."):
                try:
                    init_payload = {
                        "resume_text": st.session_state.resume_data["extracted_text"],
                        "job_description": job_description.strip(),
                        "target_role": target_role.strip(),
                        "max_turns": 5,
                    }
                    init_res = requests.post(
                        f"{BACKEND_API_BASE}/api/v1/interview/start", json=init_payload, timeout=15
                    )
                    if init_res.status_code == 200:
                        data = init_res.json()
                        st.session_state.active_session = data
                        st.session_state.conversation_history = [
                            {"role": "assistant", "content": data["first_question"]}
                        ]
                        st.session_state.is_interview_completed = False
                        st.session_state.app_mode = "interview"
                        st.rerun()
                    else:
                        st.error(f"Failed to start session: {init_res.text}")
                except Exception as ex:
                    st.error(f"Failed to connect to session engine: {str(ex)}")

# ==========================================
# MODE 2: LIVE INTERVIEW CONSOLE
# ==========================================
elif st.session_state.app_mode == "interview":
    session = st.session_state.active_session
    turn_num = len([m for m in st.session_state.conversation_history if m["role"] == "user"]) + 1
    max_turns = session["max_turns"]

    # Top Status Bar
    col_meta1, col_meta2, col_meta3 = st.columns([2, 2, 1])
    with col_meta1:
        st.markdown(f"**Role:** {session['target_role']}")
    with col_meta2:
        st.markdown(f"**Progress:** Turn {min(turn_num, max_turns)} of {max_turns} (`{session['current_phase']}`)")
    with col_meta3:
        if st.button("End Session Early", type="secondary"):
            st.session_state.app_mode = "setup"
            st.rerun()

    progress_val = min(1.0, (turn_num - 1) / max_turns)
    st.progress(progress_val)

    st.markdown("---")

    # Display Current Interviewer Question
    current_question = st.session_state.conversation_history[-1]["content"]
    st.markdown('<div class="metric-label">Active Interviewer Question</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="question-box">{current_question}</div>', unsafe_allow_html=True)

    # Voice Playback for Question
    if st.session_state.last_voiced_question != current_question:
        try:
            voice_res = requests.post(
                f"{BACKEND_API_BASE}/api/v1/voice/synthesize",
                json={"text": current_question},
                timeout=10,
            )
            if voice_res.status_code == 200:
                st.session_state.current_audio_bytes = voice_res.content
                st.session_state.last_voiced_question = current_question
        except Exception:
            pass

    if st.session_state.current_audio_bytes:
        col_audio, _ = st.columns([2, 3])
        with col_audio:
            st.audio(st.session_state.current_audio_bytes, format="audio/mp3", autoplay=True)

    # Candidate Answer Submission Area
    if not st.session_state.is_interview_completed:
        st.markdown("#### Candidate Response")

        # Audio Input Option (if supported by Streamlit runtime)
        audio_prompt = st.audio_input("Record Verbal Answer (Optional)")

        user_answer_text = st.text_area(
            "Your Answer (Type or dictated verbal response)",
            height=120,
            placeholder="Type your structured answer here...",
            key="user_text_response",
        )

        col_sub1, _ = st.columns([1, 4])
        with col_sub1:
            submit_answer_btn = st.button("Submit Answer", type="primary", use_container_width=True)

        if submit_answer_btn:
            if not user_answer_text or len(user_answer_text.strip()) < 5:
                st.warning("Please provide a substantive answer (minimum 5 characters).")
            else:
                with st.spinner("Interviewer is evaluating your response and preparing follow-up..."):
                    try:
                        turn_payload = {
                            "session_id": session["session_id"],
                            "user_answer": user_answer_text.strip(),
                        }
                        turn_res = requests.post(
                            f"{BACKEND_API_BASE}/api/v1/interview/turn", json=turn_payload, timeout=20
                        )
                        if turn_res.status_code == 200:
                            turn_data = turn_res.json()
                            # Append user answer and assistant question
                            st.session_state.conversation_history.append(
                                {"role": "user", "content": user_answer_text.strip()}
                            )
                            st.session_state.conversation_history.append(
                                {"role": "assistant", "content": turn_data["interviewer_question"]}
                            )
                            session["current_phase"] = turn_data["current_phase"]
                            st.session_state.is_interview_completed = turn_data["is_completed"]
                            st.rerun()
                        else:
                            st.error(f"Failed to process turn: {turn_res.text}")
                    except Exception as err:
                        st.error(f"Turn processing error: {str(err)}")
    else:
        st.success("All interview rounds completed! Your comprehensive assessment scorecard is ready.")
        if st.button("Generate Performance Audit Report", type="primary"):
            st.session_state.app_mode = "report"
            st.rerun()

    # Conversation History Feed
    with st.expander("Interview Session Transcript Log", expanded=False):
        for msg in st.session_state.conversation_history:
            if msg["role"] == "assistant":
                st.markdown(
                    f'<div class="chat-bubble-ai"><strong>Interviewer:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bubble-user"><strong>Candidate:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

# ==========================================
# MODE 3: PERFORMANCE AUDIT REPORT
# ==========================================
elif st.session_state.app_mode == "report":
    session = st.session_state.active_session
    st.subheader("Executive Performance Audit Report")

    # Fetch full session state from backend
    with st.spinner("Compiling turn evaluations and metrics..."):
        try:
            full_res = requests.get(f"{BACKEND_API_BASE}/api/v1/interview/session/{session['session_id']}")
            state_data = full_res.json()
        except Exception:
            state_data = {"evaluations": []}

    evals = state_data.get("evaluations", [])

    if evals:
        # Calculate aggregates
        avg_tech = sum(e.get("technical_accuracy_score", 0) for e in evals) / len(evals)
        avg_comm = sum(e.get("communication_clarity_score", 0) for e in evals) / len(evals)
        composite_score = round(((avg_tech * 0.6) + (avg_comm * 0.4)) * 10, 1)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown('<div class="metric-label">Composite Index</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{composite_score} / 100</div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-label">Technical Mastery</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{round(avg_tech, 1)} / 10</div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-label">Communication & Articulation</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{round(avg_comm, 1)} / 10</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Turn-by-Turn Audit & Benchmarking")

        for idx, ev in enumerate(evals, start=1):
            with st.container():
                st.markdown(f"#### Turn {idx}: {ev.get('question', '')}")
                c_a, c_b = st.columns(2, gap="medium")
                with c_a:
                    st.markdown("**Candidate Transcript:**")
                    st.caption(ev.get("candidate_answer", ""))
                    st.markdown(f"**Technical Score:** `{ev.get('technical_accuracy_score', 0)}/10` | **Clarity:** `{ev.get('communication_clarity_score', 0)}/10`")
                with c_b:
                    st.markdown("**Identified Strengths:**")
                    for s in ev.get("key_strengths", []):
                        st.markdown(f"- {s}")
                    st.markdown("**Critical Technical Deficits:**")
                    for d in ev.get("critical_deficits", []):
                        st.markdown(f"- {d}")

                st.markdown("**Benchmarked Ideal Response:**")
                st.info(ev.get("suggested_ideal_response", ""))
                st.markdown("---")
    else:
        st.info("No completed evaluations recorded for this session.")

    col_dl, col_new = st.columns([1, 1], gap="medium")
    with col_dl:
        try:
            pdf_res = requests.get(
                f"{BACKEND_API_BASE}/api/v1/interview/session/{session['session_id']}/report.pdf",
                timeout=10,
            )
            if pdf_res.status_code == 200:
                st.download_button(
                    label="Download Official Assessment PDF",
                    data=pdf_res.content,
                    file_name=f"Assessment_Report_{session['session_id'][:8]}.pdf",
                    mime="application/pdf",
                    type="secondary",
                    use_container_width=True,
                )
        except Exception:
            pass

    with col_new:
        if st.button("Start New Interview Session", type="primary", use_container_width=True):
            st.session_state.app_mode = "setup"
            st.session_state.active_session = None
            st.session_state.conversation_history = []
            st.session_state.is_interview_completed = False
            st.session_state.current_audio_bytes = None
            st.session_state.last_voiced_question = None
            st.rerun()

# ==========================================
# MODE 4: INTERVIEW HISTORY & PAST SCORECARDS
# ==========================================
elif st.session_state.app_mode == "history":
    st.subheader("Historical Assessment Ledger")
    with st.spinner("Loading interview records from database..."):
        try:
            hist_res = requests.get(f"{BACKEND_API_BASE}/api/v1/interview/history", timeout=5)
            records = hist_res.json() if hist_res.status_code == 200 else []
        except Exception as e:
            records = []
            st.error(f"Failed to query database: {str(e)}")

    if records:
        st.markdown(f"**Total Recorded Sessions:** `{len(records)}`")
        st.markdown("---")
        for rec in records:
            with st.container():
                h_col1, h_col2, h_col3, h_col4 = st.columns([3, 2, 2, 2])
                with h_col1:
                    st.markdown(f"**{rec['target_role']}**")
                    created_date = rec.get("created_at")[:10] if rec.get("created_at") else "N/A"
                    st.caption(f"Session: `{rec['session_id'][:8]}...` | Date: {created_date}")
                with h_col2:
                    score = rec.get("composite_score")
                    st.markdown(f"Composite: **{score if score is not None else 'In-Progress'}**")
                    st.caption(f"Progress: {rec['completed_turns']} of {rec['total_turns']} turns")
                with h_col3:
                    t_score = rec.get("technical_score")
                    c_score = rec.get("communication_score")
                    if t_score is not None:
                        st.caption(f"Technical: {t_score}/10\nClarity: {c_score}/10")
                    else:
                        st.caption("Awaiting completion")
                with h_col4:
                    if st.button("Review Report", key=f"btn_hist_{rec['session_id']}", use_container_width=True):
                        st.session_state.active_session = {
                            "session_id": rec["session_id"],
                            "target_role": rec["target_role"],
                            "max_turns": rec["total_turns"],
                            "current_phase": "completed",
                        }
                        st.session_state.app_mode = "report"
                        st.rerun()
                st.markdown("---")
    else:
        st.info("No recorded interview sessions in database yet. Launch your first session to build your assessment history.")
