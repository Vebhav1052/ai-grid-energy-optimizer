# 🚀 Deployment Guide - AI Grid Energy Optimizer

## Pre-Deployment Checklist

- [ ] All tests passing (`python test_features.py` → 100%)
- [ ] Weather API integration working
- [ ] No Python syntax errors
- [ ] `requirements.txt` updated with all dependencies
- [ ] Streamlit app launches without errors

---

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended for Hackathon)

**Easiest option - Free and quick!**

#### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "AI Grid Energy Optimizer - Production Ready"
git remote add origin https://github.com/YOUR_USERNAME/ai-grid-energy-optimizer.git
git branch -M main
git push -u origin main
```

#### Step 2: Connect to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Choose main branch and specify `app.py`
5. Click "Deploy"

#### Step 3: Configure Secrets (Optional - for OpenWeatherMap)
In Streamlit Cloud settings, add:
```toml
[secrets]
OPENWEATHER_API_KEY = "your_api_key_here"
```

**Setup Time:** ~5 minutes  
**Cost:** Free  
**URL Format:** `https://share.streamlit.io/username/repo-name`

---

### Option 2: Heroku Cloud Platform

#### Step 1: Create Heroku App
```bash
heroku login
heroku create your-grid-optimizer
```

#### Step 2: Create `Procfile`
```
web: streamlit run --server.port=$PORT app.py
```

#### Step 3: Create `setup.sh`
```bash
mkdir -p ~/.streamlit/
echo "[theme]
primaryColor = '#FF6B6B'
backgroundColor = '#1a1a1a'
secondaryBackgroundColor = '#262626'
textColor = '#FFFFFF'
font = 'sans serif'

[client]
showErrorDetails = false

[server]
headless = true
port = $PORT
enableXsrfProtection = false
" > ~/.streamlit/config.toml
```

#### Step 4: Deploy
```bash
git push heroku main
```

**Setup Time:** ~10 minutes  
**Cost:** Free tier available (5 active apps)  
**URL:** `https://your-grid-optimizer.herokuapp.com`

---

### Option 3: Docker Containerization

#### Step 1: Create `Dockerfile`
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 2: Create `.dockerignore`
```
.git
.gitignore
__pycache__
*.pyc
.pytest_cache
.streamlit/
.venv
venv
```

#### Step 3: Build and Run
```bash
# Build image
docker build -t ai-grid-optimizer:latest .

# Run container
docker run -p 8501:8501 ai-grid-optimizer:latest

# Push to Docker Hub
docker tag ai-grid-optimizer:latest your-hub-username/ai-grid-optimizer:latest
docker push your-hub-username/ai-grid-optimizer:latest
```

**Setup Time:** ~15 minutes  
**Best for:** Multiple environments, CI/CD pipelines

---

### Option 4: AWS Deployment

#### Using AWS Elastic Beanstalk

**Step 1: Install EB CLI**
```bash
pip install awsebcli
```

**Step 2: Initialize EB Application**
```bash
eb init -p python-3.9 ai-grid-optimizer --region us-east-1
```

**Step 3: Create `.ebextensions/python.config`**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current:$PYTHONPATH
```

**Step 4: Deploy**
```bash
eb create production-env
eb deploy
```

**Setup Time:** ~20 minutes  
**Cost:** Free tier available (12 months)

---

### Option 5: Local Server Setup (Development)

#### For Development/Testing

```bash
# Terminal 1: Run Streamlit app
streamlit run app.py

# Terminal 2: Run API server (if needed)
python api_server.py
```

**Access:** `http://localhost:8501`  
**Use Case:** Development, testing before deployment

---

## 📋 Deployment Checklist

### Before Any Deployment

- [ ] Update `requirements.txt` with exact versions
  ```bash
  pip freeze > requirements.txt
  ```

- [ ] Test locally one final time
  ```bash
  streamlit run app.py
  ```

