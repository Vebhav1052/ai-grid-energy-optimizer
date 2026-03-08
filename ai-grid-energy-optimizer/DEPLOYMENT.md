# 🚀 Deployment Guide: AI Grid Energy Optimizer

This guide provides step-by-step instructions to deploy your project to production.

## 📋 Prerequisites
- A GitHub account with your code pushed to a repository.
- A Streamlit Cloud account (for the main dashboard).
- A Heroku or Render account (optional, for the Flask API).

---

## 🏗️ Option 1: Streamlit Cloud (Recommended for Dashboard)
Streamlit Cloud is the easiest way to deploy the main interactive dashboard.

1.  **Push your code to GitHub.**
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Click **"New app"**.
4.  Select your repository, branch, and set the main file path to `app.py`.
5.  Click **"Deploy!"**.

> **Note:** The "Execute Energy Plan" feature in the dashboard requires the Flask API to be running. If you only deploy the Streamlit app, this specific feature will look for the API at `localhost:5000` unless you set the `API_BASE_URL` environment variable.

---

## 🏗️ Option 2: Heroku (For Flask API & Dashboard)
You can deploy both components to Heroku using the provided `Procfile`.

1.  **Install Heroku CLI** and log in: `heroku login`.
2.  **Create a new Heroku app**: `heroku create ai-grid-optimizer`.
3.  **Add buildpacks**:
    ```bash
    heroku buildpacks:add heroku/python
    ```
4.  **Deploy your code**: `git push heroku main`.
5.  **Set Environment Variables**:
    If you deploy the API to a different URL (e.g., `https://my-api.herokuapp.com`), set it in the Streamlit app settings:
    ```bash
    heroku config:set API_BASE_URL=https://my-api.herokuapp.com
    ```

---

## 🏗️ Option 3: Local Production Mode
If you want to run the project in a "production-like" environment on your own machine:

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Start the API Server (Production Mode)**:
    ```bash
    gunicorn api_server:app --bind 0.0.0.0:5000
    ```
3.  **Start the Streamlit Dashboard**:
    ```bash
    streamlit run app.py
    ```

---

## 🔐 Environment Variables
The following environment variables can be configured:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `PORT` | The port the Flask API or Streamlit app will listen on. | `5000` (API) / `8501` (Streamlit) |
| `API_BASE_URL` | The URL where the Flask API is hosted (used by Streamlit). | `http://localhost:5000` |
| `REACT_APP_API_BASE_URL` | The URL where the Flask API is hosted (used by React). | `http://localhost:5000/api` |

---

## ✅ Deployment Checklist
- [ ] Models are trained (`demand_model.pkl`, `solar_model.pkl` in `models/` folder).
- [ ] `requirements.txt` is up-to-date.
- [ ] `Procfile` and `runtime.txt` are present in the root.
- [ ] Environment variables are correctly set in the deployment platform.
