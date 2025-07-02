## 🐍 FastAPI Backend

# Introduction
A cost-effective, flexible VM provisioning solution built on a bidding-based model, designed for private cloud scalability. Offers raw VM access with volumes, security, and SSH controls—perfect for enterprises, developers, and internal cloud teams.

# ⚙️ VM on Spot Platform - FastAPI Backend

This is the backend service for VM provisioning, built with FastAPI.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.9+
- pip (Python package installer)
- Rackspace OSPC credentials ( username and password ) to Staging tenant

### 2. Clone Repo, check Python Version and create virtual environments
```bash
git clone <repo>
cd vm-allocater

python3 --version
pip3 --version

python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Installing requirements
```bash
pip3 install -r requirements.txt
```

### 4. Step to Run Application
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
OR
python3 app.py
```



