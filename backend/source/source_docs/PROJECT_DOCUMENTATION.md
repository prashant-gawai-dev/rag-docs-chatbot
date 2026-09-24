# api-integration-project — Full Project Documentation

Everything this project covers: the code itself, the concepts behind it, and the full workflow from writing a line of code to it being live on the internet.

---

# PART 1 — The Code, Explained Line by Line

## 1.1 `database.py`

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()

engine = None
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

| Line | What it does |
|---|---|
| `load_dotenv()` | Reads the `.env` file in the project root and loads its key=value pairs into the environment, so `os.getenv()` can see them |
| `os.getenv("DATABASE_URL")` | Reads the `DATABASE_URL` environment variable — returns `None` if it doesn't exist, rather than crashing |
| `Base = declarative_base()` | Creates the base class every SQLAlchemy model (table) inherits from. This must exist **unconditionally** — even code that never touches the real database (like tests) needs `Base` to define models against |
| `engine = None` / `SessionLocal = None` | Default values — if there's no real `DATABASE_URL` (e.g. running in CI), the app doesn't crash just from being imported |
| `if DATABASE_URL:` | Only build a real database connection if a real connection string actually exists |
| `create_engine(DATABASE_URL)` | Builds the actual connection object to Postgres (or whatever `DATABASE_URL` points to) |
| `sessionmaker(...)` | A factory that creates new database "conversations" (sessions) on demand — each API request gets its own session |

**Why this design matters:** early versions of this file unconditionally built a real engine the moment the file was imported. That meant *anything* importing from this file — including test files that should never touch production data — silently required live database credentials just to load. Making `engine`/`SessionLocal` conditional fixed a real architectural flaw, not just a CI inconvenience.

---

## 1.2 `model.py`

```python
from sqlalchemy import Column, Integer, String
from database import Base

class APIConfig(Base):
    __tablename__ = "api_configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    endpoint = Column(String)
    timeout = Column(Integer, default=30)
    auth_type = Column(String)
    rate_limit = Column(Integer)
```

| Concept | Explanation |
|---|---|
| `class APIConfig(Base)` | This class **is** a database table, via SQLAlchemy's ORM (Object-Relational Mapper). Each attribute becomes a column |
| `__tablename__` | The literal table name in Postgres |
| `Column(Integer, primary_key=True, index=True)` | `id` — auto-incrementing primary key, indexed for fast lookups |
| `Column(String)` | A text column, no fixed length limit at the Python level (Postgres itself defines actual storage) |
| `default=30` | If no value is given on insert, Postgres uses 30 automatically |

**Real bug history on this file:** a column was once misspelled `dafault=30` instead of `default=30` — SQLAlchemy silently ignored the unrecognized argument rather than erroring immediately, which made the bug harder to spot than a hard crash would have been.

---

## 1.3 `main.py` — the FastAPI application

### App setup and dependency injection

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from model import APIConfig as APIConfigModel

app = FastAPI()

if engine is not None:
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

| Line | Explanation |
|---|---|
| `app = FastAPI()` | Creates the actual application object — everything else attaches to this |
| `if engine is not None:` | Only try to create tables if a real database connection exists (same reasoning as Part 1.1) |
| `Base.metadata.create_all(bind=engine)` | Creates any tables defined via `Base` that don't already exist in the database. **Important limitation:** this never *alters* an existing table — if you add a new column to a model, this line won't add it to a table that already exists |
| `def get_db():` | A **dependency** — a reusable function FastAPI calls to provide something an endpoint needs |
| `yield db` | Hands the session to the endpoint temporarily, then resumes this function *after* the endpoint finishes, to run `db.close()` — guarantees the connection is always cleaned up, even if the endpoint raises an error |
| `Depends(get_db)` (used in endpoints) | Tells FastAPI "run `get_db()` and give me its yielded value" — this is how every endpoint gets a fresh, isolated database session per request |

### Pydantic schema (validation)

```python
from pydantic import BaseModel

class APIConfig(BaseModel):
    name: str
    endpoint: str
    auth_type: str
    timeout: int = 30
    rate_limit: int = 100
```

**This is a completely different thing from `model.py`'s `APIConfig`**, despite the same name (aliased on import as `APIConfigModel` to avoid collision). This one validates *incoming request data* — if a client sends `{"timeout": "abc"}`, Pydantic rejects it automatically with a `422 Unprocessable Entity`, before your endpoint code even runs. Fields with `= value` are optional with a default; fields without are required.

