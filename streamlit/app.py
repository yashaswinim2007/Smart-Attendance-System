

import streamlit as st
import subprocess
import csv
import io
import pandas as pd
from pathlib import Path
from datetime import date

# ==========================================
# CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

JAVA_DIR = Path(__file__).resolve().parent.parent / "java"
JAVA_FILE = JAVA_DIR / "Main.java"
CLASS_FILE = JAVA_DIR / "Main.class"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "login_error" not in st.session_state:
    st.session_state.login_error = False

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background: #f3f6fc;
}

[data-testid="stSidebar"] {
    background: #172554;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.login-container {
    background: white;
    padding: 35px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 5px 25px rgba(0,0,0,0.07);
}

.main-heading {
    font-size: 34px;
    font-weight: 800;
    color: #172554;
}

.sub-heading {
    color: #64748b;
    font-size: 15px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    min-height: 115px;
}

.metric-label {
    color: #64748b;
    font-size: 14px;
}

.metric-value {
    color: #172554;
    font-size: 30px;
    font-weight: bold;
}

div.stButton > button {
    background: #2563eb;
    color: white;
    border-radius: 9px;
    border: none;
    min-height: 42px;
}

div.stButton > button:hover {
    background: #1d4ed8;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# JAVA BACKEND CONNECTION
# ==========================================

def run_java(*arguments):

    if not JAVA_FILE.exists():
        st.error(f"Main.java not found: {JAVA_FILE}")
        return None

    try:

        if (
            not CLASS_FILE.exists()
            or JAVA_FILE.stat().st_mtime > CLASS_FILE.stat().st_mtime
        ):

            compile_result = subprocess.run(
                ["javac", "Main.java"],
                cwd=str(JAVA_DIR),
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                raise Exception(compile_result.stderr)

        result = subprocess.run(
            [
                "java",
                "-cp",
                str(JAVA_DIR),
                "Main",
                *map(str, arguments)
            ],
            cwd=str(JAVA_DIR),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(result.stderr or result.stdout)

        output = result.stdout.strip()

        if output.startswith("ERROR:"):
            raise Exception(output)

        return output

    except Exception as error:
        st.error(f"Java Backend Error: {error}")
        return None


# ==========================================
# DATA FUNCTIONS
# ==========================================

def get_students():

    output = run_java("list")
    students = []

    if output:

        for line in output.splitlines():

            parts = line.split("|", 2)

            if len(parts) == 3:

                students.append({
                    "Student ID": parts[0],
                    "Name": parts[1],
                    "Department": parts[2]
                })

    return students


def get_records():

    output = run_java("records")
    records = []

    if output:

        for line in output.splitlines():

            parts = line.split("|", 2)

            if len(parts) == 3:

                records.append({
                    "Student ID": parts[0],
                    "Date": parts[1],
                    "Status": parts[2]
                })

    return records


# ==========================================
# LOGIN PAGE
# ==========================================

def login_page():

    st.markdown("<br><br>", unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        st.markdown("""
        <div style="text-align:center;">
            <div style="font-size:65px;">🎓</div>
            <h1 style="color:#172554;">Smart Attendance</h1>
            <p style="color:#64748b;">
                Student Attendance Management System
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):

            st.subheader("Admin Login")

            username = st.text_input(
                "Username",
                placeholder="Enter username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password"
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if submitted:

                if (
                    username == ADMIN_USERNAME
                    and password == ADMIN_PASSWORD
                ):

                    st.session_state.logged_in = True
                    st.session_state.login_error = False
                    st.rerun()

                else:

                    st.session_state.login_error = True

        if st.session_state.login_error:
            st.error("Invalid username or password.")

        st.info("Demo username: admin | Password: admin123")


# ==========================================
# MAIN APPLICATION
# ==========================================

def main_application():

    # Sidebar
    st.sidebar.title("🎓 Smart Attendance")
    st.sidebar.caption("ADMIN PANEL")

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "MENU",
        [
            "Dashboard",
            "Add Student",
            "View Students",
            "Mark Attendance",
            "Attendance Records",
            "Student Reports"
        ]
    )

    st.sidebar.markdown("---")

    st.sidebar.success("Admin Logged In")

    if st.sidebar.button("Logout", use_container_width=True):

        st.session_state.logged_in = False
        st.session_state.login_error = False
        st.rerun()

    students = get_students()
    records = get_records()

    # ======================================
    # DASHBOARD
    # ======================================

    if page == "Dashboard":

        st.markdown(
            '<div class="main-heading">Dashboard</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sub-heading">Welcome to your Smart Attendance System Admin Panel.</div>',
            unsafe_allow_html=True
        )

        st.write("")

        total_students = len(students)
        total_records = len(records)

        present = sum(
            1 for r in records
            if r["Status"].lower() == "present"
        )

        absent = sum(
            1 for r in records
            if r["Status"].lower() == "absent"
        )

        percentage = (
            present / total_records * 100
            if total_records else 0
        )

        c1, c2, c3, c4 = st.columns(4)

        values = [
            ("Total Students", total_students, "👨‍🎓"),
            ("Total Records", total_records, "📋"),
            ("Present", present, "✅"),
            ("Absent", absent, "❌")
        ]

        for col, item in zip([c1, c2, c3, c4], values):

            with col:

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{item[2]} {item[0]}</div>
                    <div class="metric-value">{item[1]}</div>
                </div>
                """, unsafe_allow_html=True)

        st.write("")
        st.subheader("Overall Attendance")

        st.progress(int(percentage))
        st.write(f"**{percentage:.1f}%** attendance")

        st.write("")

        left, right = st.columns(2)

        with left:

            st.subheader("Attendance Distribution")

            if total_records:

                chart_data = pd.DataFrame({
                    "Status": ["Present", "Absent"],
                    "Count": [present, absent]
                })

                st.bar_chart(
                    chart_data.set_index("Status")
                )

            else:
                st.info("No attendance data available.")

        with right:

            st.subheader("Recent Attendance")

            if records:

                st.dataframe(
                    records[-5:][::-1],
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No recent records.")

    # ======================================
    # ADD STUDENT
    # ======================================

    elif page == "Add Student":

        st.markdown(
            '<div class="main-heading">Add New Student</div>',
            unsafe_allow_html=True
        )

        with st.form("add_student_form"):

            student_id = st.number_input(
                "Student ID",
                min_value=1,
                step=1
            )

            name = st.text_input("Student Name")

            department = st.selectbox(
                "Department",
                [
                    "Computer Science",
                    "Information Technology",
                    "Electronics",
                    "Mechanical",
                    "Civil",
                    "Other"
                ]
            )

            submitted = st.form_submit_button("Add Student")

            if submitted:

                if not name.strip():

                    st.warning("Enter student name.")

                elif any(
                    s["Student ID"] == str(student_id)
                    for s in students
                ):

                    st.error("Student ID already exists.")

                else:

                    result = run_java(
                        "add",
                        student_id,
                        name.strip(),
                        department
                    )

                    if result and result.startswith("SUCCESS"):

                        st.success("Student added successfully!")
                        st.rerun()

    # ======================================
    # VIEW STUDENTS
    # ======================================

    elif page == "View Students":

        st.markdown(
            '<div class="main-heading">Student Details</div>',
            unsafe_allow_html=True
        )

        search = st.text_input(
            "🔍 Search by student name or ID"
        )

        filtered = [
            s for s in students
            if search.lower() in
            (s["Name"] + " " + s["Student ID"]).lower()
        ]

        if filtered:

            st.success(f"{len(filtered)} student(s) found.")

            st.dataframe(
                filtered,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No matching students found.")

    # ======================================
    # MARK ATTENDANCE
    # ======================================

    elif page == "Mark Attendance":

        st.markdown(
            '<div class="main-heading">Mark Attendance</div>',
            unsafe_allow_html=True
        )

        if not students:

            st.warning("Please add students first.")

        else:

            student_options = {
                f'{s["Student ID"]} - {s["Name"]}': s["Student ID"]
                for s in students
            }

            with st.form("attendance_form"):

                selected = st.selectbox(
                    "Select Student",
                    list(student_options.keys())
                )

                attendance_date = st.date_input(
                    "Attendance Date",
                    value=date.today()
                )

                status = st.radio(
                    "Attendance Status",
                    ["Present", "Absent"],
                    horizontal=True
                )

                submitted = st.form_submit_button(
                    "Save Attendance"
                )

                if submitted:

                    result = run_java(
                        "mark",
                        student_options[selected],
                        attendance_date.isoformat(),
                        status
                    )

                    if result and result.startswith("SUCCESS"):

                        st.success("Attendance saved successfully!")
                        st.rerun()

    # ======================================
    # ATTENDANCE RECORDS
    # ======================================

    elif page == "Attendance Records":

        st.markdown(
            '<div class="main-heading">Attendance Records</div>',
            unsafe_allow_html=True
        )

        if records:

            st.dataframe(
                records[::-1],
                use_container_width=True,
                hide_index=True
            )

            output = io.StringIO()

            writer = csv.DictWriter(
                output,
                fieldnames=["Student ID", "Date", "Status"]
            )

            writer.writeheader()
            writer.writerows(records)

            st.download_button(
                "⬇ Download CSV",
                data=output.getvalue(),
                file_name="attendance_records.csv",
                mime="text/csv"
            )

        else:

            st.info("No attendance records available.")

    # ======================================
    # STUDENT REPORTS
    # ======================================

    elif page == "Student Reports":

        st.markdown(
            '<div class="main-heading">Student Attendance Reports</div>',
            unsafe_allow_html=True
        )

        report_data = []

        for student in students:

            student_records = [
                r for r in records
                if r["Student ID"] == student["Student ID"]
            ]

            total = len(student_records)

            present_count = sum(
                1 for r in student_records
                if r["Status"].lower() == "present"
            )

            absent_count = total - present_count

            percentage = (
                present_count / total * 100
                if total else 0
            )

            report_data.append({
                "Student ID": student["Student ID"],
                "Name": student["Name"],
                "Department": student["Department"],
                "Total Classes": total,
                "Present": present_count,
                "Absent": absent_count,
                "Attendance %": f"{percentage:.1f}%"
            })

        if report_data:

            st.dataframe(
                report_data,
                use_container_width=True,
                hide_index=True
            )

            selected_id = st.selectbox(
                "Select student for detailed report",
                [s["Student ID"] for s in students]
            )

            selected_student = next(
                s for s in students
                if s["Student ID"] == selected_id
            )

            individual_records = [
                r for r in records
                if r["Student ID"] == selected_id
            ]

            total = len(individual_records)

            present_count = sum(
                1 for r in individual_records
                if r["Status"].lower() == "present"
            )

            individual_percentage = (
                present_count / total * 100
                if total else 0
            )

            st.subheader(
                f'Report: {selected_student["Name"]}'
            )

            st.metric(
                "Attendance Percentage",
                f"{individual_percentage:.1f}%"
            )

            st.progress(int(individual_percentage))

            if individual_records:

                st.dataframe(
                    individual_records[::-1],
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No attendance records for this student.")

            csv_output = io.StringIO()

            writer = csv.DictWriter(
                csv_output,
                fieldnames=list(report_data[0].keys())
            )

            writer.writeheader()
            writer.writerows(report_data)

            st.download_button(
                "⬇ Download Student Reports",
                data=csv_output.getvalue(),
                file_name="student_reports.csv",
                mime="text/csv"
            )

        else:

            st.info("Add students to generate reports.")


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if st.session_state.logged_in:

    main_application()

else:

    login_page()

