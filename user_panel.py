import streamlit as st
from supabase import create_client
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

# ---------------- CONFIG ----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

styles = getSampleStyleSheet()

# ---------------- DB ----------------
def get_employee_by_dob(dob):
    return (
        supabase.table("employees")
        .select("*")
        .eq("date_of_birth", str(dob))
        .execute()
        .data
    )

# ---------------- FAST PDF (IN-MEMORY) ----------------
def generate_pdf_bytes(emp):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    story = []

    story.append(Paragraph("<b>Staff Management</b>", styles["Title"]))
    story.append(Spacer(1, 10))

    def section(title, rows):
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
        story.append(Spacer(1, 6))

        table = Table(rows, colWidths=[250, 250])
        table.setStyle(TableStyle([
            ("BOX", (0,0), (-1,-1), 1, colors.grey),
            ("INNERGRID", (0,0), (-1,-1), 0.5, colors.lightgrey),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(table)

    section("Employee Information", [
        [f"Name: {emp.get('name','')}", f"Shift: {emp.get('shift','')}"],
        [f"Department: {emp.get('dept_name','')}", f"Position: {emp.get('position','')}"],
        [f"Qualification: {emp.get('qualification','')}", f"Other Post: {emp.get('other_post','')}"],
    ])

    section("Employment Dates", [
        [f"Date of Birth: {emp.get('date_of_birth','')}", f"Joining Date: {emp.get('date_of_join','')}"],
        [f"Appointment Date: {emp.get('date_of_appoint','')}", ""],
    ])

    section("Contact & Government Details", [
        [f"Mobile: {emp.get('mobile_num','')}", f"Email: {emp.get('email_id','')}"],
        [f"Aadhar: {emp.get('aadhar_num','')}", f"PAN: {emp.get('pan_num','')}"],
        [f"UAN / PF: {emp.get('uan_pf','')}", ""],
    ])

    section("University Approval", [
        [emp.get("university_approval", ""), ""]
    ])

    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------- UI ----------------
def view_employee_page():
    st.markdown("## Staff Management")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        dob = st.date_input("📅 Date of Birth", format="DD-MM-YYYY")
        search = st.button("🔎 Search", use_container_width=True)

    if not search:
        return

    data = get_employee_by_dob(dob)

    if not data:
        st.error("❌ No employee found")
        return

    emp = data[0]

    st.success(f"✅ Employee Found: **{emp['name']}**")

    # -------- DISPLAY --------
    st.markdown("##### 👤 Employee Information")
    with st.container(border=True):
        st.write("**Name:**", emp.get("name", "-"))
        st.write("**Department:**", emp.get("dept_name", "-"))
        st.write("**Qualification:**", emp.get("qualification", "-"))
        st.write("**Shift:**", emp.get("shift", "-"))
        st.write("**Position:**", emp.get("position", "-"))
        st.write("**Other Position:**", emp.get("other_post", "-"))

    st.markdown("##### 📅 Employment Dates")
    with st.container(border=True):
        st.write("**Date of Birth:**", emp.get("date_of_birth", "-"))
        st.write("**Appointment Date:**", emp.get("date_of_appoint", "-"))
        st.write("**Joining Date:**", emp.get("date_of_join", "-"))

    st.markdown("##### 📞 Contact & Government Details")
    with st.container(border=True):
        st.write("**Mobile:**", emp.get("mobile_num", "-"))
        st.write("**Email:**", emp.get("email_id", "-"))
        st.write("**Aadhar:**", emp.get("aadhar_num", "-"))
        st.write("**PAN:**", emp.get("pan_num", "-"))
        st.write("**UAN / PF:**", emp.get("uan_pf", "-"))

    st.markdown("##### ✅ University Approval")
    with st.container(border=True):
        st.write(emp.get("university_approval", "-"))

    # -------- WORKING PDF DOWNLOAD --------
    st.markdown("---")

    pdf_buffer = generate_pdf_bytes(emp)

    st.download_button(
        label="📄 Download Employee PDF",
        data=pdf_buffer,
        file_name=f"{emp['name']}_profile.pdf",
        mime="application/pdf",
        use_container_width=True
    )
