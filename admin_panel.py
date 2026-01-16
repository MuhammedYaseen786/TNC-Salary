import streamlit as st
from supabase import create_client
from datetime import date

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_CODE = st.secrets["ADMIN_ACCESS_CODE"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------- SECURITY ----------
def admin_auth():
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        code = st.text_input("Enter Admin Access Code", type="password")
        if st.button("Login"):
            if code == ADMIN_CODE:
                st.session_state.admin_auth = True
                st.success("Access granted ✅")
                st.rerun()
            else:
                st.error("Invalid access code ❌")
        st.stop()


# ---------- HELPERS ----------
def get_employee_by_dob(dob):
    return (
        supabase.table("employees")
        .select("*")
        .eq("date_of_birth", str(dob))
        .execute()
        .data
    )



def employee_form(emp_id, defaults=None):
    defaults = defaults or {}
    k = lambda x: f"{x}_{emp_id}"  # key helper

    col1, col2 = st.columns(2)

    with col1:
        dept_name = st.text_input(
            "Department Name",
            defaults.get("dept_name", ""),
            key=k("dept_name")
        )

        shift = st.selectbox(
            "Shift",
            ["I", "SF-I", "II"],
            index=["I", "SF-I", "II"].index(defaults.get("shift", "I"))
            if defaults.get("shift") in ["I", "SF-I", "II"] else 0,
            key=k("shift")
        )

        position = st.text_input(
            "Position",
            defaults.get("position", ""),
            key=k("position")
        )

        other_post = st.text_input(
            "Other Post",
            defaults.get("other_post", ""),
            key=k("other_post")
        )

        university_approval = st.radio(
            "University Qualification Approval",
            ["Yes", "No", "In-Progress"],
            index=["Yes", "No", "In-Progress"].index(
                defaults.get("university_approval", "No")
            ),
            key=k("university_approval")
        )

    with col2:
        name = st.text_input(
            "Employee Name",
            defaults.get("name", ""),
            key=k("name")
        )

        ug_options = ["BA", "BSC", "BCA", "B.COM", "NA"]
        pg_options = ["MA", "MSC", "MCA", "M.COM", "M.PHIL", "NET", "CET", "NA"]

        ug_qualification = st.selectbox(
            "UG Qualification",
            ug_options,
            index=ug_options.index(defaults.get("qualification"))
            if defaults.get("qualification") in ug_options else ug_options.index("NA"),
            key=k("ug_qualification")
        )

        pg_qualification = st.selectbox(
            "PG Qualification",
            pg_options,
            index=pg_options.index(defaults.get("qualification"))
            if defaults.get("qualification") in pg_options else pg_options.index("NA"),
            key=k("pg_qualification")
        )

        if ug_qualification != "NA" and pg_qualification != "NA":
            st.error("Either UG or PG must be NA")
            st.stop()

        qualification = (
            ug_qualification if ug_qualification != "NA"
            else pg_qualification if pg_qualification != "NA"
            else ""
        )

        date_of_birth = st.date_input(
            "Date of Birth",
            date.fromisoformat(defaults["date_of_birth"])
            if defaults.get("date_of_birth") else date.today(),
            key=k("dob")
        )

        date_of_appoint = st.date_input(
            "Date of Appointment",
            date.fromisoformat(defaults["date_of_appoint"])
            if defaults.get("date_of_appoint") else date.today(),
            key=k("doa")
        )

        date_of_join = st.date_input(
            "Date of Join",
            date.fromisoformat(defaults["date_of_join"])
            if defaults.get("date_of_join") else date.today(),
            key=k("doj")
        )

    st.subheader("Contact / Government Details")

    col3, col4 = st.columns(2)

    with col3:
        uan_pf = st.text_input("UAN / PF", defaults.get("uan_pf", ""), key=k("uan_pf"))
        aadhar_num = st.text_input("Aadhar Number", defaults.get("aadhar_num", ""), key=k("aadhar"))
        pan_num = st.text_input("PAN Number", defaults.get("pan_num", ""), key=k("pan"))

    with col4:
        mobile_num = st.text_input("Mobile Number", defaults.get("mobile_num", ""), key=k("mobile"))
        email_id = st.text_input("Email ID", defaults.get("email_id", ""), key=k("email"))

    return {
        "dept_name": dept_name,
        "shift": shift,
        "position": position,
        "other_post": other_post,
        "university_approval": university_approval,
        "name": name,
        "qualification": qualification,
        "date_of_birth": str(date_of_birth),
        "date_of_appoint": str(date_of_appoint),
        "date_of_join": str(date_of_join),
        "uan_pf": uan_pf,
        "aadhar_num": aadhar_num,
        "pan_num": pan_num,
        "mobile_num": mobile_num,
        "email_id": email_id,
    }


# ---------- PAGE ----------
def admin_panel_page():
    admin_auth()
    st.title("⚙️ Admin Panel")

    tab1, tab2, tab3 = st.tabs(["➕ Add", "✏️ Edit", "🗑️ Delete"])

    # ---------------- ADD ----------------
    with tab1:
        # Use a constant unique ID for ADD form
        data = employee_form(emp_id="add")

        if st.button("Add Employee", key="add_btn"):
            supabase.table("employees").insert(data).execute()
            st.success("Employee added 🎉")

    # ---------------- EDIT ----------------
    with tab2:
        dob = st.date_input("Date of Birth to Edit", key="edit_dob")
        emp = get_employee_by_dob(dob)

        if emp:
            emp_data = emp[0]

            # Use DOB or employee ID as unique key
            updated_data = employee_form(
                emp_id=f"edit_{emp_data['date_of_birth']}",
                defaults=emp_data
            )

            if st.button("Update Employee", key="update_btn"):
                supabase.table("employees") \
                    .update(updated_data) \
                    .eq("date_of_birth", str(dob)) \
                    .execute()
                st.success("Employee updated ✅")

    # ---------------- DELETE ----------------
    with tab3:
        dob = st.date_input("Date of Birth to Delete", key="delete_dob")
        emp = get_employee_by_dob(dob)

        if emp:
            st.error(f"Delete **{emp[0]['name']}**?")
            if st.checkbox("Confirm delete", key="confirm_delete") and st.button("Delete", key="delete_btn"):
                supabase.table("employees") \
                    .delete() \
                    .eq("date_of_birth", str(dob)) \
                    .execute()
                st.success("Employee deleted 🗑️")