- [ ] Verify weather API works
  ```bash
  python weather_utils.py
  ```

- [ ] Run all tests
  ```bash
  python test_features.py
  python test_weather_integration.py
  ```

### Environment Setup

- [ ] Set Python version to 3.9 or higher
- [ ] Configure secret keys if needed
- [ ] Set timeout for API calls (recommended: 10 seconds)
- [ ] Enable error logging

### Performance Optimization

- [ ] Add `@st.cache_data` decorators for expensive operations
- [ ] Cache weather API calls (5-minute TTL recommended)
- [ ] Minimize model reloading
- [ ] Optimize Plotly figures for web

---

## 🔐 Security Best Practices

### 1. Environment Variables
```python
import os

# Load from environment, not hardcoded
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
```

### 2. Input Validation
```python
# Already implemented in weather_utils.py
def validate_weather_data(weather_data):
    """Validates all required fields and data types."""
    if not weather_data:
        return False
    
    required = ['temperature', 'humidity', 'cloud_cover']
    return all(field in weather_data for field in required)
```

### 3. HTTPS Only
- Streamlit Cloud: Automatically HTTPS ✅
- Heroku: Enable SSL/TLS
- Docker: Place behind reverse proxy (nginx)

### 4. Rate Limiting
```python
# Add to weather_utils.py if needed
from functools import lru_cache
import time

CACHE_TIMEOUT = 300  # 5 minutes

@lru_cache(maxsize=32)
def get_weather_data(city: str):
    """Cached weather data to prevent API abuse."""
    # Implementation remains the same
```

---

## 📊 Monitoring & Logging

### Streamlit Cloud Logs
```bash
streamlit run app.py --logger.level=info
```

### Local Logging Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

---

## 🚨 Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError" | Run `pip install -r requirements.txt` |
| Weather API timeout | Increase timeout in `weather_utils.py` to 15 seconds |
| Port already in use | Use different port: `streamlit run app.py --server.port 8502` |
| Memory issues | Enable caching and optimize data structures |
| Slow performance | Enable Streamlit cache: `@st.cache_data` |

---

## 📈 Performance Metrics

**Target Performance:**
- Page load time: < 3 seconds
- Weather API response: < 1 second
- Dashboard rendering: < 2 seconds
- Model prediction: < 1 second

**Current Performance:**
- ✅ All metrics achieved in testing
- ✅ Smooth user experience
- ✅ No memory leaks detected

---

## 🎯 Recommended Deployment Path for Hackathon

### Quick Deploy (15 minutes)
```bash
# 1. Push to GitHub
git push origin main

# 2. Deploy on Streamlit Cloud
# Go to share.streamlit.io and connect repository
# App will be live in 2-3 minutes

# 3. Share URL with judges
# Example: https://share.streamlit.io/username/ai-grid-energy-optimizer
```

### Production Deploy (After Hackathon)
```bash
# 1. Containerize with Docker
docker build -t ai-grid-optimizer .

# 2. Deploy to AWS/Heroku/Azure
# Use cloud provider's native deployment

# 3. Set up monitoring and logging
# Configure alerts for errors
```

---

## 🔄 Continuous Deployment (Optional)

### GitHub Actions Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test
        run: |
          pip install -r requirements.txt
          python test_features.py
          python test_weather_integration.py
      - name: Deploy
        run: streamlit run app.py
```

---

## 📞 Support

For deployment help:
1. Check [Streamlit Docs](https://docs.streamlit.io/knowledge-base/deploy)
2. Review Heroku deployment guide
3. Check Docker documentation
4. Review cloud provider docs (AWS/Azure/GCP)

---

## ✅ Final Verification

After deployment, verify:
- [ ] App loads without errors
- [ ] Dashboard displays all features
- [ ] Weather API works
- [ ] Temperature conversions work
- [ ] Peak demand calculates
- [ ] No console errors
- [ ] Response time acceptable

**You're ready to deploy! 🚀**
