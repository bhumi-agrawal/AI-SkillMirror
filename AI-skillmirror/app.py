import streamlit as st
import json
from pathlib import Path
import plotly.express as px
from pypdf import PdfReader

# ---------------- PAGE SETUP ----------------

st.set_page_config(
    page_title="AI SkillMirror",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@500;600;700;800&display=swap');

:root {
    --bg-deep: #1B0B18;
    --bg-card: #2B1226;
    --text-main: #FFF4FA;
    --text-muted: #F0C9DC;
    --accent-cyan: #FF8FC7;
    --accent-purple: #FF5FA2;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(255, 95, 162, 0.22), transparent 28%),
        radial-gradient(circle at 88% 18%, rgba(255, 143, 199, 0.16), transparent 26%),
        linear-gradient(135deg, #180A17 0%, #35132D 52%, #4A1738 100%);
    color: var(--text-main);
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3.5rem;
    max-width: 1320px;
}

/* Clear, modern headings */
h1, h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    letter-spacing: -0.4px;
}
h1 { text-shadow: 0 0 24px rgba(255, 143, 199, 0.24); }
h2 { border-bottom: 1px solid rgba(255, 143, 199, 0.28); padding-bottom: 0.35rem; }

/* Readable body text */
.stApp p, .stApp li, .stApp label,
.stApp [data-testid="stMarkdownContainer"],
.stCaption, small {
    color: var(--text-muted);
}
strong, b { color: #FFFFFF !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #35132D 0%, #1B0B18 100%);
    border-right: 1px solid rgba(255, 143, 199, 0.30);
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #FFFFFF !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(74, 24, 57, 0.97), rgba(48, 17, 43, 0.97));
    border: 1px solid rgba(255, 143, 199, 0.34);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(255, 143, 199, 0.75);
}
[data-testid="stMetricLabel"] { color: #FFD6E8 !important; }
[data-testid="stMetricValue"] { color: var(--accent-cyan) !important; font-weight: 800 !important; }
[data-testid="stMetricDelta"] { color: #FFA8D1 !important; }

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(100deg, #FF4F9A 0%, #E84393 55%, #FF9BCB 100%);
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 0.65rem 1.25rem;
    font-weight: 700;
    transition: all 0.2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--accent-cyan);
    box-shadow: 0 0 22px rgba(255, 95, 162, 0.32);
    transform: translateY(-1px);
}

/* Upload panel */
[data-testid="stFileUploader"] {
    background: rgba(58, 20, 48, 0.82);
    border: 1px dashed #FF7EB6;
    border-radius: 16px;
    padding: 16px;
}
[data-testid="stFileUploader"] section { color: #FFF0F7 !important; }

/* Inputs and dropdowns */
.stSelectbox > div > div,
.stNumberInput input,
.stTextInput input,
.stMultiSelect > div > div,
.stTextArea textarea {
    background-color: #35172E !important;
    color: #FFFFFF !important;
    border: 1px solid #8D426C !important;
    border-radius: 10px !important;
}
[data-baseweb="select"] * { color: #FFFFFF !important; }

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #FF4F9A, #FFB0D6);
    border-radius: 20px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] { color: #F7D6E7; font-weight: 600; }
.stTabs [aria-selected="true"] { color: var(--accent-cyan) !important; }

/* Expanders and data tables */
[data-testid="stExpander"] {
    background: rgba(53, 19, 45, 0.84);
    border: 1px solid rgba(255, 143, 199, 0.28);
    border-radius: 14px;
}
[data-testid="stDataFrame"] { border: 1px solid rgba(255, 143, 199, 0.30); border-radius: 12px; }

/* Alerts and separators */
[data-testid="stAlert"] { border-radius: 12px; border: 1px solid rgba(255, 190, 220, 0.20); }
hr { border-color: rgba(255, 143, 199, 0.34); }

/* Links */
a { color: var(--accent-cyan) !important; }
a:hover { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)
# ---------------- FUNCTIONS ----------------

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "

    return text.lower()


def find_skills(resume_text, required_skills):
    detected_skills = []

    for skill in required_skills:
        if skill.lower() in resume_text:
            detected_skills.append(skill)

    return detected_skills


def calculate_score(career_data, detected_skills):
    total_weight = sum(career_data.values())

    if total_weight == 0:
        return 0

    earned_weight = sum(
        weight
        for skill, weight in career_data.items()
        if skill in detected_skills
    )

    return round((earned_weight / total_weight) * 100)


def get_skill_gaps(career_data, detected_skills):
    return [
        skill
        for skill in career_data
        if skill not in detected_skills
    ]


# Career skill weights used by the resume matcher
careers = {
    "Data Scientist": {
        "Python": 15, "SQL": 10, "Statistics": 10, "Pandas": 10,
        "NumPy": 8, "Machine Learning": 15, "Data Visualization": 8,
        "Git": 5, "Excel": 4, "Power BI": 5, "Problem Solving": 5,
        "Deep Learning": 5
    },
    "Software Developer": {
        "Java": 15, "Python": 10, "DSA": 20, "OOP": 10, "SQL": 8,
        "DBMS": 8, "Git": 7, "Problem Solving": 12, "Excel": 2,
        "Data Visualization": 2, "Pandas": 2, "NumPy": 2
    },
    "Data Analyst": {
        "SQL": 15, "Excel": 15, "Python": 10, "Pandas": 12,
        "Statistics": 12, "Data Visualization": 12, "Power BI": 12,
        "NumPy": 4, "Git": 3, "Problem Solving": 5
    },
    "Machine Learning Engineer": {
        "Python": 12, "Machine Learning": 20, "Deep Learning": 15,
        "NumPy": 8, "Pandas": 8, "Statistics": 8, "SQL": 5,
        "Git": 5, "DSA": 7, "Problem Solving": 7, "Data Visualization": 5
    }
}

# ---------------- SIDEBAR ----------------

# ---------------- SIDEBAR ----------------

st.sidebar.title("🤖 AI SkillMirror")
st.sidebar.markdown("---")

st.sidebar.subheader("🎯 Career Selection")

career = st.sidebar.selectbox(
    "Choose your target career",
    list(careers.keys())
)

st.sidebar.markdown("---")

st.sidebar.subheader("📌 Navigation")

selected_page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Overview",
        "📄 Resume & Skills",
        "🧩 Skill Gaps",
        "🗺️ Learning Roadmap",
        "🤖 AI Career Coach",
        "🎯 Placement Dashboard"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Build your skills. Shape your future! 💗"
)


# ---------------- OVERVIEW PAGE ----------------
if selected_page == "🏠 Overview":
    st.title("🤖 AI SkillMirror")
    st.subheader(
        "Know where you stand. Discover your skill gaps. "
        "Build your career roadmap."
    )
    st.write(
        "Analyze your resume against your target career, "
        "discover missing skills, and explore your learning roadmap."
    )
    st.success("Welcome to AI SkillMirror! Select a section from the sidebar to get started. 💗")

# Keep the uploaded resume available while switching sidebar pages.
import io
if "resume_bytes" not in st.session_state:
    st.session_state["resume_bytes"] = None

# ---------------- RESUME & SKILLS PAGE ----------------
if selected_page == "📄 Resume & Skills":
    st.header("📄 Upload Your Resume")
    with st.form(key="resume_upload_form", clear_on_submit=False):
        resume_upload = st.file_uploader(
            "Upload your resume in PDF format", type=["pdf"], key="resume_upload_widget"
        )
        analyze_resume = st.form_submit_button("🚀 Analyze My Resume")
    if resume_upload is not None:
        st.session_state["resume_bytes"] = resume_upload.getvalue()

# Rebuild a file-like object from the saved upload on every rerun.
uploaded_file = io.BytesIO(st.session_state["resume_bytes"]) if st.session_state["resume_bytes"] else None
if uploaded_file is not None:
    uploaded_file.seek(0)

# Defaults prevent undefined-variable errors before a resume is uploaded.
career_data = careers[career]
detected_skills = []
gaps = list(career_data.keys())
score = 0
resume_text = ""

# ---------------- RESUME ANALYSIS ----------------
if uploaded_file is not None:
    try:
        resume_text = extract_text_from_pdf(uploaded_file)
        if not resume_text.strip():
            if selected_page == "📄 Resume & Skills":
                st.warning("PDF text not found.")
        else:
            detected_skills = find_skills(resume_text, career_data.keys())
            score = calculate_score(career_data, detected_skills)
            gaps = get_skill_gaps(career_data, detected_skills)
    except Exception as error:
        st.error(f"Resume read nahi ho paaya: {error}")
        resume_text = ""
        detected_skills = []
        gaps = list(career_data.keys())
        score = 0

if selected_page == "📄 Resume & Skills":
    if uploaded_file is None:
        st.info("Please upload resume first' then click.")
    elif not resume_text.strip():
        st.warning("text can not read.  please upload Text-based PDF")
    else:
    # ---------------- SCORE ----------------

        st.header("📊 Career Readiness")

        col1, col2, col3 = st.columns(3)

        col1.metric("Readiness Score", f"{score}%")
        col2.metric("Skills Found", len(detected_skills))
        col3.metric("Skill Gaps", len(gaps))

        st.progress(score / 100)

        if score >= 80:
            st.success("You have a strong foundation for this career!")
        elif score >= 50:
            st.warning(
                "You have a foundation to build on. "
                "Focus on the missing skills below."
            )
        else:
            st.info(
                "Start with the foundational skills in your learning roadmap."
            )

        st.caption(
            "This score measures keyword matches against our predefined "
            "career-skill weights. It is an estimate, not a job guarantee."
        )

        # ---------------- CURRENT SKILLS ----------------

        st.header("✅ Your Current Skills")

        if detected_skills:
            cols = st.columns(4)

            for i, skill in enumerate(detected_skills):
                cols[i % 4].success(skill)
        else:
            st.warning(
                "No matching skills detected. Check whether your resume "
                "mentions your skills clearly."
            )



# ---------------- SKILL GAPS PAGE ----------------
if selected_page == "🧩 Skill Gaps":
    st.header("⚠️ Your Skill Gaps")
    if uploaded_file is None or not resume_text.strip():
        st.info("For see skill gap kindly upload your resume First")
    else:
        # ---------------- SKILL GAPS ----------------

            st.header("⚠️ Your Skill Gaps")

            if gaps:
                cols = st.columns(4)

                for i, skill in enumerate(gaps):
                    cols[i % 4].error(skill)
            else:
                st.success("All listed career skills were matched!")

            # ---------------- GRAPH ----------------

            st.header("📈 Skill Analysis")

            chart_data = []

            for skill, weight in career_data.items():
                chart_data.append({
                    "Skill": skill,
                    "Status": (
                        "Matched" if skill in detected_skills
                        else "Not matched"
                    ),
                    "Weight": weight
                })

            fig = px.bar(
                chart_data,
                x="Skill",
                y="Weight",
                color="Status",
                barmode="group",
                title=f"{career} — Career Skill Requirements",
                labels={"Weight": "Importance weight"}
            )

            st.plotly_chart(fig, use_container_width=True)


# ---------------- LEARNING ROADMAP PAGE ----------------
if selected_page == "🗺️ Learning Roadmap":
    if uploaded_file is None or not resume_text.strip():
        st.info("For see Roadmap upload your Resume first .")
    else:
        st.header("🚀 Smart Learning Roadmap")

        learning_plan = {
            "Python": {
                "time": "1-2 weeks",
                "task": "Practice variables, loops, functions and lists.",
                "project": "Build a Student Marks Calculator."
            },
            "SQL": {
                "time": "1 week",
                "task": "Practice SELECT, WHERE, GROUP BY and JOIN.",
                "project": "Create a Student Database."
            },
            "Statistics": {
                "time": "2 weeks",
                "task": "Learn mean, median, probability and correlation.",
                "project": "Analyze a Student Marks Dataset."
            },
            "Pandas": {
                "time": "1 week",
                "task": "Practice filtering, cleaning and grouping data.",
                "project": "Build a Data Cleaning Project."
            },
            "NumPy": {
                "time": "1 week",
                "task": "Practice arrays, indexing and basic calculations.",
                "project": "Create a Numerical Analysis Notebook."
            },
            "Machine Learning": {
                "time": "3 weeks",
                "task": "Learn regression, classification and model evaluation.",
                "project": "Build a Student Performance Predictor."
            },
            "Data Visualization": {
                "time": "1 week",
                "task": "Learn charts, labels and interpreting graphs.",
                "project": "Create a Data Insights Dashboard."
            },
            "Git": {
                "time": "3 days",
                "task": "Practice commits, branches and repositories.",
                "project": "Upload a Python project to GitHub."
            },
            "Excel": {
                "time": "1 week",
                "task": "Learn formulas, sorting, filters and pivot tables.",
                "project": "Create a Student Marks Report."
            },
            "Power BI": {
                "time": "2 weeks",
                "task": "Learn charts, dashboards and basic data modelling.",
                "project": "Build a Sales Dashboard."
            },
            "Java": {
                "time": "2 weeks",
                "task": "Learn OOP, collections and basic problem solving.",
                "project": "Build a Student Management System."
            },
            "DSA": {
                "time": "3 weeks",
                "task": "Practice arrays, strings, searching and sorting.",
                "project": "Create a Problem-Solving Portfolio."
            },
            "OOP": {
                "time": "1 week",
                "task": "Practice classes, objects, inheritance and polymorphism.",
                "project": "Build a Library Management System."
            },
            "DBMS": {
                "time": "1 week",
                "task": "Learn SQL, keys, normalization and relationships.",
                "project": "Design a College Database."
            },
            "Problem Solving": {
                "time": "2 weeks",
                "task": "Solve beginner programming problems regularly.",
                "project": "Create a Coding Practice Portfolio."
            },
            "Deep Learning": {
                "time": "3 weeks",
                "task": "Learn neural network basics and model training.",
                "project": "Build an Image Classification Demo."
            }
        }

        if gaps:
            st.write("Your suggested next learning steps:")

            for number, skill in enumerate(gaps[:5], start=1):
                plan = learning_plan.get(
                    skill,
                    {
                        "time": "1 week",
                        "task": f"Learn the fundamentals of {skill}.",
                        "project": f"Build a small project using {skill}."
                    }
                )

                with st.expander(f"{number}. Learn {skill}"):
                    st.write(f"**Estimated time:** {plan['time']}")
                    st.write(f"**Practice task:** {plan['task']}")
                    st.write(f"**Project idea:** {plan['project']}")
        else:
            st.success("Explore advanced projects for your target career!")

            # ---------------- WHAT-IF SIMULATOR ----------------

            # WHAT-IF CAREER SIMULATOR

        st.header("🔮 What-If Career Simulator")

        if gaps:
            selected = st.multiselect(
                "Which skills do you plan to learn?",
                options=gaps
            )

            added_points = sum(
                career_data[skill]
                for skill in selected
            )

            future_score = min(score + added_points, 100)

            col1, col2 = st.columns(2)

            col1.metric("Current Readiness", f"{score}%")
            col2.metric(
                "Projected Readiness",
                f"{future_score}%",
                delta=f"+{future_score - score}%"
            )

            st.progress(future_score / 100)

            if selected:
                st.write("**Selected skills:**", ", ".join(selected))
                st.info(
                    "This is a hypothetical score based on skill weights, "
                    "not a prediction of job placement."
                )
            else:
                st.caption("Select one or more missing skills to simulate progress.")
        else:
            st.success("All listed skills are covered for this career profile.")

# ---------------- AI CAREER COACH PAGE ----------------
if selected_page == "🤖 AI Career Coach":
    # CAREER COACH

    st.header("🤖 SkillMirror Career Coach")

    if uploaded_file:
        st.write(f"**Target career:** {career}")

        if gaps:
            st.write(
                f"You currently match {len(detected_skills)} "
                f"of the listed career skills."
            )

            st.write("**Your recommended next steps:**")

            for skill in gaps[:3]:
                st.write(
                    f"- Focus on {skill} and complete a small practical project."
                )

            st.write(
                "Build projects, document them on GitHub, "
                "and update your resume as you gain skills."
            )
        else:
            st.write(
                "Your resume matches all listed skills. "
                "Try an advanced project and strengthen your portfolio."
            )
    else:
        st.info("Upload a PDF resume to receive career suggestions.")


    # ---------------- AI-POWERED CAREER COACH (LOCAL OLLAMA) ----------------
    st.divider()
    st.header("🧠 AI-Powered Resume & Career Coach")
    st.write(
        "Get AI-generated resume feedback, prioritized skill-gap advice, "
        "interview preparation tips, and a practical 30-day learning plan."
    )

    with st.expander("🔐 AI setup and privacy", expanded=False):
        st.write(
            "This version uses Ollama with a model running locally on your computer. "
            "No OpenAI API key or paid API credits are needed. Your resume text is sent "
            "to the local Ollama server at http://localhost:11434 and is not sent to OpenAI. "
            "You must install Ollama and download a model first."
        )

    if uploaded_file is None:
        st.info("Upload a PDF resume above first, then generate personalized AI advice.")
    else:
        ai_question = st.text_area(
            "What would you like the AI coach to focus on? (optional)",
            placeholder="Example: Help me prepare for a Data Scientist internship.",
            key="ai_coach_question",
        )

        if st.button("✨ Generate AI Career Advice", key="generate_ai_advice"):
            import requests

            resume_excerpt = resume_text[:12000]
            prompt = f"""You are a supportive, practical career coach for students.
Analyze the resume excerpt and career-matching results below.
Do not invent experience, qualifications, or skills.
Clearly separate observations from suggestions.

Use these headings:
1. Resume strengths
2. Skills to improve
3. Resume improvement suggestions
4. Internship and job preparation plan
5. Recommended next steps

Career coach focus: {ai_question}

Resume excerpt:
{resume_excerpt}
"""

            try:
                api_key = st.secrets["GROQ_API_KEY"]

                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an ethical, supportive career coach. Protect privacy and avoid unsupported claims."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3
                }

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                with st.spinner("AI is reviewing your resume and preparing recommendations..."):
                    response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=90
                    )

                response.raise_for_status()
                result = response.json()

                advice = result["choices"][0]["message"]["content"].strip()

                if advice:
                    st.success("AI career advice generated!")
                    st.markdown(advice)
                    st.caption(
                        "AI advice can contain mistakes. Verify recommendations "
                        "and edit your resume honestly. Your readiness score is "
                        "still a keyword-based estimate."
                    )
                else:
                    st.error("AI returned an empty response. Please try again.")

            except KeyError:
                st.error(
                    "GROQ_API_KEY is missing. Add it in your Streamlit app Secrets."
                )
            except requests.exceptions.HTTPError as error:
                st.error(f"Groq API request failed: {error.response.status_code}")
                st.caption(error.response.text[:1000])
            except requests.exceptions.RequestException as error:
                st.error(f"Could not connect to the AI service: {error}")
            except Exception as error:
                st.error(f"Could not generate AI advice: {error}")



# ---------------- PLACEMENT DASHBOARD PAGE ----------------
if selected_page == "🎯 Placement Dashboard":
    # =====================================================
    # PLACEMENT INTELLIGENCE DASHBOARD
    # Add this section at the END of app.py
    # =====================================================

    st.divider()
    st.title("🎯 Placement Intelligence Dashboard")

    st.write(
        "Explore potential company targets, check profile fit "
        "against configurable criteria, and plan your preparation."
    )

    # Load configurable company data
    PLACEMENT_FILE = Path(__file__).resolve().parent / "placement_data.json"

    try:
        with open(PLACEMENT_FILE, "r", encoding="utf-8") as f:
            placement_data = json.load(f)

        companies = placement_data.get("companies", [])

    except FileNotFoundError:
        st.error("placement_data.json not found. Project folder check please.")
        st.stop()

    except json.JSONDecodeError:
        st.error("placement_data.json  check format.")
        st.stop()

    # Collect student profile
    st.subheader("👩‍🎓 Your Placement Profile")

    profile_col1, profile_col2 = st.columns(2)

    with profile_col1:
        student_cgpa = st.number_input(
            "Current CGPA",
            min_value=0.0,
            max_value=10.0,
            value=7.0,
            step=0.1
        )

        student_branch = st.selectbox(
            "Branch",
            ["CSE", "IT", "ECE", "Other"]
        )

    with profile_col2:
        graduation_year = st.selectbox(
            "Graduation year",
            [2027, 2028, 2029, 2030, 2031],
            index=2
        )

        active_backlogs = st.number_input(
            "Current active backlogs",
            min_value=0,
            max_value=20,
            value=0,
            step=1
        )

    # Roles and skills
    all_roles = sorted({
        role
        for company in companies
        for role in company.get("roles", [])
    })

    target_role = st.selectbox(
        "Target job role",
        all_roles
    )

    all_skills = sorted({
        skill
        for company in companies
        for skill in company.get("skills", [])
    })

    # Reuse resume-detected skills if a PDF was analysed above
    resume_skills = (
        detected_skills
        if uploaded_file is not None
        else []
    )

    st.subheader("🧠 Skills You Have")

    selected_skills = st.multiselect(
        "Select skills you currently know",
        options=all_skills,
        default=[
            skill for skill in resume_skills
            if skill in all_skills
        ]
    )

    st.caption(
        "Resume matching is keyword-based. Add or remove skills "
        "to reflect your actual knowledge accurately."
    )

    # Eligibility and target matching
    st.subheader("🏢 Company Eligibility Checker")

    matching_role_companies = [
        company for company in companies
        if target_role in company.get("roles", [])
    ]

    if not matching_role_companies:
        st.info("role not found.")

    for company in matching_role_companies:
        reasons = []

        min_cgpa = company.get("min_cgpa", 0)
        allowed_branches = company.get("allowed_branches", [])
        graduation_years = company.get("graduation_years", [])
        max_backlogs = company.get("max_backlogs", 0)

        if student_cgpa < min_cgpa:
            reasons.append(f"CGPA below configured minimum ({min_cgpa})")

        if (
            "ALL" not in allowed_branches
            and student_branch not in allowed_branches
        ):
            reasons.append("Branch does not match configured criteria")

        if graduation_year not in graduation_years:
            reasons.append("Graduation year does not match configured criteria")

        if active_backlogs > max_backlogs:
            reasons.append("Backlogs exceed configured limit")

        company_skills = company.get("skills", [])
        missing_skills = [
            skill for skill in company_skills
            if skill not in selected_skills
        ]

        st.markdown(f"### {company['name']}")

        st.caption(
            company.get(
                "criteria_status",
                "Criteria not independently verified"
            )
        )

        if reasons:
            st.warning("Configured criteria mismatch: " + "; ".join(reasons))
        else:
            st.success("Matches the configured basic eligibility criteria")

        if missing_skills:
            st.write("**Skills to work on:** " + ", ".join(missing_skills))
        else:
            st.write("**Configured skills:** All listed skills selected")

        if company_skills:
            skill_match = (
                (len(company_skills) - len(missing_skills))
                / len(company_skills)
            ) * 100

            st.progress(skill_match / 100)
            st.caption(f"Listed skill match: {skill_match:.0f}%")

        st.divider()

    # Company Target Finder
    st.subheader("🎯 Your Company Target List")

    target_list = []

    for company in matching_role_companies:
        allowed_branches = company.get("allowed_branches", [])
        graduation_years = company.get("graduation_years", [])

        basic_match = (
            student_cgpa >= company.get("min_cgpa", 0)
            and (
                "ALL" in allowed_branches
                or student_branch in allowed_branches
            )
            and graduation_year in graduation_years
            and active_backlogs <= company.get("max_backlogs", 0)
        )

        company_skills = company.get("skills", [])
        missing_skills = [
            skill for skill in company_skills
            if skill not in selected_skills
        ]

        skill_match = (
            (len(company_skills) - len(missing_skills))
            / len(company_skills) * 100
            if company_skills else 0
        )

        target_list.append({
            "Company / Profile": company["name"],
            "Basic Criteria Match": (
                "Matches configured criteria"
                if basic_match else "Criteria mismatch"
            ),
            "Skill Match (%)": round(skill_match),
            "Missing Skills": ", ".join(missing_skills) or "None listed"
        })

    if target_list:
        target_list.sort(
            key=lambda item: (
                item["Basic Criteria Match"] == "Matches configured criteria",
                item["Skill Match (%)"]
            ),
            reverse=True
        )

        st.dataframe(
            target_list,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "This is a target shortlist based on your inputs and demo data, "
            "not a verified list of open vacancies or a placement guarantee."
        )

    # Placement Preparation Roadmap
    st.subheader("🗺️ Placement Preparation Roadmap")

    roadmap_skills = sorted({
        skill
        for company in matching_role_companies
        for skill in company.get("skills", [])
        if skill not in selected_skills
    })

    if roadmap_skills:
        st.write("Focus on these skills for your selected role:")

        for number, skill in enumerate(roadmap_skills, start=1):
            st.markdown(f"**{number}. {skill}**")

            if skill in ["DSA", "Problem Solving"]:
                st.write("Practice coding problems and explain your approach.")
            elif skill in ["SQL", "DBMS"]:
                st.write("Practise queries, joins, grouping and database concepts.")
            elif skill in ["Python", "Java", "OOP"]:
                st.write("Revise fundamentals and build a small working project.")
            elif skill in ["Statistics", "Pandas", "Machine Learning"]:
                st.write("Study the concepts and apply them to a small dataset.")
            else:
                st.write(
                    f"Learn the fundamentals of {skill} and add a practical "
                    "project to your portfolio."
                )

        st.info(
            "Suggested order only. Prioritise skills mentioned in the "
            "actual job description and practise aptitude/interview questions."
        )
    else:
        st.success(
            "All configured skills for this role are selected. "
            "Practise interviews and build a strong project portfolio."
        )
