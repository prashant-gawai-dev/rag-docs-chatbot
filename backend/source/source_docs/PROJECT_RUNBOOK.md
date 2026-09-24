# Project Runbook — api-integration-project

Personal reference for starting each session, plus every command category used on this project, with plain explanations of *why* each one matters.

---

## 1. Daily Startup Checklist

Run through this at the start of every session, in order.

```bash
# 1. Activate your local Python environment
cd ~/Documents/api-integration-project
source venv/bin/activate

# 2. Pull latest changes (in case you edited from another machine)
git pull

# 3. If working with AWS today: start the EC2 instance
#    (AWS Console → EC2 → Instances → select instance → Instance state → Start instance)
#    Wait for "Running", then copy the NEW public IPv4 address — it changes every stop/start
#    unless you've set up an Elastic IP.

# 4. SSH into the instance (replace IP with today's actual IP)
ssh -i ~/.ssh/api-integration-project-key.pem ubuntu@<NEW_PUBLIC_IP>

# 5. Once connected, check if your container survived the stop
docker ps -a
# If it shows "Exited", restart it:
docker start <container_name_or_id>

# 6. Confirm it's live (run this from your LAPTOP, not the SSH session)
curl http://<NEW_PUBLIC_IP>:8000/
```

**Why the IP changes:** AWS assigns a new public IP each time you start a *stopped* instance, unless an Elastic IP is reserved. Everything on disk (code, Docker image, `.env`) survives — only the IP and running processes reset.

---

## 2. Linux / Bash Essentials

| Command | What it does | Why it matters |
|---|---|---|
| `ls -la` | List all files, including hidden ones (`.env`, `.git`) | Regular `ls` hides dotfiles — easy to think a file's missing when it's just hidden |
| `cat <file>` | Print a file's contents | Quick way to verify what's actually in a file, not what you assume is in it |
| `nano <file>` | Open a simple terminal text editor | `Ctrl+O` save, `Enter` confirm, `Ctrl+X` exit |
| `grep -n "text" file` | Search for text inside a file, with line numbers | Faster than manually scrolling; `-n` shows exactly where |
| `chmod 400 <file>` | Restrict a file to read-only, owner-only | Required for SSH private keys — SSH refuses overly-open key files |
| `kill %2` | Kill a suspended background job by job number | Fixes "Address already in use" from a `Ctrl+Z`-suspended server |
| `lsof -i :8000` | Show what process is using port 8000 | Diagnose port conflicts before restarting a server |
| `which python` | Show which Python binary is currently active | Confirms whether your virtualenv is actually activated |
| `echo "text" >> file` | Append a line to a file | `>>` appends; `>` (single) **overwrites** the whole file — easy mistake |
| `rm <file>` | Delete a file | No undo — be certain before running |
| `mv <src> <dest>` | Move/rename a file | Used to move downloaded `.pem` keys into `~/.ssh/` |

**Key distinction:** `Ctrl+C` terminates a running process cleanly (releases ports). `Ctrl+Z` only *suspends* it (pauses in background, port stays held) — use `Ctrl+C` to stop dev servers, not `Ctrl+Z`.

---

## 3. Python / Virtual Environment

```bash
# Create a virtual environment (once per project)
python3 -m venv venv

# Activate it (every session)
source venv/bin/activate
# Prompt shows (venv) prefix when active

# Install a package
pip install <package>

# Save exact installed versions to a file others can reinstall from
pip freeze > requirements.txt

# Install everything from that file (e.g. on a fresh machine/server)
pip install -r requirements.txt --no-cache-dir

# Run the dev server
uvicorn main:app --reload
# --reload = auto-restart on code changes (development only — never use in production)
```

**Why `--no-cache-dir` on servers:** skips pip's local package cache, keeping the environment (or Docker image) smaller — no benefit to caching on a machine you won't reuse for other installs.

---

## 4. Git & GitHub

### One-time setup (per machine)
```bash
git config --global user.name "Your Name"
git config --global user.email "your-personal-email@example.com"

# Generate an SSH key dedicated to GitHub (don't reuse across accounts)
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519_personal

# Register it with SSH via a config file
nano ~/.ssh/config
```
```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
```
```bash
# Add the PUBLIC key (cat the .pub file) to GitHub: Settings → SSH and GPG keys → New SSH key
cat ~/.ssh/id_ed25519_personal.pub

# Test the connection
ssh -T git@github.com
# Success looks like: "Hi <username>! You've successfully authenticated..."
```