### Create (POST)

```python
@app.post("/configs")
def create_config(config: APIConfig, db: Session = Depends(get_db)):
    new_things = APIConfigModel(
        name=config.name,
        endpoint=config.endpoint,
        timeout=config.timeout,
        auth_type=config.auth_type,
        rate_limit=config.rate_limit,
    )
    db.add(new_things)
    db.commit()
    db.refresh(new_things)
    return {"received": new_things}
```

| Step | What happens |
|---|---|
| `config: APIConfig` | FastAPI validates the request body against the Pydantic schema automatically |
| `APIConfigModel(...)` | Builds a real SQLAlchemy object — the Python representation of a not-yet-saved database row |
| `db.add(new_things)` | Stages the object for insertion (nothing written to the database yet) |
| `db.commit()` | Actually executes the `INSERT` SQL and writes it |
| `db.refresh(new_things)` | Reloads the object from the database, pulling in the auto-generated `id` |

### Read one, with 404 handling

```python
@app.get("/getConfig/{config_id}")
def get_one_config(config_id: int, db: Session = Depends(get_db)):
    oneconfig = db.get(APIConfigModel, config_id)
    if oneconfig is None:
        raise HTTPException(status_code=404, detail="config not found")
    return oneconfig
```

`db.get(Model, id)` fetches by primary key, returning `None` if nothing matches — never raises an error on its own. The explicit `if ... is None: raise HTTPException(...)` is what turns "nothing found" into a proper, honest `404` response instead of silently returning `null` with a misleading `200 OK`.

### Update (PUT) — the fetch-then-mutate pattern

```python
@app.put("/configUpdate/{config_id}")
def update_config(Update_config: APIConfig, config_id: int, db: Session = Depends(get_db)):
    getConfig = db.get(APIConfigModel, config_id)
    if getConfig is None:
        raise HTTPException(status_code=404, detail="config not found")
    getConfig.name = Update_config.name
    getConfig.endpoint = Update_config.endpoint
    getConfig.timeout = Update_config.timeout
    getConfig.auth_type = Update_config.auth_type
    getConfig.rate_limit = Update_config.rate_limit
    db.commit()
    db.refresh(getConfig)
    return {"received": getConfig}
```

**Key concept:** there is no `db.update()` method. SQLAlchemy's session automatically tracks any object it fetched (via `db.get()`). Directly reassigning attributes on that already-tracked object (`getConfig.name = ...`) is enough — `db.commit()` detects the change and writes an `UPDATE` statement. No `db.add()` needed here, since the object was already under session tracking the moment it was fetched.

### Delete, with rollback on failure

```python
@app.delete("/configDelete/{config_id}")
def deleteConfig(config_id: int, db: Session = Depends(get_db)):
    deleteConfig = db.get(APIConfigModel, config_id)
    if deleteConfig is None:
        raise HTTPException(status_code=404, detail="not found")
    try:
        db.delete(deleteConfig)
        db.commit()
        return {"detail": f"Config '{deleteConfig.name}' (id={config_id}) deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
```

`db.rollback()` matters because a failed `commit()` can leave the session's transaction in a broken, half-finished state — rollback explicitly discards it, returning the session to a clean, reusable state rather than leaving it corrupted for the next operation.

### Third-party API integration with layered error handling

```python
@app.get("/weather")
def get_weather(lat: float, lon: float):
    try:
        response = httpx.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true",
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="Could not connect to weather service")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Weather service timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Weather service error: {e}")
```

Three distinct failure modes get three distinct, honest responses — a **502** (bad gateway) if the upstream service is unreachable, a **504** (timeout) if it's too slow, another **502** if it responds but with an error status. This is meaningfully better than a single generic `except Exception`, since the client actually learns what kind of failure occurred.

---

## 1.4 `test_main.py` — automated testing

```python
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)
```

