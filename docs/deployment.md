# TrustLens AI - Cloudways Deployment & Hosting Guide

**Target Platform**: Cloudways (DigitalOcean / AWS / GCP infrastructure)  
**Verification Date**: October 31, 2026  
**Status**: ARCHITECTURE VERIFIED | LIVE HOSTING BLOCKED (Awaiting Cloudways Server Credentials)

---

## 1. Hosting Architecture Overview

Cloudways provides a managed hosting environment optimized for Nginx and Apache. Because Cloudways does not feature a 1-click Python runtime, the production-grade deployment pattern uses an **Nginx Reverse Proxy** terminating at a local **ASGI Uvicorn process** managed by **Supervisor**.

```mermaid
graph LR
    User[Web Client / Browser] -- HTTPS:443 --> CloudwaysNginx[Cloudways Nginx Reverse Proxy]
    CloudwaysNginx -- Static Assets --> StaticFiles[/app/static/*]
    CloudwaysNginx -- Proxy Pass http://127.0.0.1:8000 --> Uvicorn[Uvicorn ASGI Server]
    Supervisor[Supervisor Daemon] -- Manages/Restarts --> Uvicorn
    Uvicorn --> FastAPI[TrustLens FastAPI Application]
```

### Key Architectural Strengths:
- **Zero Port Conflict**: The FastAPI/Uvicorn process binds to loopback `127.0.0.1:8000`, protected behind Cloudways' Nginx firewall.
- **Process Supervision**: Supervisor ensures automatic restart upon process failure or server reboot.
- **SSL / TLS**: Cloudways automated Let's Encrypt SSL terminates directly at Nginx.
- **Environment Isolation**: Server secrets (`GEMMA_API_KEY`, etc.) live in `/home/master/applications/trustlens/.env` on the server and are never committed to Git.

---

## 2. Step-by-Step Server Setup Guide

### Step 1: Provision Cloudways Application
1. Log into the Cloudways Console.
2. Select or launch a server (DigitalOcean 2GB+ recommended).
3. Under **Add Application**, choose **Custom PHP (PHP 8.2+)** and name it `trustlens-ai`.

### Step 2: SSH Access & Code Deployment
Connect to the server via SSH as the application master user:
```bash
ssh master_user@<CLOUDWAYS_SERVER_IP>
cd /home/master/applications/trustlens/public_html
```

Clone the repository:
```bash
git clone https://github.com/your-org/trustlens-ai.git .
```

### Step 3: Python Virtual Environment & Dependencies
Initialize Python 3.11+ virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Production Environment Variables
Create the server `.env` file (protected with `chmod 600`):
```bash
cat << 'EOF' > .env
ENVIRONMENT=production
LOG_LEVEL=info
HOST=127.0.0.1
PORT=8000
RATE_LIMIT_PER_MINUTE=30
MAX_UPLOAD_SIZE_BYTES=10485760
MAX_PDF_PAGES=10

# Google AI Studio Gemma 4 Key
GEMMA_API_KEY=your_actual_google_ai_studio_api_key
GEMMA_MODEL_ID=gemma-4-31b-it
GEMMA_API_BASE=https://generativelanguage.googleapis.com/v1beta
EOF

chmod 600 .env
```

### Step 5: Configure Process Supervision (Supervisor)
Create `/etc/supervisor/conf.d/trustlens.conf`:
```ini
[program:trustlens]
directory=/home/master/applications/trustlens/public_html
command=/home/master/applications/trustlens/public_html/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
user=master_user
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/supervisor/trustlens.err.log
stdout_logfile=/var/log/supervisor/trustlens.out.log
environment=PATH="/home/master/applications/trustlens/public_html/.venv/bin:%(ENV_PATH)s"
```

Update and start supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status trustlens
```

### Step 6: Configure Cloudways Nginx Reverse Proxy
In Cloudways Application Settings > **Application Settings** > **Vhost Container** (or editing `/etc/nginx/sites-available/<app_id>`):

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 90s;
    proxy_connect_timeout 90s;
    client_max_body_size 12M;
}

location /static/ {
    alias /home/master/applications/trustlens/public_html/app/static/;
    expires 7d;
    add_header Cache-Control "public, max-age=604800";
}
```

Reload Nginx:
```bash
sudo service nginx reload
```

### Step 7: Enable SSL Certificate
1. In Cloudways Dashboard, navigate to **Application Management** > **SSL Certificate**.
2. Select **Let's Encrypt**.
3. Enter your email and custom domain (or default `*.cloudwaysapps.com` subdomain).
4. Click **Install Certificate**.

---

## 3. Deployment Verification Checklist

Once credentials are provided and the steps are executed:
- [ ] Verify `https://<DOMAIN>/api/health` returns HTTP 200 with `status: "ok"`.
- [ ] Verify `https://<DOMAIN>/` loads the responsive glassmorphic interface.
- [ ] Upload `samples/fake_internship_fee.pdf` and verify detection of upfront fees.
- [ ] Upload `samples/phishing_sms.png` and verify image upload handling.
- [ ] Click "Export Markdown Report (.md)" and confirm clean download.

---

## 4. Current Status & Honest Reporting

- **Architecture Feasibility**: VERIFIED.
- **Local Parity**: VERIFIED (FastAPI + PyMuPDF runs seamlessly under Uvicorn and Docker Compose).
- **Live Cloudways Deployment**: **BLOCKED on Credentials**. Cloudways server SSH credentials or API access tokens were not provided in this environment. Following Operating Rule 8 and Rule 15, live deployment is honestly marked BLOCKED until credentials are provided.
