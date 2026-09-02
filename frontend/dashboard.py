
import json
import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Workforce Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "processed"

# Authentication file
AUTH_FILE = ROOT / "data" / "users.json"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 26px;
        font-weight: 650;
        margin-top: 20px;
    }

    .small-text {
        font-size: 13px;
        opacity: 0.7;
    }

    .login-box {
        max-width: 500px;
        margin: auto;
        padding: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# AUTH FILE
# ============================================================

def create_default_users():

    AUTH_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    default_users = {

        "admin": {
            "password": hash_password("Admin@123"),
            "role": "ADMIN",
            "department": "ALL"
        },

        "hr": {
            "password": hash_password("HR@123"),
            "role": "HR",
            "department": "ALL"
        },

        "manager": {
            "password": hash_password("Manager@123"),
            "role": "MANAGER",
            "department": "Sales"
        }

    }

    with open(
        AUTH_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            default_users,
            file,
            indent=4
        )


def load_users():

    if not AUTH_FILE.exists():

        create_default_users()

    try:

        with open(
            AUTH_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        st.error(
            "Unable to read authentication database."
        )

        st.stop()


def save_users(users):

    with open(
        AUTH_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            users,
            file,
            indent=4
        )


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False


if "username" not in st.session_state:

    st.session_state.username = None


if "role" not in st.session_state:

    st.session_state.role = None


if "department" not in st.session_state:

    st.session_state.department = None


if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


if "page" not in st.session_state:

    st.session_state.page = "Dashboard"


# ============================================================
# LOGIN FUNCTION
# ============================================================

def login_user(username, password):

    users = load_users()

    username = username.strip().lower()

    if username not in users:

        return False

    stored_password = users[username]["password"]

    if hash_password(password) != stored_password:

        return False

    st.session_state.authenticated = True

    st.session_state.username = username

    st.session_state.role = users[username]["role"]

    st.session_state.department = users[username].get(
        "department",
        "ALL"
    )

    return True


# ============================================================
# LOGOUT
# ============================================================

def logout():

    st.session_state.authenticated = False

    st.session_state.username = None

    st.session_state.role = None

    st.session_state.department = None

    st.session_state.chat_history = []

    st.session_state.page = "Dashboard"

    st.rerun()


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login():

    st.markdown(
        "<div class='login-box'>",
        unsafe_allow_html=True
    )

    st.markdown(
        "# 🤖 AI Workforce Intelligence"
    )

    st.markdown(
        "### Enterprise HR Analytics Platform"
    )

    st.divider()

    st.subheader("🔐 Login")

    username = st.text_input(
        "Username",
        placeholder="Enter username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    login_button = st.button(
        "🔓 Login",
        use_container_width=True
    )

    if login_button:

        if not username or not password:

            st.error(
                "Please enter username and password."
            )

        elif login_user(
            username,
            password
        ):

            st.success(
                "Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )

    st.divider()

    st.caption(
        "Authorized personnel only."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# AUTHENTICATION CHECK
# ============================================================

if not st.session_state.authenticated:

    show_login()

    st.stop()


# ============================================================
# CURRENT USER
# ============================================================

CURRENT_USER = st.session_state.username
CURRENT_ROLE = st.session_state.role
CURRENT_DEPARTMENT = st.session_state.department


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🤖 AI Workforce Intelligence Platform'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Enterprise HR AI — Attrition, Engagement, Skill Gaps & Upskilling'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    scores = pd.read_csv(
        DATA / "attrition_scores.csv"
    )

    metrics = pd.read_csv(
        DATA / "model_metrics.csv"
    ).iloc[0]

    gaps = pd.read_csv(
        DATA / "organization_skill_gaps.csv"
    )

    intel = pd.read_csv(
        DATA / "employee_intelligence.csv"
    )

    return scores, metrics, gaps, intel


try:

    scores, metrics, gaps, intel = load_data()

except Exception as e:

    st.error(
        "Unable to load dashboard data."
    )

    st.exception(e)

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

scores["Attrition_Prob"] = pd.to_numeric(
    scores["Attrition_Prob"],
    errors="coerce"
).fillna(0)


if "Department" not in scores.columns:

    scores["Department"] = "Unknown"


if "EmployeeNumber" in scores.columns:

    scores["EmployeeNumber"] = pd.to_numeric(
        scores["EmployeeNumber"],
        errors="coerce"
    )


if "Risk" not in scores.columns:

    scores["Risk"] = "LOW"


# ============================================================
# ROLE-BASED DATA ACCESS
# ============================================================

# ADMIN and HR can see everything.
#
# MANAGER can only see employees belonging
# to their assigned department.

if CURRENT_ROLE == "MANAGER":

    visible_scores = scores[
        scores["Department"].astype(str)
        == str(CURRENT_DEPARTMENT)
    ].copy()

else:

    visible_scores = scores.copy()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Dashboard Controls")

st.sidebar.success(
    f"👤 {CURRENT_USER}\n\n"
    f"Role: **{CURRENT_ROLE}**"
)


if CURRENT_ROLE == "MANAGER":

    st.sidebar.info(
        f"🏢 Department: **{CURRENT_DEPARTMENT}**"
    )

else:

    st.sidebar.info(
        "🏢 Access: **All Departments**"
    )


st.sidebar.divider()


# ============================================================
# NAVIGATION
# ============================================================

st.sidebar.subheader("📌 Navigation")

page_options = [
    "Dashboard",
    "Employee Drill-down",
    "HR AI Assistant",
    "Change Password"
]


# Managers still get the same navigation,
# but the data shown is restricted.

selected_page = st.sidebar.radio(
    "Go to",
    page_options,
    index=page_options.index(
        st.session_state.page
    )
)


st.session_state.page = selected_page


# ============================================================
# LOGOUT
# ============================================================

st.sidebar.divider()

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    logout()


# ============================================================
# CHANGE PASSWORD PAGE
# ============================================================

if selected_page == "Change Password":

    st.title("🔑 Change Password")

    st.caption(
        f"Change password for **{CURRENT_USER}**"
    )

    st.divider()

    old_password = st.text_input(
        "Current Password",
        type="password"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password"
    )

    if st.button(
        "🔐 Update Password",
        use_container_width=True
    ):

        users = load_users()

        current_hash = hash_password(
            old_password
        )

        stored_hash = users[
            CURRENT_USER
        ]["password"]

        if current_hash != stored_hash:

            st.error(
                "Current password is incorrect."
            )

        elif len(new_password) < 8:

            st.error(
                "New password must contain at least 8 characters."
            )

        elif new_password != confirm_password:

            st.error(
                "New passwords do not match."
            )

        elif old_password == new_password:

            st.error(
                "New password must be different from the current password."
            )

        else:

            users[
                CURRENT_USER
            ]["password"] = hash_password(
                new_password
            )

            save_users(users)

            st.success(
                "✅ Password changed successfully."
            )

            st.info(
                "Your new password will be required the next time you log in."
            )

    st.stop()


# ============================================================
# RISK CONFIGURATION
# ============================================================

st.sidebar.subheader(
    "⚠️ Risk Configuration"
)

threshold = st.sidebar.slider(
    "High-Risk Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.60,
    step=0.05,
    format="%.2f"
)

st.sidebar.caption(
    f"Current threshold: **{threshold:.0%}**"
)


# ============================================================
# DYNAMIC RISK CALCULATION
# ============================================================

def calculate_risk(
    probability,
    threshold_value
):

    if probability >= threshold_value:

        return "HIGH"

    elif probability >= threshold_value * 0.60:

        return "MEDIUM"

    else:

        return "LOW"


scores["Dynamic_Risk"] = scores[
    "Attrition_Prob"
].apply(
    lambda x: calculate_risk(
        x,
        threshold
    )
)


# Apply same risk calculation to visible data

visible_scores["Dynamic_Risk"] = visible_scores[
    "Attrition_Prob"
].apply(
    lambda x: calculate_risk(
        x,
        threshold
    )
)


# ============================================================
# FILTERS
# ============================================================

st.sidebar.subheader(
    "🔎 Filters"
)


departments = sorted(
    visible_scores["Department"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


selected_departments = st.sidebar.multiselect(
    "Department",
    options=departments,
    default=departments
)


risk_options = [
    "LOW",
    "MEDIUM",
    "HIGH"
]


selected_risks = st.sidebar.multiselect(
    "Risk Level",
    options=risk_options,
    default=risk_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_scores = visible_scores[
    visible_scores["Department"]
    .astype(str)
    .isin(
        selected_departments
    )
    &
    visible_scores["Dynamic_Risk"]
    .isin(
        selected_risks
    )
].copy()


# ============================================================
# REFRESH
# ============================================================

if st.sidebar.button(
    "🔄 Refresh Data",
    use_container_width=True
):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# DOWNLOAD DATA
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "📥 Export"
)


csv_data = filtered_scores.to_csv(
    index=False
).encode("utf-8")


st.sidebar.download_button(
    label="Download Employee Data",
    data=csv_data,
    file_name="filtered_employee_data.csv",
    mime="text/csv",
    use_container_width=True
)


# ============================================================
# DASHBOARD PAGE
# ============================================================

if selected_page == "Dashboard":

    # ========================================================
    # KPI SECTION
    # ========================================================

    total_employees = len(
        filtered_scores
    )


    high_risk_count = int(
        (
            filtered_scores[
                "Dynamic_Risk"
            ]
            == "HIGH"
        ).sum()
    )


    medium_risk_count = int(
        (
            filtered_scores[
                "Dynamic_Risk"
            ]
            == "MEDIUM"
        ).sum()
    )


    low_risk_count = int(
        (
            filtered_scores[
                "Dynamic_Risk"
            ]
            == "LOW"
        ).sum()
    )


    if total_employees > 0:

        average_attrition = (
            filtered_scores[
                "Attrition_Prob"
            ].mean()
        )

    else:

        average_attrition = 0


    roc_auc = float(
        metrics["roc_auc"]
    )


    precision = float(
        metrics["precision"]
    )


    recall = float(
        metrics["recall"]
    )


    f1 = float(
        metrics["f1"]
    )


    c1, c2, c3, c4, c5 = st.columns(5)


    c1.metric(
        "👥 Employees",
        f"{total_employees:,}"
    )


    c2.metric(
        "🔴 High Risk",
        f"{high_risk_count:,}"
    )


    c3.metric(
        "🟡 Medium Risk",
        f"{medium_risk_count:,}"
    )


    c4.metric(
        "📊 Avg Attrition",
        f"{average_attrition:.1%}"
    )


    c5.metric(
        "🎯 ROC-AUC",
        f"{roc_auc:.3f}"
    )


    st.divider()


    # ========================================================
    # ROLE ACCESS INFORMATION
    # ========================================================

    if CURRENT_ROLE == "ADMIN":

        st.success(
            "🔐 ADMIN ACCESS — Full workforce visibility enabled."
        )

    elif CURRENT_ROLE == "HR":

        st.info(
            "👥 HR ACCESS — Workforce analytics available."
        )

    elif CURRENT_ROLE == "MANAGER":

        st.warning(
            f"🏢 MANAGER ACCESS — "
            f"Showing only **{CURRENT_DEPARTMENT}** department."
        )


    # ========================================================
    # RISK CONFIGURATION
    # ========================================================

    st.subheader(
        "⚠️ Current Risk Configuration"
    )


    r1, r2, r3 = st.columns(3)


    r1.metric(
        "High-Risk Threshold",
        f"{threshold:.0%}"
    )


    r2.metric(
        "High-Risk Employees",
        f"{high_risk_count:,}"
    )


    if total_employees > 0:

        high_risk_percentage = (
            high_risk_count
            / total_employees
        )

    else:

        high_risk_percentage = 0


    r3.metric(
        "High-Risk Percentage",
        f"{high_risk_percentage:.1%}"
    )


    st.info(
        f"Employees with an attrition probability "
        f"of **{threshold:.0%} or higher** are classified "
        f"as HIGH risk."
    )


    # ========================================================
    # DEPARTMENT ANALYSIS
    # ========================================================

    st.divider()

    st.subheader(
        "🏢 Attrition Risk by Department"
    )


    dept = (
        filtered_scores
        .groupby("Department")[
            "Attrition_Prob"
        ]
        .mean()
        .sort_values(
            ascending=False
        )
    )


    if dept.empty:

        st.warning(
            "No department data available "
            "for the selected filters."
        )

    else:

        st.bar_chart(
            dept,
            use_container_width=True
        )


    # ========================================================
    # RISK DISTRIBUTION
    # ========================================================

    st.subheader(
        "📊 Risk Distribution"
    )


    risk_counts = (
        filtered_scores[
            "Dynamic_Risk"
        ]
        .value_counts()
        .reindex(
            [
                "LOW",
                "MEDIUM",
                "HIGH"
            ]
        )
        .fillna(0)
    )


    st.bar_chart(
        risk_counts,
        use_container_width=True
    )


    # ========================================================
    # MODEL PERFORMANCE
    # ========================================================

    st.divider()

    st.subheader(
        "🧠 Model Performance"
    )


    m1, m2, m3, m4 = st.columns(4)


    m1.metric(
        "Precision",
        f"{precision:.3f}"
    )


    m2.metric(
        "Recall",
        f"{recall:.3f}"
    )


    m3.metric(
        "F1 Score",
        f"{f1:.3f}"
    )


    m4.metric(
        "ROC-AUC",
        f"{roc_auc:.3f}"
    )


    # ========================================================
    # ORGANIZATION SKILL GAPS
    # ========================================================

    st.divider()

    st.subheader(
        "🧩 Critical Organisation Skill Gaps"
    )


    if CURRENT_ROLE == "MANAGER":

        st.info(
            "Organization-wide skill gaps are restricted for Manager accounts."
        )

    elif gaps.empty:

        st.info(
            "No role-mapped skill gaps were produced. "
            "Add or verify O*NET role mappings."
        )

    else:

        display_gaps = gaps.copy()


        st.dataframe(
            display_gaps.head(20),
            use_container_width=True,
            hide_index=True
        )


        gaps_csv = display_gaps.to_csv(
            index=False
        ).encode("utf-8")


        st.download_button(
            "📥 Download Skill Gap Report",
            data=gaps_csv,
            file_name="organization_skill_gaps.csv",
            mime="text/csv"
        )


    # ========================================================
    # UPSKILLING
    # ========================================================

    st.divider()

    st.subheader(
        "🎓 Upskilling Recommendations"
    )


    if intel.empty:

        st.info(
            "No employee intelligence data available."
        )

    else:

        recommendation_columns = [
            "EmployeeNumber",
            "JobRole",
            "Attrition_Prob",
            "Risk",
            "SkillGap",
            "Recommendation"
        ]


        available_columns = [
            column
            for column in recommendation_columns
            if column in intel.columns
        ]


        recommendation_data = intel[
            available_columns
        ].copy()


        # Restrict managers to their department
        if CURRENT_ROLE == "MANAGER":

            if "Department" in intel.columns:

                recommendation_data = recommendation_data[
                    intel["Department"].astype(str)
                    == str(CURRENT_DEPARTMENT)
                ]


        if "Attrition_Prob" in recommendation_data.columns:

            recommendation_data[
                "Attrition_Prob"
            ] = pd.to_numeric(
                recommendation_data[
                    "Attrition_Prob"
                ],
                errors="coerce"
            )


        st.dataframe(
            recommendation_data.head(50),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# EMPLOYEE DRILL-DOWN
# ============================================================

if selected_page == "Employee Drill-down":

    st.title(
        "👤 Employee Drill-down"
    )


    st.caption(
        "Employee-level workforce intelligence"
    )


    if CURRENT_ROLE == "MANAGER":

        st.info(
            f"You can only view employees in the "
            f"**{CURRENT_DEPARTMENT}** department."
        )


    if filtered_scores.empty:

        st.warning(
            "No employees match the current filters."
        )

    else:

        employee_ids = (
            filtered_scores[
                "EmployeeNumber"
            ]
            .dropna()
            .astype(int)
            .tolist()
        )


        employee_id = st.selectbox(
            "Select Employee",
            employee_ids
        )


        selected_employee = filtered_scores[
            filtered_scores[
                "EmployeeNumber"
            ] == employee_id
        ]


        if not selected_employee.empty:

            employee_row = selected_employee.iloc[0]


            e1, e2, e3, e4 = st.columns(4)


            e1.metric(
                "Employee ID",
                str(employee_id)
            )


            e2.metric(
                "Attrition Probability",
                f"{employee_row['Attrition_Prob']:.1%}"
            )


            e3.metric(
                "Risk",
                employee_row["Dynamic_Risk"]
            )


            e4.metric(
                "Department",
                str(employee_row["Department"])
            )


            st.write(
                "### Employee Information"
            )


            employee_data = employee_row.to_dict()


            st.json(
                employee_data
            )


# ============================================================
# HR AI ASSISTANT
# ============================================================

if selected_page == "HR AI Assistant":

    st.title(
        "🤖 HR AI Assistant"
    )


    st.caption(
        f"Ask questions about workforce intelligence. "
        f"Your access level is **{CURRENT_ROLE}**."
    )


    # ========================================================
    # CHATBOT FUNCTION
    # ========================================================

    def hr_chatbot(
        question,
        scores_data,
        metrics_data,
        gaps_data,
        intel_data,
        threshold_value,
        user_role,
        user_department
    ):

        q = str(
            question
        ).lower().strip()


        # ----------------------------------------------------
        # EMPLOYEE QUESTIONS
        # ----------------------------------------------------

        if (
            "employee" in q
            or "employees" in q
            or "workforce" in q
            or q == "everything"
        ):

            total = len(
                scores_data
            )


            high = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "HIGH"
                ).sum()
            )


            medium = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "MEDIUM"
                ).sum()
            )


            low = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "LOW"
                ).sum()
            )


            average_probability = (
                scores_data[
                    "Attrition_Prob"
                ].mean()
                if total > 0
                else 0
            )


            scope = (
                f"{user_department} department"
                if user_role == "MANAGER"
                else "the entire workforce"
            )


            return (
                "### 👥 Workforce Summary\n\n"
                f"- **Access Scope:** {scope}\n"
                f"- **Total Employees:** {total:,}\n"
                f"- **High Risk:** {high:,}\n"
                f"- **Medium Risk:** {medium:,}\n"
                f"- **Low Risk:** {low:,}\n"
                f"- **Average Attrition Probability:** "
                f"{average_probability:.1%}\n"
                f"- **Current Threshold:** "
                f"{threshold_value:.0%}"
            )


        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        elif (
            "risk" in q
            or "high risk" in q
            or "risky" in q
        ):

            high = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "HIGH"
                ).sum()
            )


            medium = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "MEDIUM"
                ).sum()
            )


            low = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "LOW"
                ).sum()
            )


            total = len(
                scores_data
            )


            percentage = (
                high / total
                if total > 0
                else 0
            )


            return (
                "### ⚠️ Risk Analysis\n\n"
                f"- 🔴 **High Risk:** {high:,}\n"
                f"- 🟡 **Medium Risk:** {medium:,}\n"
                f"- 🟢 **Low Risk:** {low:,}\n"
                f"- **High-Risk Percentage:** "
                f"{percentage:.1%}\n\n"
                f"The current high-risk threshold is "
                f"**{threshold_value:.0%}**."
            )


        # ----------------------------------------------------
        # THRESHOLD
        # ----------------------------------------------------

        elif (
            "threshold" in q
            or "cutoff" in q
        ):

            high = int(
                (
                    scores_data[
                        "Dynamic_Risk"
                    ]
                    == "HIGH"
                ).sum()
            )


            return (
                "### 🎚️ Risk Threshold\n\n"
                f"The current threshold is "
                f"**{threshold_value:.0%}**.\n\n"
                "**Classification logic:**\n\n"
                f"- Probability >= "
                f"**{threshold_value:.0%}** "
                "→ 🔴 HIGH\n"
                f"- Probability >= "
                f"**{threshold_value * 0.60:.0%}** "
                "→ 🟡 MEDIUM\n"
                f"- Probability < "
                f"**{threshold_value * 0.60:.0%}** "
                "→ 🟢 LOW\n\n"
                f"Currently **{high:,} employees** "
                "are HIGH risk."
            )


        # ----------------------------------------------------
        # ATTRITION
        # ----------------------------------------------------

        elif (
            "attrition" in q
            or "leaving" in q
            or "leave" in q
            or "turnover" in q
        ):

            average_probability = (
                scores_data[
                    "Attrition_Prob"
                ].mean()
            )


            highest_probability = (
                scores_data[
                    "Attrition_Prob"
                ].max()
            )


            return (
                "### 📉 Attrition Analysis\n\n"
                f"- **Average Probability:** "
                f"{average_probability:.1%}\n"
                f"- **Highest Probability:** "
                f"{highest_probability:.1%}\n"
                f"- **High-Risk Employees:** "
                f"{int((scores_data['Dynamic_Risk'] == 'HIGH').sum()):,}"
            )


        # ----------------------------------------------------
        # DEPARTMENT
        # ----------------------------------------------------

        elif (
            "department" in q
            or "departments" in q
            or "team" in q
        ):

            department_data = (
                scores_data
                .groupby("Department")[
                    "Attrition_Prob"
                ]
                .mean()
                .sort_values(
                    ascending=False
                )
            )


            if department_data.empty:

                return (
                    "No department information "
                    "is available."
                )


            highest_department = (
                department_data.index[0]
            )


            highest_probability = (
                department_data.iloc[0]
            )


            lowest_department = (
                department_data.index[-1]
            )


            lowest_probability = (
                department_data.iloc[-1]
            )


            result = (
                "### 🏢 Department Analysis\n\n"
                f"**Highest average attrition:** "
                f"{highest_department} "
                f"({highest_probability:.1%})\n\n"
                f"**Lowest average attrition:** "
                f"{lowest_department} "
                f"({lowest_probability:.1%})\n\n"
                "### Department-wise Risk\n\n"
            )


            for department, probability in department_data.items():

                result += (
                    f"- **{department}:** "
                    f"{probability:.1%}\n"
                )


            return result


        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------

        elif (
            "roc" in q
            or "auc" in q
            or "precision" in q
            or "recall" in q
            or "f1" in q
            or "model performance" in q
        ):

            # Manager does not get model internals

            if user_role == "MANAGER":

                return (
                    "🔒 **Access Restricted**\n\n"
                    "Model performance metrics are "
                    "available to ADMIN and HR users only."
                )


            return (
                "### 🧠 Model Performance\n\n"
                f"- **Precision:** "
                f"{float(metrics_data['precision']):.3f}\n"
                f"- **Recall:** "
                f"{float(metrics_data['recall']):.3f}\n"
                f"- **F1 Score:** "
                f"{float(metrics_data['f1']):.3f}\n"
                f"- **ROC-AUC:** "
                f"{float(metrics_data['roc_auc']):.3f}\n"
                f"- **Test Rows:** "
                f"{int(metrics_data['test_rows']):,}"
            )


        # ----------------------------------------------------
        # SKILL GAPS
        # ----------------------------------------------------

        elif (
            "skill" in q
            or "skills" in q
            or "skill gap" in q
            or "skill gaps" in q
        ):

            if user_role == "MANAGER":

                return (
                    "🔒 **Access Restricted**\n\n"
                    "Organization-wide skill gap analytics "
                    "are available to ADMIN and HR users only."
                )


            if gaps_data.empty:

                return (
                    "No organization-level skill "
                    "gaps are currently available."
                )


            result = (
                "### 🧩 Critical Skill Gaps\n\n"
            )


            for _, row in gaps_data.head(10).iterrows():

                skill = row.get(
                    "Skill",
                    "Unknown"
                )


                missing = row.get(
                    "EmployeesMissing",
                    0
                )


                severity = row.get(
                    "Severity",
                    "Unknown"
                )


                try:

                    missing_value = int(
                        missing
                    )

                except:

                    missing_value = 0


                result += (
                    f"- **{skill}** → "
                    f"{missing_value:,} employees "
                    f"({severity})\n"
                )


            return result


        # ----------------------------------------------------
        # UPSKILLING
        # ----------------------------------------------------

        elif (
            "upskill" in q
            or "training" in q
            or "recommendation" in q
            or "recommendations" in q
            or "learning" in q
        ):

            if intel_data.empty:

                return (
                    "No employee intelligence "
                    "data is available."
                )


            intelligence = intel_data.copy()


            if user_role == "MANAGER":

                if "Department" in intelligence.columns:

                    intelligence = intelligence[
                        intelligence[
                            "Department"
                        ].astype(str)
                        == str(
                            user_department
                        )
                    ]


            if "Risk" in intelligence.columns:

                high_risk = intelligence[
                    intelligence["Risk"] == "HIGH"
                ]

            else:

                high_risk = intelligence


            if high_risk.empty:

                return (
                    "No HIGH-risk employees with "
                    "available recommendations were found."
                )


            result = (
                "### 🎓 Upskilling Recommendations\n\n"
            )


            for _, row in high_risk.head(10).iterrows():

                employee_id = row.get(
                    "EmployeeNumber",
                    "Unknown"
                )


                job_role = row.get(
                    "JobRole",
                    "Unknown"
                )


                recommendation = row.get(
                    "Recommendation",
                    "No recommendation available"
                )


                result += (
                    f"- **Employee {employee_id}** "
                    f"({job_role}) → "
                    f"{recommendation}\n"
                )


            return result


        # ----------------------------------------------------
        # GREETING / HELP
        # ----------------------------------------------------

        elif (
            q in [
                "hi",
                "hello",
                "hey",
                "help"
            ]
            or "what can you do" in q
        ):

            if user_role == "MANAGER":

                return (
                    "### 👋 Hello!\n\n"
                    f"You are logged in as a **MANAGER** "
                    f"for the **{user_department}** department.\n\n"
                    "You can ask me:\n\n"
                    "- 👥 How many employees are in my department?\n"
                    "- 🔴 How many employees are high risk?\n"
                    "- 📉 What is the average attrition?\n"
                    "- 🏢 What is my department's attrition risk?\n"
                    "- 🎓 Show upskilling recommendations\n"
                    "- 🎚️ What is the current threshold?\n"
                )


            return (
                "### 👋 Hello!\n\n"
                f"You are logged in as **{user_role}**.\n\n"
                "You can ask me:\n\n"
                "- 👥 How many employees are there?\n"
                "- 🔴 How many employees are high risk?\n"
                "- 📉 What is the average attrition?\n"
                "- 🏢 Which department has the highest risk?\n"
                "- 🧩 What are the major skill gaps?\n"
                "- 🎓 Show upskilling recommendations\n"
                "- 🧠 What is the ROC-AUC?\n"
                "- 🎚️ What is the current threshold?\n"
            )


        # ----------------------------------------------------
        # UNKNOWN
        # ----------------------------------------------------

        else:

            return (
                "I couldn't find an answer to that question "
                "from the current workforce dataset.\n\n"
                "Try asking about:\n\n"
                "**employees, attrition, risk, departments, "
                "skill gaps, ROC-AUC, threshold, or upskilling.**"
            )


    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    for message in st.session_state.chat_history:

        if message["role"] == "user":

            with st.chat_message("user"):

                st.write(
                    message["content"]
                )

        else:

            with st.chat_message("assistant"):

                st.markdown(
                    message["content"]
                )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    question = st.chat_input(
        "Ask HR AI something..."
    )


    # ========================================================
    # PROCESS QUESTION
    # ========================================================

    if question:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": question
            }
        )


        answer = hr_chatbot(
            question=question,
            scores_data=visible_scores,
            metrics_data=metrics,
            gaps_data=gaps,
            intel_data=intel,
            threshold_value=threshold,
            user_role=CURRENT_ROLE,
            user_department=CURRENT_DEPARTMENT
        )


        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        st.rerun()


    # ========================================================
    # CHAT CONTROLS
    # ========================================================

    if st.session_state.chat_history:

        if st.button(
            "🗑️ Clear Chat"
        ):

            st.session_state.chat_history = []

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Workforce Intelligence Platform | "
    "Enterprise HR Analytics | "
    f"Logged in as {CURRENT_USER} ({CURRENT_ROLE})"
)