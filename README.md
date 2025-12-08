# 🕐 Open Scheduler

**A modern, beautiful web app for scheduling Python scripts** — inspired by Dagster and Windows Task Scheduler, but simpler and more elegant.

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Dash](https://img.shields.io/badge/dash-2.14+-green)

---

## ✨ Features

- 🎨 **Beautiful Dark UI** — Modern, responsive interface with Bootstrap styling
- 📅 **Flexible Scheduling** — Cron, interval, or one-time execution
- 📁 **File Tree** — Browse and select Python files from tracked directories
- ⬆️ **Upload Support** — Upload standalone .py files (max 5MB)
- 📊 **Live Monitoring** — Real-time status updates and execution logs
- 🔄 **Retry Logic** — Automatic retry on failure with configurable backoff
- 🎯 **No Code Changes** — Schedule any Python file without decorators

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Initialize Database

```powershell
python backend\init_db.py
```

### 3. Run the App

```powershell
.\run.bat
```

Or directly:

```powershell
python -m backend.app
```

### 4. Open in Browser

Navigate to: **http://localhost:8050**

---

## 📁 Project Structure

```
open-scheduler/
├── backend/
│   ├── core/
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── models.py         # DB models (Job, Execution, etc)
│   │   ├── schemas.py        # Pydantic validation
│   │   ├── scheduler.py      # APScheduler wrapper
│   │   ├── executor.py       # Job execution engine
│   │   └── fileops.py        # File operations
│   ├── app.py                # Main Dash app
│   └── init_db.py            # Database initialization
├── frontend/
│   ├── components/
│   │   ├── navbar.py         # Navigation bar
│   │   ├── status_badge.py   # Status indicators
│   │   └── job_card.py       # Job display cards
│   ├── pages/
│   │   ├── overview.py       # Dashboard
│   │   ├── jobs.py           # Job management
│   │   ├── new_job.py        # Create new jobs
│   │   ├── logs.py           # Execution logs
│   │   └── settings.py       # Settings & config
│   └── assets/
│       └── custom.css        # Dark theme styling
├── scheduler.db              # SQLite database (auto-generated)
├── requirements.txt
├── run.bat
└── SPRINTS.md                # Development roadmap

```

---

## 🎯 Usage

### Creating a Job

1. Go to **New Job** page
2. Select a Python file:
   - **Project Files**: Browse tracked directories
   - **Upload**: Upload a new .py file (max 5MB)
3. Configure schedule:
   - **Cron**: e.g., `0 2 * * *` (daily at 2 AM)
   - **Interval**: e.g., every 10 minutes
   - **One-time**: specific date/time
4. Set optional parameters:
   - Timeout (default: 300s)
   - Retry policy (max retries + delay)
   - CLI arguments
   - Environment variables
5. **Test Run** (optional) to verify the script works
6. **Activate** to schedule the job

### Monitoring Jobs

- **Overview**: Dashboard with KPIs and active jobs
- **Jobs**: List all jobs, filter by status, pause/resume/delete
- **Logs**: View execution history with detailed output

### Managing Tracked Directories

- **Settings** → **Tracked Directories**
- Add new directories to scan for Python files
- Default: project root is tracked automatically

---

## ⚙️ Configuration

Create a `.env` file (copy from `.env.example`):

```env
PROJECT_ROOT=.
APP_HOST=0.0.0.0
APP_PORT=8050
DEBUG=True
DB_PATH=scheduler.db
```

---

## 🔒 Security Notice

⚠️ **Important**: This app executes Python code directly on the host machine. Do **not** expose it to untrusted users or the public internet without additional security measures:

- Runs scripts with host permissions (no sandboxing by default)
- No authentication/authorization in MVP
- Suitable for personal/internal use only

**Recommended for production**:
- Run jobs in Docker containers
- Implement user authentication
- Use path whitelisting/blacklisting
- Deploy behind a firewall/VPN

---

## 📊 Status

**Current Progress:** 30% (Sprint 2/9 complete)

- ✅ Database schema and models
- ✅ Frontend base with dark theme
- ✅ Navigation and layout
- 🔄 Overview page (in progress)
- 🔜 Backend API and scheduler
- 🔜 Job creation and execution
- 🔜 Logs and monitoring

See [SPRINTS.md](SPRINTS.md) for detailed roadmap.

---

## 🛠️ Tech Stack

- **Frontend**: Dash 2.14, Plotly, Dash Bootstrap Components
- **Backend**: Python 3.10+, APScheduler, SQLAlchemy
- **Database**: SQLite (default) / PostgreSQL (production)
- **Styling**: Bootstrap 5 + Custom CSS (dark theme)

---

## 📝 License

MIT License (or specify your license)

---

## 🤝 Contributing

This is a work in progress. Contributions welcome!

---

**Built with ❤️ using Dash and Python**
