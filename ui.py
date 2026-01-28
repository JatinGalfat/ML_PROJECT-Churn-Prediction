import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Customer Churn Predictor", page_icon="📊")

st.title("📊 Customer Churn Prediction System")

# -------------------------
# Session state
# -------------------------
if "token" not in st.session_state:
    st.session_state.token = None

# -------------------------
# Auth Section
# -------------------------
st.sidebar.header("🔐 Authentication")

auth_choice = st.sidebar.radio("Choose action", ["Login", "Register"])

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button(auth_choice):
    endpoint = "/login" if auth_choice == "Login" else "/register"

    payload = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload)

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.sidebar.success(f"{auth_choice} successful ✅")
        else:
            st.sidebar.error(response.json().get("detail", "Authentication failed"))
    except Exception as e:
        st.sidebar.error(str(e))

# -------------------------
# Prediction Section
# -------------------------
st.header("🧮 Predict Customer Churn")

if not st.session_state.token:
    st.warning("Please login to access prediction 🔒")
    st.stop()

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        Gender = st.selectbox("Gender", ["Male", "Female"])
        Age = st.number_input("Age", min_value=18, max_value=100, value=30)
        Tenure = st.number_input("Tenure", min_value=0, max_value=100, value=12)
        Services_Subscribed = st.number_input("Services Subscribed", 0, 10, 3)
        Contract_Type = st.selectbox(
            "Contract Type",
            ["Month-to-month", "One year", "Two year"]
        )

    with col2:
        MonthlyCharges = st.number_input("Monthly Charges", min_value=0.0, value=70.5)
        TotalCharges = st.number_input("Total Charges", min_value=0.0, value=500.0)
        TechSupport = st.selectbox("Tech Support", ["Yes", "No"])
        OnlineSecurity = st.selectbox("Online Security", ["Yes", "No"])
        InternetService = st.selectbox(
            "Internet Service",
            ["DSL", "Fiber optic", "No"]
        )

    submit = st.form_submit_button("🚀 Predict")

if submit:
    payload = {
        "customer": {
            "Gender": Gender,
            "Age": Age,
            "Tenure": Tenure,
            "Services_Subscribed": Services_Subscribed,
            "Contract_Type": Contract_Type,
            "MonthlyCharges": MonthlyCharges,
            "TotalCharges": TotalCharges,
            "TechSupport": TechSupport,
            "OnlineSecurity": OnlineSecurity,
            "InternetService": InternetService
        }
    }

    headers = {
        "Authorization": f"Bearer {st.session_state.token}"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/predict/auth",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()

            st.success("Prediction Successful 🎯")
            st.metric("Churn Label", result["churn_label"])
            st.metric("Churn Prediction", result["churn_prediction"])
            if result["churn_probability"] is not None:
                st.metric(
                    "Churn Probability",
                    f"{result['churn_probability']:.2%}"
                )
        else:
            st.error(response.json().get("detail", "Prediction failed"))

    except Exception as e:
        st.error(str(e))
