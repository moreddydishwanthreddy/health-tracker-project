import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import date, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="VitalPulse | Personal Health & Wellness",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

USERS_FILE = "users.csv"
DATA_FILE = "health_data.csv"
WATER_GOAL = 2.5       # Liters
CALORIE_LIMIT = 2200   # kcal
SLEEP_GOAL = 7.5       # Hours

# --- Custom CSS for Modern UI ---
st.markdown("""
<style>
    /* Main background & typography */
    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #111827 100%);
        color: #f8fafc;
    }
    /* Styled Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 16px 20px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    /* Login Card Container */
    .login-banner {
        background: linear-gradient(120deg, #0284c7, #0d9488);
        padding: 28px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px rgba(2, 132, 199, 0.3);
    }
    .insight-card {
        background: rgba(15, 23, 42, 0.9);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions: Authentication ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_users():
    if not os.path.exists(USERS_FILE):
        default_users = pd.DataFrame([
            {
                "username": "student",
                "full_name": "CSE Student (Demo)",
                "password": hash_password("1234")
            }
        ])
        default_users.to_csv(USERS_FILE, index=False)


def verify_user(username, password):
    init_users()
    users_df = pd.read_csv(USERS_FILE)
    user_row = users_df[users_df["username"].str.lower() == username.strip().lower()]
    if not user_row.empty:
        if user_row.iloc[0]["password"] == hash_password(password):
            return user_row.iloc[0]["full_name"], user_row.iloc[0]["username"]
    return None, None


def register_user(full_name, username, password):
    init_users()
    users_df = pd.read_csv(USERS_FILE)
    if username.strip().lower() in users_df["username"].str.lower().values:
        return False, "Username already exists. Choose another one."
    new_user = pd.DataFrame([{
        "username": username.strip(),
        "full_name": full_name.strip(),
        "password": hash_password(password)
    }])
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv(USERS_FILE, index=False)
    return True, "Account created! You can now log in."


# --- Helper Functions: Health Data ---
def load_all_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "Username", "Date", "Weight (kg)", "Height (cm)", "BMI",
        "Category", "Calories (kcal)", "Water (L)", "Sleep (hrs)",
        "Wellness Score", "Goal Status"
    ])


def save_all_data(df):
    df.to_csv(DATA_FILE, index=False)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25.0:
        return "Normal Weight"
    elif 25.0 <= bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def calculate_wellness_score(bmi, water, calories, sleep):
    score = 0
    # BMI component (30 pts)
    if 18.5 <= bmi < 25.0:
        score += 30
    elif 17.0 <= bmi < 28.0:
        score += 20
    else:
        score += 10

    # Water component (25 pts)
    score += min(25, int((water / WATER_GOAL) * 25))

    # Calorie component (25 pts)
    if 1500 <= calories <= CALORIE_LIMIT:
        score += 25
    elif calories <= CALORIE_LIMIT + 300:
        score += 15
    else:
        score += 8

    # Sleep component (20 pts)
    score += min(20, int((sleep / SLEEP_GOAL) * 20))
    return min(100, score)


def load_demo_records(username):
    today = date.today()
    sample_rows = []
    weights = [69.5, 69.2, 69.0, 68.8, 68.5, 68.3, 68.0]
    cals = [2150, 2300, 1980, 2050, 2100, 1950, 2020]
    waters = [2.1, 2.4, 2.6, 2.8, 2.5, 3.0, 2.7]
    sleeps = [6.5, 7.0, 7.5, 8.0, 7.2, 7.8, 7.5]

    for i in range(7):
        d = str(today - timedelta(days=6 - i))
        w = weights[i]
        h = 175.0
        bmi = round(w / ((h / 100) ** 2), 2)
        cat = get_bmi_category(bmi)
        score = calculate_wellness_score(bmi, waters[i], cals[i], sleeps[i])
        status = "Goals Met" if (waters[i] >= WATER_GOAL and cals[i] <= CALORIE_LIMIT) else "Needs Focus"
        sample_rows.append({
            "Username": username,
            "Date": d,
            "Weight (kg)": w,
            "Height (cm)": h,
            "BMI": bmi,
            "Category": cat,
            "Calories (kcal)": cals[i],
            "Water (L)": waters[i],
            "Sleep (hrs)": sleeps[i],
            "Wellness Score": score,
            "Goal Status": status
        })

    all_df = load_all_data()
    all_df = all_df[all_df["Username"] != username]
    all_df = pd.concat([all_df, pd.DataFrame(sample_rows)], ignore_index=True)
    save_all_data(all_df)


# --- Session State Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.full_name = ""


# =========================================================
# 1. LOGIN & REGISTRATION SCREEN
# =========================================================
def show_login_page():
    col_left, col_mid, col_right = st.columns([1, 1.4, 1])

    with col_mid:
        st.markdown("""
        <div class="login-banner">
            <h1 style="margin:0; font-size: 2rem;">🩺 VitalPulse Health Portal</h1>
            <p style="margin:6px 0 0 0; opacity: 0.92;">Smart BMI, Hydration & Wellness Analytics Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter username (Demo: student)")
                password = st.text_input("Password", type="password", placeholder="Enter password (Demo: 1234)")
                submit_login = st.form_submit_button("Login to Dashboard", use_container_width=True)

                if submit_login:
                    full_name, valid_user = verify_user(username, password)
                    if valid_user:
                        st.session_state.logged_in = True
                        st.session_state.username = valid_user
                        st.session_state.full_name = full_name
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Try demo login: `student` / `1234`.")

            st.info("💡 **Quick Viva Login:** Username `student` | Password `1234`")

        with tab_register:
            with st.form("register_form"):
                new_name = st.text_input("Full Name", placeholder="e.g., Aarav Patel")
                new_user = st.text_input("Choose Username", placeholder="e.g., aarav01")
                new_pass = st.text_input("Choose Password", type="password")
                submit_reg = st.form_submit_button("Register Account", use_container_width=True)

                if submit_reg:
                    if not new_name.strip() or not new_user.strip() or not new_pass.strip():
                        st.warning("All fields are required.")
                    else:
                        ok, msg = register_user(new_name, new_user, new_pass)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)


