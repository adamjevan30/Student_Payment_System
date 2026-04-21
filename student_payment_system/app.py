import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from db import init_db, insert_student, get_students, update_status, delete_student
from email_service import send_email

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Pro Student Payment System", layout="wide")
init_db()

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# =========================
# ADMIN LOGIN
# =========================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def login():
    st.title("🔐 Admin Login")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == ADMIN_USER and pw == ADMIN_PASS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

def logout():
    st.session_state.logged_in = False
    st.rerun()

# =========================
# AUTH CHECK
# =========================
if not st.session_state.logged_in:
    login()
    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📌 Admin Panel")

pages = ["Dashboard", "Add Student", "Upload CSV", "Quick Actions"]

for p in pages:
    if st.sidebar.button(p):
        st.session_state.page = p

st.sidebar.markdown("---")
st.sidebar.button("🚪 Logout", on_click=logout)

page = st.session_state.page

# =========================
# LOAD DATA
# =========================
students = get_students()

df = pd.DataFrame(
    students,
    columns=["ID", "Name", "Email", "Amount", "Status", "Notified"]
) if students else pd.DataFrame()

# =========================
# DASHBOARD STYLE
# =========================
st.markdown("""
<style>
.card {
    background:#111827;
    padding:18px;
    border-radius:12px;
    color:white;
    text-align:center;
}
.title {font-size:16px;}
.value {font-size:26px;color:#00C2FF;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 📊 DASHBOARD (PRO VERSION + CHARTS)
# =========================================================
if page == "Dashboard":

    st.title("📊 PRO ADMIN DASHBOARD")

    if df.empty:
        st.info("No students yet.")

    else:

        paid_df = df[df["Status"] == "paid"]
        unpaid_df = df[df["Status"] == "unpaid"]

        # ================= CARDS =================
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card'><div class='title'>Total</div><div class='value'>{len(df)}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><div class='title'>Paid</div><div class='value'>{len(paid_df)}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><div class='title'>Unpaid</div><div class='value'>{len(unpaid_df)}</div></div>", unsafe_allow_html=True)

        st.divider()

        # ================= CHARTS =================
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Payment Status Chart")

            fig, ax = plt.subplots()
            ax.bar(["Paid", "Unpaid"], [len(paid_df), len(unpaid_df)])
            ax.set_ylabel("Students")
            st.pyplot(fig)

        with col2:
            st.subheader("🥧 Distribution")

            fig2, ax2 = plt.subplots()
            ax2.pie(
                [len(paid_df), len(unpaid_df)],
                labels=["Paid", "Unpaid"],
                autopct="%1.1f%%"
            )
            st.pyplot(fig2)

        st.divider()

        # ================= CLEAN TABLE =================
        def table(data, title, color):

            st.subheader(title)

            if data.empty:
                st.info("No data.")
                return

            data = data.copy().reset_index(drop=True)
            data.insert(0, "No", range(1, len(data) + 1))

            for _, row in data.iterrows():

                col1, col2, col3, col4, col5 = st.columns([1,3,3,2,2])

                col1.write(row["No"])
                col2.write(row["Name"])
                col3.write(row["Email"])
                col4.write(f"₱ {row['Amount']}")
                col5.write(f"{color} {row['Status'].upper()}")

                if col5.button("❌ Remove", key=f"del_{title}_{row['ID']}"):
                    delete_student(row["ID"])
                    st.rerun()

        table(paid_df, "🟢 Paid Students", "🟢")
        table(unpaid_df, "🔴 Unpaid Students", "🔴")

# =========================================================
# ➕ ADD STUDENT
# =========================================================
elif page == "Add Student":

    st.title("➕ Add Student")

    with st.form("form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        amount = st.number_input("Amount", min_value=0.0)
        status = st.selectbox("Status", ["paid", "unpaid"])

        if st.form_submit_button("Save"):
            insert_student(name, email, amount, status)
            st.success("Added!")
            st.rerun()

# =========================================================
# 📂 UPLOAD CSV
# =========================================================
elif page == "Upload CSV":

    st.title("📂 Upload Students")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        upload_df = pd.read_csv(file)
        st.dataframe(upload_df)

        if st.button("Save"):
            for _, row in upload_df.iterrows():
                insert_student(
                    row.get("Name"),
                    row.get("Email"),
                    row.get("Amount", 0),
                    row.get("Status", "unpaid")
                )
            st.success("Uploaded!")
            st.rerun()

# =========================================================
# ⚡ QUICK ACTIONS
# =========================================================
elif page == "Quick Actions":

    st.title("⚡ Quick Actions")

    if df.empty:
        st.info("No students.")

    else:

        edit_df = df.copy()
        edit_df["New Status"] = edit_df["Status"]

        edited = st.data_editor(
            edit_df[["ID", "Name", "Email", "Amount", "New Status"]],
            column_config={
                "New Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["paid", "unpaid"]
                )
            },
            use_container_width=True,
            disabled=["ID"]
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Update"):
                for _, row in edited.iterrows():
                    update_status(row["ID"], row["New Status"])
                st.success("Updated!")
                st.rerun()

        with col2:
            if st.button("📧 Send Emails"):

                for _, row in edited.iterrows():

                    if row["New Status"] == "paid":
                        send_email(
                            row["Email"],
                            "Payment Receipt",
                            f"Hi {row['Name']}, your payment is CONFIRMED PAID."
                        )
                    else:
                        send_email(
                            row["Email"],
                            "Payment Reminder",
                            f"Hi {row['Name']}, please settle your payment."
                        )

                st.success("Emails sent!")
                st.rerun()