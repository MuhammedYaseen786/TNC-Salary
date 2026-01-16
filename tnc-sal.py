import streamlit as st
from user_panel import view_employee_page
from admin_panel import admin_panel_page

st.set_page_config(
    page_title="Employee Management",
    layout="wide",
    page_icon="tnc-logo-1.png"
)

pg = st.navigation([
    st.Page(view_employee_page, title="View Employee", icon="🔍"),
    st.Page(admin_panel_page, title="Admin Panel", icon="⚙️"),
])

pg.run()
