# PartyPe

0% commission dining platform: live bill splitting, merchant dashboard, waiter portal.

Backend: FastAPI, layered architecture (API → service → repository → model), versioned at `/api/v1`.
Frontend: Next.js 15 + TypeScript + Tailwind + shadcn/ui, migrating incrementally from a legacy static SPA. See `docs/ARCHITECTURE.md` and `docs/MIGRATION_PLAN.md`.

## Project Structure

```
backend/app/         Layered FastAPI app — see docs/ARCHITECTURE.md
  core/               settings (env-var driven), auth primitives
  db/                 engine/session
  models/             SQLModel table models
  schemas/            Pydantic request/response models
  repositories/       DB access layer
  services/           business logic
  api/v1/             versioned routers
frontend/             Next.js 15 app (target) — see docs/MIGRATION_PLAN.md
  legacy-spa/          pre-migration static SPA + design-reference mockups,
                       still served by the backend at "/" during migration
docs/                 architecture, migration plan, API reference, dev guide
requirements.txt      Python dependencies (single source of truth)
.env.example          backend config template
run.py                Local dev entrypoint: `python run.py`
```

## Local Development Setup

1. **Create a Virtual Environment (Python 3.11+ recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

   ```

3. **Run the Development Server:**
   ```bash
   python run.py
   ```
   The app will be available at `http://localhost:8000`.

## Linting

The backend is linted with [ruff](https://docs.astral.sh/ruff/):
```bash
pip install ruff
ruff check backend/ run.py
```
Rule `E712` is intentionally disabled in `pyproject.toml`: SQLModel/SQLAlchemy
query columns overload `==`, so `Model.field == True` builds a SQL `WHERE`
clause and is correct as written — it is not a Python truthiness check.

## VPS Production Deployment Guide

This app is structured to be deployed natively on an Ubuntu/Debian VPS using `gunicorn`, `uvicorn`, and `nginx`.

### Step 1: Push to GitHub (Local Machine)
Run these commands in this directory to push your code to a new GitHub repository:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Setup VPS
SSH into your VPS and install the required system dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git
```

### Step 3: Clone & Install (On VPS)
```bash
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git partype
cd partype

# Create virtual environment and install
sudo python3 -m venv venv
source venv/bin/activate
sudo venv/bin/pip install -r requirements.txt
```

### Step 4: Run as a Background Service (Systemd)
Create a service file to keep the app running forever:
```bash
sudo nano /etc/systemd/system/partype.service
```
Paste the following (adjust paths if necessary):
```ini
[Unit]
Description=Gunicorn instance to serve PartyPe
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/partype
Environment="PATH=/var/www/partype/venv/bin"
ExecStart=/var/www/partype/venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl start partype
sudo systemctl enable partype
```

### Step 5: Configure Nginx (Reverse Proxy)
```bash
sudo nano /etc/nginx/sites-available/partype
```
Paste this configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com; # Or your VPS IP address

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/partype /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

Your app is now live on your VPS!
