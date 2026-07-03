# Salesman KPI Dashboard

Streamlit + MySQL (Cloud SQL) sales/KPI dashboard with login authentication.
(Rebuilt from the SalesPulse v2 codebase into a fresh project: `salesman_kpi`.)

## Project structure

```
salesman_kpi/
├── app.py                  # entry point, routes to login or dashboard
├── login.py                # login form + DB auth (users table)
├── dashboard.py            # sidebar nav + page routing
├── pages_/
│   ├── sales.py            # main sales KPI page
│   ├── cp_sales.py
│   ├── fy_sales.py
│   ├── sales_metrics.py    # stub -> coming_soon
│   ├── outstanding.py      # stub -> coming_soon
│   ├── l10d_trend.py       # stub -> coming_soon
│   ├── gp_leakage.py       # stub -> coming_soon
│   ├── reports.py          # stub -> coming_soon
│   └── coming_soon.py      # shared "coming soon" placeholder UI
├── .streamlit/
│   ├── config.toml         # theme/server config (safe to commit)
│   └── secrets.toml.example
├── requirements.txt
└── .gitignore
```

## 1. Run locally in VS Code

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the secrets template and fill in the real DB password:
```powershell
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```
Edit `.streamlit/secrets.toml`:
```toml
DB_PASSWORD = "your_real_password"
```

Run:
```powershell
streamlit run app.py
```
Open http://localhost:8501

## 2. Push to a NEW GitHub repo

```powershell
git init
git add .
git commit -m "Initial commit - Salesman KPI dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/salesman-kpi.git
git push -u origin main
```
`.gitignore` already excludes `secrets.toml`, so your DB password won't be pushed.

## 3. Deploy on a NEW Streamlit Cloud account

1. Log into the new Streamlit Cloud account at share.streamlit.io
2. "New app" → connect the new `salesman-kpi` GitHub repo → branch `main` → main file `app.py`
3. In **App settings → Secrets**, add:
   ```toml
   DB_PASSWORD = "your_real_password"
   ```
4. Deploy.

## ⚠️ Security note — please read

The `secrets.toml` from your old project contained a real, working database
password. That file was **not** copied into this package — only a placeholder
template (`secrets.toml.example`) is included, and you fill in the real value
yourself in a local file that `.gitignore` keeps out of GitHub.

Since that password has already existed in a plain, unencrypted `secrets.toml`
file that's been shared/moved around, it's worth **rotating it (changing the
DB user's password in Cloud SQL/your MySQL host)** before this goes into a
new public-facing repo or a new Streamlit account — especially if you're not
100% sure where copies of the old file have been.

## Notes on current DB layer

- Connects to a MySQL host (`db31521.public.databaseasp.net`) via SQLAlchemy + PyMySQL.
- `login.py` checks the `users` table with a plain `SELECT ... WHERE username=:u AND password=:p`
  query — i.e. **passwords are stored/compared in plaintext**, not hashed.
  Recommended next step: migrate to `bcrypt` hashed passwords (happy to do this
  as a follow-up once you confirm you want it — it requires re-hashing existing
  user passwords in the `users` table too).
- `sales.py` reads from a `sales_dashboard` table and filters by `role`,
  `region`, `unit`, `asm_code` from the logged-in user's session — this is
  effectively your row-level access control per salesman/ASM.