### Everyday commands
| Command | What it does |
|---|---|
| `git init` | Turn the current folder into a git repository |
| `git status` | Show what's staged, unstaged, or untracked — **always check before committing** |
| `git add <file>` / `git add .` | Stage specific file(s) / everything eligible |
| `git commit -m "message"` | Save a snapshot of staged changes with a description |
| `git push` | Upload commits to GitHub (`-u origin main` only needed the *first* time, to set tracking) |
| `git pull` | Download and merge latest changes from GitHub |
| `git log --oneline` | Compact history of commits |
| `git remote add origin <url>` | Link a local repo to a GitHub repo (once) |
| `git rm --cached <file>` | Stop tracking a file in git, **without deleting it from disk** |
| `git ls-files` | List every file git is currently tracking — good sanity check |
| `git branch -m main` | Rename current branch (e.g. `master` → `main`) |

### Safety habits (learned the hard way this project)
- **Always create `.gitignore` *before* your first `git add`.** Once a secret is committed, deleting the file later doesn't remove it from history — it's still recoverable.
- `.gitignore` must include: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `.vscode/`
- After `git add .`, always run `git status` again and manually confirm `.env` is **not** in "Changes to be committed" before committing.
- If a real secret is ever pasted anywhere (chat, terminal, committed) — **rotate it immediately**, don't just delete the text. Assume it's compromised.

### Cloning on a server (e.g. EC2)
```bash
git clone https://github.com/username/repo.git
```
Use plain `https://` (not `git@`) for read-only clones on machines you're not pushing *from* — no key setup needed for a public repo.

---

## 5. Docker

### Core commands
| Command | What it does |
|---|---|
| `docker --version` | Confirm Docker is installed |
| `docker build -t <name> .` | Build an image from the `Dockerfile` in the current directory |
| `docker run <image>` | Start a container in the foreground |
| `docker run -d <image>` | Start a container in the **background** (detached) — needed so it survives you closing the terminal |
| `docker run -p 8000:8000 <image>` | Map port 8000 on the host to port 8000 in the container |
| `docker run --env-file .env <image>` | Inject environment variables at runtime (never bake secrets into the image itself) |
| `docker run --name myapp <image>` | Give the container a memorable name instead of a random one |
| `docker ps` | List **running** containers |
| `docker ps -a` | List **all** containers, including stopped ones |
| `docker start <name/id>` | Restart a stopped container |
| `docker stop <name/id>` | Stop a running container |
| `docker logs <name/id>` | View a container's output/logs — first place to check when something's wrong |
| `docker exec -it <name/id> bash` | Open a shell *inside* a running container, for live debugging |

### Dockerfile pattern (what each line does)
```dockerfile
FROM python:3.12-slim          # base image — match your real dev Python version
WORKDIR /app                   # sets working directory inside the container
COPY requirements.txt .        # copy dependency list FIRST — enables Docker layer caching
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                       # copy the rest of the code AFTER deps are installed
EXPOSE 8000                    # documents which port the app uses (doesn't open it by itself)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# --host 0.0.0.0 is REQUIRED — 127.0.0.1 inside a container is invisible from outside it
```

**Why dependencies are copied before code:** Docker caches each instruction as a layer. If `requirements.txt` hasn't changed, Docker skips reinstalling packages entirely on rebuild — only re-running the `COPY . .` step. Combining code + deps in one step forces a full reinstall on every single code change.

**`.dockerignore`** — same idea as `.gitignore`, but for what `COPY . .` excludes:
```
.env
venv/
__pycache__/
*.pyc
.git/
.gitignore
```

---

## 6. AWS EC2

### Launching an instance (console-based, one-time per instance)
1. EC2 → Launch Instance
2. Choose **Ubuntu Server 24.04 LTS**, **t2.micro/t3.micro** (free tier)
3. Create a new key pair — **RSA, `.pem` format** — download it immediately (AWS never stores a copy)
4. Security group: allow **SSH from "My IP"** only (not "Anywhere")
5. Launch, wait for state = **Running**, copy the **Public IPv4 address**

### Key file setup (once, right after download)
```bash
mv ~/Downloads/your-key.pem ~/.ssh/
chmod 400 ~/.ssh/your-key.pem
```

