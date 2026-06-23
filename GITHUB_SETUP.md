# Put This Project on GitHub

Step-by-step guide to publish `quantum-regime-engine` to your GitHub account.

---

## Before you start

1. Install [Git](https://git-scm.com/download/win)
2. Create a free account at [github.com](https://github.com) if you don't have one
3. Make sure the tool works locally:

```bash
cd quantum-regime-engine
install.bat          # Windows
# or: bash install.sh   # Mac/Linux
```

---

## Step 1 — Create a new repository on GitHub

1. Go to https://github.com/new
2. **Repository name:** `quantum-regime-engine` (or any name you like)
3. **Description:** `HMM market regime detection with backtesting and optional QAOA`
4. Choose **Public**
5. Do **NOT** check "Add a README" (you already have one)
6. Click **Create repository**

GitHub will show you a page with setup commands. Keep that tab open.

---

## Step 2 — Initialize Git in your project folder

Open PowerShell or Terminal:

```bash
cd path\to\quantum-regime-engine

git init
git branch -M main
```

---

## Step 3 — Stage and commit your files

```bash
git add .
git status
```

You should see source files, README, etc. You should **not** see `output/*.png`, `__pycache__`, or `.venv` (`.gitignore` blocks those).

```bash
git commit -m "Initial commit: regime detection engine with HMM, backtest, and dashboard"
```

---

## Step 4 — Connect to GitHub and push

For this project (org **OuroTools**):

```bash
git remote add origin https://github.com/OuroTools/Quantum-regime-engine.git
git push -u origin main
```

GitHub may ask you to log in. Options:

- **HTTPS:** Use a [Personal Access Token](https://github.com/settings/tokens) as your password
- **SSH:** Set up [SSH keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) and use `git@github.com:YOUR_USERNAME/quantum-regime-engine.git`

---

## Step 5 — Verify on GitHub

Refresh your repo page. You should see:

- `README.md` rendered on the home page
- `src/regime_engine/` with all Python modules
- `dashboard.py`, `main.py`, `notebooks/`

---

## Optional — Add topics (helps discoverability)

On your repo page: **Settings** → scroll to **Topics** → add:

`python` `finance` `hidden-markov-model` `backtesting` `quantum-computing` `streamlit` `portfolio-optimization`

---

## Optional — Deploy dashboard online (free)

Streamlit Community Cloud can host your dashboard:

1. Push project to GitHub (steps above)
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. **New app** → select your repo
5. **Main file path:** `src/regime_engine/dashboard_app.py`
6. Deploy

Add a `requirements.txt` at repo root (already included) so Streamlit knows what to install.

---

## Updating the repo later

After you change code:

```bash
git add .
git commit -m "Describe what you changed"
git push
```

---

## Clone on another computer

```bash
git clone https://github.com/OuroTools/Quantum-regime-engine.git
cd quantum-regime-engine
pip install -e ".[all]"
regime-engine
regime-dashboard
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `git: command not found` | Install Git and restart terminal |
| `remote origin already exists` | `git remote set-url origin https://github.com/OuroTools/Quantum-regime-engine.git` |
| Push rejected | `git pull origin main --rebase` then `git push` |
| Large files rejected | Don't commit `output/` charts — `.gitignore` handles this |

---

## What gets published vs kept local

| Published (in Git) | Kept local (gitignored) |
|--------------------|-------------------------|
| All source code | `output/*.png`, `output/report.txt` |
| README, docs | `__pycache__/`, `.venv/` |
| `requirements.txt`, `pyproject.toml` | Jupyter checkpoints |