| Concept | Explanation |
|---|---|
| `sqlite:///:memory:` | An entire database that exists only in RAM, never touches disk, and disappears when the process ends — perfect for disposable test runs |
| `poolclass=StaticPool` | **Critical, non-obvious requirement.** Without this, every new database connection gets its *own separate* in-memory database, causing "no such table" errors — because the table only existed in whichever connection created it. `StaticPool` forces one single, persistent connection for the whole test run |
| `app.dependency_overrides[get_db] = override_get_db` | FastAPI's built-in mechanism to swap out a dependency during tests — every endpoint that asks for `get_db` now gets the fake SQLite session instead, with zero changes to `main.py` itself |
| `TestClient(app)` | Lets tests call your actual endpoints in-process — no real server, no real network traffic, but exercises the real FastAPI routing/validation logic |

### Example test

```python
def test_create_config():
    response = client.post("/configs", json={
        "name": "test_api",
        "endpoint": "https://example.com",
        "auth_type": "none",
        "timeout": 10,
        "rate_limit": 50
    })
    assert response.status_code == 200
    data = response.json()
    assert data["received"]["name"] == "test_api"
```

`pytest` automatically discovers and runs any function whose name starts with `test_` — no registration or decorators needed. `assert` does nothing if the condition is true; it fails the whole test immediately if false.

---

# PART 2 — Git & GitHub

## 2.1 One-time setup (per machine)

```bash
git config --global user.name "Your Name"
git config --global user.email "your-personal-email@example.com"

ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519_personal
```
Register the key in `~/.ssh/config`:
```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
```
Add the **public** key (`cat ~/.ssh/id_ed25519_personal.pub`) to GitHub → Settings → SSH and GPG keys.

Test:
```bash
ssh -T git@github.com
```

## 2.2 Everyday commands