### Connecting
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@<PUBLIC_IP>
```
`ubuntu` is the fixed default username for Ubuntu AMIs — not something you choose.

### Managing the instance
| Action | Where |
|---|---|
| Stop (pauses, no charges, disk preserved) | Console → Instance state → **Stop instance** |
| Start (new public IP unless Elastic IP set) | Console → Instance state → **Start instance** |
| **Terminate** (permanent deletion — never do by accident) | Console → Instance state → Terminate instance |

### Security groups (the AWS firewall)
- Default: only SSH open, only to your IP
- To expose an app port (e.g. 8000, or 80 for nginx): Security group → **Edit inbound rules** → Add rule → Custom TCP → port → Source `0.0.0.0/0` (Anywhere) if it needs to be public
- A `curl` request that **times out** (not "connection refused") almost always means a security group is silently blocking the port — the request never reaches the instance at all.

### Setting up the instance for Docker (first time only)
```bash
sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# then either: newgrp docker   OR   exit and reconnect via SSH
```

---

## 7. PostgreSQL / Neon / SQLAlchemy

### Key concepts
- **`Base.metadata.create_all(bind=engine)`** only creates tables that **don't already exist** — it never alters an existing table. If you add a new column to a model, existing tables won't get it automatically. Fix (dev only, no real data): drop and let it recreate, or use a migration tool (Alembic) for real projects.
- **SQLAlchemy Session basics:**
  - `db.add(obj)` — stage a new object for insert
  - `db.commit()` — actually write staged changes to the database (takes no arguments)
  - `db.refresh(obj)` — reload an object with DB-generated values (like auto-incremented `id`)
  - `db.get(Model, id)` — fetch one row by primary key (returns `None` if missing)
  - `db.query(Model).all()` — fetch every row
  - `db.query(Model).filter(Model.col == value).first()` — fetch one row by any column
  - `db.delete(obj)` — mark a fetched object for deletion
  - `db.rollback()` — discard a failed/half-finished transaction, always call this in an `except` block after a failed `commit()`
- **Updating a row:** fetch it with `db.get()`, then just reassign its attributes directly (`obj.name = new_value`) — no separate "update" method exists; SQLAlchemy tracks the change automatically and writes it on `commit()`.

### Direct connection check
```python
from database import engine
from sqlalchemy import text

with engine.connect() as connection:
    result = connection.execute(text("SELECT version()"))
    print(result)
```

### Environment-based config pattern (never hardcode credentials)
```python
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```
`.env` file (never committed):
```
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

**If a real credential is ever exposed** (pasted in chat, committed to git, etc.): rotate it immediately in the Neon dashboard, update `.env`, restart the app. Treat any exposure as compromised regardless of how it happened.

---

## 8. Testing (pytest)

```bash
pip install pytest
pytest test_main.py -v          # -v = verbose, shows each test by name
```

Key pattern — isolate tests from the real database using an in-memory SQLite database:
```python
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # REQUIRED — without this, each connection gets its own
                            # empty in-memory DB, causing "no such table" errors
)
```
Override the app's real `get_db` dependency with a test version pointed at this engine, using `app.dependency_overrides[get_db] = override_get_db`.

---

## 9. Common Error Patterns (seen this project, worth recognizing fast)

| Symptom | Likely cause |
|---|---|
| `Address already in use` | An old server process is still holding the port — check `lsof -i :PORT`, kill it |
| `no such table` (SQLite) | Missing `poolclass=StaticPool`, or `create_all()` never ran against that engine |
| `column "X" does not exist` | Model has the column, but the actual live table was created before you added it — `create_all()` doesn't alter existing tables |
| `TypeError: 'X' is an invalid keyword argument` | Trying to pass a field into a SQLAlchemy model constructor that isn't a defined `Column` |
| `curl` times out (not refused) | Security group blocking the port — check inbound rules |
| `Permission denied (publickey)` on SSH | Wrong username, wrong key file, or key permissions aren't `400` |
| Empty/`null` response body on a request that should have data | Request body wasn't actually sent — check the client (Postman/browser) actually has content in the body field |

---

## 10. Deployment Flow Summary (Option B — rebuild on server)

```bash
# On the EC2 instance
git clone https://github.com/username/repo.git
cd repo
nano .env                      # add real DATABASE_URL, never commit this
docker build -t api-integration-project .
docker run -d -p 8000:8000 --env-file .env --name api-project api-integration-project
docker ps                      # confirm it's running

# Open port 8000 (or 80, once nginx is in place) in the security group

# From your laptop:
curl http://<PUBLIC_IP>:8000/
```