# =========================================================
# 2. MAIN HEALTH DASHBOARD (AUTHENTICATED)
# =========================================================
def show_dashboard():
    username = st.session_state.username
    full_name = st.session_state.full_name

    # --- Top Navigation Header ---
    head_c1, head_c2 = st.columns([4, 1])
    with head_c1:
        st.title(f"🩺 Welcome back, {full_name}")
        st.caption("Personal Health, BMI & Daily Wellness Analytics | Subject: 01AI0302")
    with head_c2:
        st.write("")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.full_name = ""
            st.rerun()

    st.divider()

    # --- Sidebar: Log Entry & Demo Controls ---
    st.sidebar.header("➕ Log Daily Health")
    with st.sidebar.form("entry_form", clear_on_submit=True):
        log_date = st.date_input("Date", value=date.today())
        weight = st.number_input("Weight (kg)", min_value=25.0, max_value=250.0, value=68.0, step=0.5)
        height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=230.0, value=175.0, step=1.0)
        calories = st.number_input("Calories (kcal)", min_value=0, max_value=6000, value=2000, step=50)
        water = st.number_input("Water Intake (L)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
        sleep = st.number_input("Sleep Duration (hrs)", min_value=0.0, max_value=16.0, value=7.5, step=0.5)

        saved = st.form_submit_button("Calculate & Save Entry", use_container_width=True)

        if saved:
            bmi = round(weight / ((height_cm / 100) ** 2), 2)
            category = get_bmi_category(bmi)
            score = calculate_wellness_score(bmi, water, calories, sleep)
            status = "Goals Met" if (water >= WATER_GOAL and calories <= CALORIE_LIMIT) else "Needs Focus"

            new_row = pd.DataFrame([{
                "Username": username,
                "Date": str(log_date),
                "Weight (kg)": weight,
                "Height (cm)": height_cm,
                "BMI": bmi,
                "Category": category,
                "Calories (kcal)": calories,
                "Water (L)": water,
                "Sleep (hrs)": sleep,
                "Wellness Score": score,
                "Goal Status": status
            }])

            all_df = load_all_data()
            all_df = pd.concat([all_df, new_row], ignore_index=True)
            save_all_data(all_df)
            st.sidebar.success(f"Logged! BMI: {bmi} ({category})")

    st.sidebar.divider()
    st.sidebar.subheader("⚡ Quick Viva Controls")
    if st.sidebar.button("📊 Load 7-Day Demo Data", use_container_width=True):
        load_demo_records(username)
        st.rerun()

    # Load current user's records
    all_df = load_all_data()
    user_df = all_df[all_df["Username"] == username].copy()

    # --- Dashboard Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 Analytics Overview", "📋 Health History & Export", "📘 Algorithm & Viva Guide"])

    with tab1:
        if user_df.empty:
            st.info("Your dashboard is currently empty. Add an entry on the **left sidebar** or click **Load 7-Day Demo Data** for an instant preview!")
        else:
            latest = user_df.iloc[-1]

            # 5 High-Contrast KPI Cards
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Latest BMI", f"{latest['BMI']}", latest["Category"])
            k2.metric("Wellness Score", f"{int(latest['Wellness Score'])}/100", "Daily Rating")
            k3.metric("Avg Water", f"{user_df['Water (L)'].mean():.2f} L", f"Goal: {WATER_GOAL} L")
            k4.metric("Avg Calories", f"{int(user_df['Calories (kcal)'].mean())} kcal", f"Limit: {CALORIE_LIMIT}")
            k5.metric("Avg Sleep", f"{user_df['Sleep (hrs)'].mean():.1f} hrs", f"Goal: {SLEEP_GOAL} hrs")

            st.write("")

            # Smart Health Advisor Section
            st.subheader("🤖 Smart Health Advisor")
            avg_water = user_df["Water (L)"].mean()
            avg_cal = user_df["Calories (kcal)"].mean()
            avg_sleep = user_df["Sleep (hrs)"].mean()

            adv_c1, adv_c2 = st.columns(2)
            with adv_c1:
                if avg_water >= WATER_GOAL:
                    st.markdown('<div class="insight-card">💧 <b>Hydration On Track:</b> You are consistently meeting the 2.5 L daily water target.</div>', unsafe_allow_html=True)
                else:
                    gap = round(WATER_GOAL - avg_water, 2)
                    st.markdown(f'<div class="insight-card">💧 <b>Hydration Alert:</b> You are averaging <b>{gap} L below</b> your daily goal. Drink 2 extra glasses of water daily.</div>', unsafe_allow_html=True)

            with adv_c2:
                if avg_cal <= CALORIE_LIMIT and avg_sleep >= 7.0:
                    st.markdown('<div class="insight-card">⚡ <b>Balanced Routine:</b> Your calorie intake and sleep recovery are well-balanced.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="insight-card">⚡ <b>Lifestyle Tip:</b> Keep daily intake under 2200 kcal and aim for 7.5+ hours of sleep for optimal recovery.</div>', unsafe_allow_html=True)

            st.divider()

            # Charts Section
            c1, c2 = st.columns(2)
            chart_df = user_df.set_index("Date")

            with c1:
                st.subheader("📈 Weight (kg) & BMI Progression")
                st.line_chart(chart_df[["Weight (kg)", "BMI"]])

            with c2:
                st.subheader("💧 Hydration (L) vs Sleep (hrs)")
                st.bar_chart(chart_df[["Water (L)", "Sleep (hrs)"]])

    with tab2:
        if user_df.empty:
            st.warning("No records logged yet.")
        else:
            st.subheader("Complete User Health Log")
            display_df = user_df.drop(columns=["Username"]).iloc[::-1]
            st.dataframe(display_df, use_container_width=True)

            dl_col, rst_col = st.columns([1, 1])
            with dl_col:
                csv_data = display_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download My Report (CSV)",
                    data=csv_data,
                    file_name=f"{username}_health_report.csv",
                    mime="text/csv"
                )
            with rst_col:
                if st.button("🗑️ Clear My Records"):
                    remaining = all_df[all_df["Username"] != username]
                    save_all_data(remaining)
                    st.rerun()

    with tab3:
        st.subheader("📘 Semester 3 Project Documentation (01AI0302)")
        st.markdown("""
        **1. Problem Statement:**  
        Students and everyday users need a secure, multi-user health dashboard to monitor Body Mass Index (BMI), hydration, calorie balance, and sleep quality with visual trend tracking.

        **2. System Architecture & Modules:**
        * **`streamlit`**: Interactive web UI, multi-tab layout, custom CSS cards, and real-time charts.
        * **`hashlib` (SHA-256)**: Encrypts user passwords securely in `users.csv` instead of storing plain text.
        * **`pandas`**: Filters user-specific records, computes rolling averages, and exports CSV reports.
        * **`st.session_state`**: Maintains active login sessions across page interactions.
        """)


# --- App Entry Point ---
init_users()
if st.session_state.logged_in:
    show_dashboard()
else:
    show_login_page()