| Command | Purpose |
|---|---|
| `git status` | **Always run before committing.** Shows staged, unstaged, and untracked files |
| `git add <file>` / `git add .` | Stage specific file(s) / everything |
| `git commit -m "message"` | Save a snapshot of staged changes |
| `git push` | Upload commits to GitHub |
| `git pull` | Download and merge latest remote changes |
| `git log --oneline -5` | Compact view of recent commit history |
| `git remote -v` | Show which URL(s) `origin` points to (and whether it's SSH or HTTPS) |
| `git remote set-url origin <url>` | Change the remote URL |
| `git rm --cached <file>` | Stop tracking a file **without deleting it from disk** |

## 2.3 Safety rules learned the hard way

- **Always create `.gitignore` *before* your first `git add`.** A committed secret isn't removed just by deleting the file later — it's still recoverable from history.
- Required `.gitignore` entries for this project: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `.vscode/`
- After `git add .`, run `git status` again and manually confirm `.env` is **not** listed before committing.
- **If a real secret is ever exposed** (pasted in chat, accidentally committed, shown on screen) — rotate it immediately. Don't debate whether the exposure was "real enough."
- **Laptop's repo → always use the SSH remote** (`git@github.com:...`). **EC2's repo → always use HTTPS** (`https://github.com/...`), since EC2 only ever needs to pull, never push, and shouldn't hold personal SSH credentials.

---

# PART 3 — Linux / Bash Reference

| Command | What it does | Why it matters here |
|---|---|---|
| `ls -la` | List all files, including hidden ones | Regular `ls` hides `.env`, `.git`, etc. |
| `cat <file>` | Print file contents | Fast way to verify actual content, not assumed content |
| `nano <file>` | Simple terminal editor | `Ctrl+O` save, `Ctrl+X` exit |
| `chmod 400 <file>` | Read-only, owner-only permissions | Required for SSH private keys — SSH refuses overly-open key files |
| `grep -n "text" file` | Search inside a file with line numbers | Fast targeted searching |
| `lsof -i :PORT` | Show what's using a port | Diagnose "Address already in use" |
| `kill %2` | Kill a suspended background job | Fixes a server stuck holding a port after `Ctrl+Z` |
| `which python` | Show active Python binary path | Confirms whether a venv is actually activated |
| `echo "text" >> file` | Append a line | `>>` appends; single `>` **overwrites the whole file** |
| `mv <src> <dest>` | Move/rename | Used to move downloaded `.pem` keys into `~/.ssh/` |

**Key habit:** use `Ctrl+C` to stop a dev server (releases the port cleanly). `Ctrl+Z` only *suspends* it in the background — the port stays held, causing "Address already in use" on the next start attempt.

---

# PART 4 — Docker

## 4.1 The Dockerfile, explained

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Line | Explanation |
|---|---|
| `FROM python:3.12-slim` | Base image — matched to the actual development Python version, to avoid dependency/behavior mismatches |
| `WORKDIR /app` | Sets the working directory inside the container's isolated filesystem |
| `COPY requirements.txt .` then `RUN pip install ...` **before** `COPY . .` | Enables Docker's layer caching — if only your code changes (not dependencies), rebuilds skip reinstalling every package, saving significant time |
| `EXPOSE 8000` | Documents which port the app uses (doesn't open it by itself — that's `-p` at `docker run` time) |
| `--host 0.0.0.0` | **Required.** `127.0.0.1` inside a container is invisible from outside it; `0.0.0.0` means "listen on all interfaces," which is what actually allows outside traffic in |

`.dockerignore` mirrors `.gitignore`'s purpose, but for what `COPY . .` excludes — must include `.env`, `venv/`, `.git/`, same reasoning as git: never bake secrets into an image.

## 4.2 Core commands

| Command | Purpose |
|---|---|
| `docker build -t <name> .` | Build an image from the Dockerfile in the current directory |
| `docker run -d -p 8000:8000 --env-file .env --name api-project <image>` | Run in background (`-d`), map the port, inject secrets at runtime (never baked into the image), give it a memorable name |
| `docker ps` | List **running** containers |
| `docker ps -a` | List **all** containers, including stopped ones |
| `docker start <name>` | Restart a stopped container |
| `docker stop <name>` / `docker rm <name>` | Stop / remove a container |
| `docker logs <name>` | View a container's output — first place to check when something's wrong |

---

# PART 5 — AWS EC2

## 5.1 Daily startup routine

```bash
# 1. AWS Console -> EC2 -> Instances -> Start instance (if stopped)
#    Wait for "Running", copy the new Public IPv4 address

# 2. SSH in
ssh -i ~/.ssh/api-integration-project-key.pem ubuntu@<CURRENT_PUBLIC_IP>

# 3. Check if the container survived the stop
docker ps -a
docker start <container_name>   # if it shows "Exited"

# 4. Confirm it's live (from your LAPTOP)
curl http://<CURRENT_PUBLIC_IP>/
```

**Why the IP changes:** without a reserved Elastic IP, AWS assigns a new public IP every time a stopped instance is started again. Everything on disk (code, image, `.env`) survives regardless — only the IP and running processes reset.

## 5.2 One-time instance + Docker setup

- Launch: **Ubuntu Server 24.04 LTS**, **t2.micro/t3.micro** (free tier)
- Key pair: RSA, `.pem` format, downloaded once — AWS never stores a copy
- Security group at launch: SSH from **My IP** only

```bash
chmod 400 ~/.ssh/your-key.pem   # required - SSH refuses overly-open key files

sudo apt update
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# then: exit and reconnect, or run `newgrp docker`
```

## 5.3 Security groups (the AWS firewall)

- A `curl` request that **times out** (not "connection refused") almost always means a security group is silently blocking the port before it ever reaches the instance.
- Opening a port: Security group -> **Edit inbound rules** -> Add rule -> Custom TCP -> port -> source `0.0.0.0/0` if it needs to be public.
- **This project's current open ports:** 22 (SSH), 80 (HTTP, via nginx). Port 8000 was deliberately **closed** after nginx was set up — the app is no longer directly reachable from outside, only through nginx's proxy on the same machine.
- **GitHub Actions needs SSH access too** — its servers use different IPs than your laptop, so the SSH rule's source had to be changed from "My IP" to "Anywhere" (`0.0.0.0/0`) for the CD pipeline to reach the instance. Trade-off accepted since the private key itself remains the real authentication barrier.

## 5.4 Precautions — read before every session

1. **Never paste a real secret (database password, private key body) into chat, a public file, or an unencrypted location.** If it happens anyway, rotate it immediately — don't debate whether it "really" leaked.
2. **Check the region selector (top-right of console) before assuming an instance is missing.** Instances are region-specific; the same account can have different instances in Mumbai, Stockholm, etc. — easy to lose track and think something's gone when you're just in the wrong region.
3. **"Stop" is not "Terminate."** Stop preserves everything and costs nothing while stopped. Terminate is permanent and unrecoverable — always double-check before confirming.
4. **An Elastic IP costs money whenever it's *not* attached to a running instance** — even on accounts with free credits. If you allocate one, either keep it attached to a running instance or release it when done.
5. **Every public IPv4 address (Elastic or regular) on a *running* instance incurs a small hourly charge** under current AWS policy (~$0.005/hour) — not something releasing an Elastic IP alone eliminates.
6. **Check Billing -> Free Tier / Credits periodically** — not out of worry, just to keep a general sense of usage, especially early on while still learning the platform's cost model.
7. **Rotate SSH access carefully if broadening a security group rule** (e.g. opening SSH to "Anywhere" for CI/CD) — understand you're trading some security surface for automation convenience, and that the private key is now the sole real barrier.

---

# PART 6 — CI/CD (GitHub Actions)

## 6.1 What it actually does

Every `git push` to `main` triggers `.github/workflows/ci.yml`, which:
1. **`test` job** — spins up a fresh, temporary machine on GitHub's infrastructure, installs dependencies, runs `pytest test_main.py -v`. Uses the isolated in-memory SQLite database — no real credentials needed at all.
2. **`deploy` job** — only runs if `test` passed (`needs: test`). SSHes into the EC2 instance (using secrets, never exposed in logs) and runs:
   ```bash
   git fetch origin
   git reset --hard origin/main
   docker build -t api-integration-project .
   docker stop api-project || true
   docker rm api-project || true
   docker run -d -p 8000:8000 --env-file .env --name api-project api-integration-project
   ```

**Why `git reset --hard origin/main` instead of `git pull`:** a deployment target should always exactly mirror the remote — `git pull` can fail on diverged local history (which happened once on this project after a stray manual push from EC2). `fetch` + `hard reset` always forces an exact match, no merge conflicts possible.

## 6.2 The three required GitHub Secrets

| Secret | Value | Notes |
|---|---|---|
| `EC2_HOST` | Current public IP, e.g. `15.252.144.225` | Must be updated manually whenever the instance is stopped/restarted (no Elastic IP in use) |
| `EC2_USER` | `ubuntu` | Fixed, never changes |
| `EC2_SSH_KEY` | Full contents of the `.pem` file, `-----BEGIN...-----` through `-----END...-----` | Never paste this anywhere except GitHub's secret value field |

**Common setup mistakes to avoid:**
- Name and value go in **separate fields** — never combine as `NAME:value` in either box
- Secrets must be under **Repository secrets**, not an Environment-scoped section
- GitHub never shows a saved secret's value again — if in doubt, just overwrite it fresh

---

# PART 7 — Making a Change and Deploying It (the actual day-to-day workflow)

This is the real end-to-end loop for any future change to this project.

## Step 1 — Make sure EC2 is ready (if using it today)
```bash
# AWS Console -> start the instance if stopped, copy the new public IP
# If the IP changed, update the EC2_HOST GitHub Secret to match
```

## Step 2 — Write the code change (on your Laptop)
```bash
cd ~/Documents/api-integration-project
source venv/bin/activate
nano main.py   # or whichever file
```

## Step 3 — Write a test for the new behavior

Add a new function to `test_main.py`, following the existing pattern:
```python
def test_my_new_feature():
    response = client.post("/your-endpoint", json={...})
    assert response.status_code == 200
    # assert on the specific fields your change affects
```
Think about the failure paths too, not just the happy path — what should happen on bad input, a missing resource, etc.

## Step 4 — Test locally, both ways, before pushing anything
```bash
# Real app still works
uvicorn main:app --reload
curl http://127.0.0.1:8000/

# Full test suite passes
pytest test_main.py -v
```
Don't skip this — CI will catch failures too, but catching them locally first is faster and doesn't require waiting on GitHub's infrastructure.

## Step 5 — Commit and push (on your Laptop)
```bash
git add <changed files>
git status   # double-check .env isn't in this list
git commit -m "clear description of the change"
git push
```

## Step 6 — Watch it deploy (on GitHub, in browser)

`github.com/prashant-gawai-dev/api-integration-project` -> **Actions** tab. Watch `test` pass, then `deploy` run automatically. If `test` fails, `deploy` never runs — the broken code never reaches the live server.

## Step 7 — Verify the live result (on your Laptop)
```bash
curl http://<current_public_ip>/
# or hit the specific new endpoint you added
```

That's the complete loop — no manual SSH into EC2 required for a routine change, as long as the instance is running and `EC2_HOST` is current.
