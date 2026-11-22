# VitalPulse - Authenticated Health & Wellness Dashboard (01AI0302)

## Features
- **Secure Login & Registration System:** Uses SHA-256 password hashing (`hashlib`) and Streamlit `session_state`.
- **Demo Account Included:** Username `student` | Password `1234`
- **Multi-User Data Isolation:** Each registered user sees only their own health records.
- **Modern Dark Glassmorphism UI:** Custom CSS cards, 5 KPI metrics, Wellness Score (/100), Smart Health Advisor, and interactive charts.
- **One-Click Viva Demo Data:** Load 7 days of sample records instantly from the sidebar.

## Run Locally
```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy Online (Streamlit Community Cloud)
1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Go to https://share.streamlit.io/, select your repository, and click **Deploy**.
