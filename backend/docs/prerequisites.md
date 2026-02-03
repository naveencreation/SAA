# Prerequisites (Windows)

This document lists the exact software and versions required to develop and run the Smart-Audit-Agent backend on Windows, plus step-by-step install and verification instructions.

Summary of required versions

- Python: 3.10.11
- Node.js: v22.22.0
- PostgreSQL: 17 (server)
- pgvector: v0.8.0 (extension built/installed for PostgreSQL 17)
- Redis (optional for caching, not covered in this guide) 
- Docker Desktop: latest stable that supports your Windows build

Note: instructions below show both interactive installer flows and PowerShell/automation alternatives when available. Use the method you prefer; interactive installers are safest for first-time setups.

---

Table of contents

1. Overview
2. System requirements
3. Downloads and links
4. Installation steps
   - Python 3.10.11
   - Node.js v22.22.0
   - Docker Desktop
   - PostgreSQL 17
   - pgvector (Windows manual build)
5. Create database & enable pgvector
6. Verification checklist
7. Troubleshooting
8. Recommended next steps

---

1) Overview

This project requires a specific toolchain so team members run a consistent environment. Follow each section in order. If you prefer, you can use WSL2 (Windows Subsystem for Linux) to avoid some Windows-native build quirks (pgvector, for example, often builds easier in WSL2). We include both native Windows and WSL2 hints where relevant.

2) System requirements (minimum)

- OS: Windows 10 64-bit (version 1903+) or Windows 11
- Architecture: x86_64 / amd64
- RAM: 8 GB (16 GB recommended)
- Disk: 10+ GB free
- Admin rights: Required for system-wide installers and installing Visual Studio components

3) Downloads and links

- Python 3.10.11 (Windows x86-64 installer):
  https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

- Node.js v22.22.0 (official binaries):
  https://nodejs.org/dist/v22.22.0/
  (Use the Windows x64 MSI from that folder or use nvm-windows to manage versions)

- PostgreSQL 17 (EnterpriseDB installer suggested):
  Installer (example): https://sbp.enterprisedb.com/getfile.jsp?fileid=1259910
  Official downloads: https://www.postgresql.org/download/windows/

- pgvector (extension):
  Source & release: https://github.com/pgvector/pgvector (we target v0.8.0 for PostgreSQL 17 in this guide)

- redis (optional, not covered in this guide):
  https://redis.io/docs/getting-started/installation/install-redis-on-windows/ or docker run --name audit-redis -p 6379:6379 -d redis:latest

- Docker Desktop (Windows):
  https://www.docker.com/get-started

- Visual Studio Community (for Windows C++ build tools):
  https://visualstudio.microsoft.com/vs/community/
  Ensure "Desktop development with C++" workload is selected.

- nvm-windows (optional, recommended for Node version management):
  https://github.com/coreybutler/nvm-windows/releases

4) Installation steps

Below are tested PowerShell (Administrator) commands and manual steps. Open PowerShell as Administrator for system installs.

A. Python 3.10.11

Manual installer (recommended):
1. Download the installer from:
   https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
2. Run the installer and choose:
   - "Install launcher for all users (recommended)"
   - "Add Python 3.10 to PATH"
   - Install for all users (optional)

PowerShell (download + interactive run):

```powershell
# From an Administrator PowerShell
$pythonUrl = 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe'
$installer = "$env:TEMP\python-3.10.11-amd64.exe"
Invoke-WebRequest -Uri $pythonUrl -OutFile $installer
Start-Process -FilePath $installer -Wait
# Follow installer UI and ensure "Add Python to PATH" is checked
```

Silent install (advanced):

```powershell
# Example silent install (works with official CPython MSI/EXE parameters)
Start-Process -FilePath $installer -ArgumentList '/quiet','InstallAllUsers=1','PrependPath=1' -Wait
```

Verify:

```powershell
python --version
pip --version
```

Expected:

- python --version -> Python 3.10.11

B. Node.js v22.22.0

Two options: official MSI installer or nvm-windows (recommended if you will switch versions).

Option 1 — MSI (manual):
1. Visit https://nodejs.org/dist/v22.22.0/ and download the Windows x64 MSI.
2. Run the MSI and follow the installer.

Option 2 — nvm-windows (recommended for devs):
1. Download nvm-windows from releases: https://github.com/coreybutler/nvm-windows/releases
2. Install nvm-windows using its installer (run as Administrator).
3. After installing nvm, open a new PowerShell (not Administrator) and run:

```powershell
nvm install 22.22.0
nvm use 22.22.0
node --version
npm --version
```

Expected:

- node --version -> v22.22.0

C. Docker Desktop

1. Download Docker Desktop for Windows: https://www.docker.com/get-started
2. Run the installer and follow the prompts. Docker Desktop may require WSL2; if prompted, enable WSL2 and install a Linux kernel update package.
3. After install, sign in if required and ensure Docker is running.

Verify:

```powershell
docker --version
docker compose version
```

D. PostgreSQL 17 (server)

Use the EnterpriseDB installer (recommended) or the official PostgreSQL installer for Windows.

Manual interactive install (EnterpriseDB example):
1. Download the PostgreSQL 17 installer: https://sbp.enterprisedb.com/getfile.jsp?fileid=1259910
2. Run the installer: choose install directory, superuser password (remember this), default port 5432, and include Stack Builder (optional).
3. After install, pgAdmin 4 is typically available as a standalone app.

Verify:

```powershell
psql --version
# or run psql from the PostgreSQL bin directory
"C:\Program Files\PostgreSQL\17\bin\psql.exe" --version
```

E. pgvector (Windows manual build for PostgreSQL 17)

We target pgvector v0.8.0. Windows requires you to build and install the extension. You can either build pgvector on native Windows using Visual Studio's build tools (documented below), or (recommended if you want simpler tooling) build and install it in WSL2 and copy the extension files into PostgreSQL's extension directory.

Native Windows (Manual Build) — high-level steps

1. Install Visual Studio Community (https://visualstudio.microsoft.com/vs/community/) and make sure the "Desktop development with C++" workload is selected.
2. Install Git for Windows: https://git-scm.com/download/win
3. Open "x64 Native Tools Command Prompt for VS" as Administrator (search in Start Menu).
4. Ensure PGROOT is set to your PostgreSQL installation path. Example (adjust if installed elsewhere):

```dos
set "PGROOT=C:\Program Files\PostgreSQL\17"
cd %TEMP%
```

5. Clone the pgvector repository and checkout desired tag:

```dos
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
```

6. Build using nmake and the provided Windows Makefile:

```dos
nmake /F Makefile.win
nmake /F Makefile.win install
```

Notes:
- You must run these commands in the Visual Studio native tools prompt so nmake and the MSVC toolchain are available.
- The build looks for pg_config (from PostgreSQL) which is usually in "%PGROOT%\bin". Make sure %PGROOT% is set to your PostgreSQL path and that pg_config is accessible.

Alternative: Build in WSL2 (recommended if you have WSL2)

1. Install WSL2 and an Ubuntu distribution (https://learn.microsoft.com/windows/wsl/install).
2. Install PostgreSQL 17 and build dependencies inside WSL2, then build pgvector using the normal "make" and "make install" commands (this often avoids Windows-specific build issues).

5) Create database & enable pgvector

After PostgreSQL 17 and pgvector are installed, create a project database and activate the extension.

PowerShell / psql examples (replace password/paths as needed):

Interactive via pgAdmin:
- Open pgAdmin 4
- Register a server: Right-click "Servers" → Register → Server
  - Name: MyLocalDB
  - Connection → Host: localhost, Port: 5432, Maintenance DB: postgres, Username: postgres, Password: (the one you set during install)

From PowerShell using psql (non-WSL):

```powershell
# Create a database
"C:\Program Files\PostgreSQL\17\bin\createdb.exe" -U postgres smart_audit
# Or use psql to run SQL directly
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d smart_audit -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

From psql inside pgAdmin Query Tool (SQL):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Test the pgvector functionality (SQL example run in pgAdmin Query Tool or psql):

```sql
CREATE TABLE items (id serial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 1;
```

Expected: the query should return the row whose embedding is closest to [3,1,2].

6) Verification checklist

Run these steps to confirm everything is installed and the correct versions are active.

PowerShell commands:

```powershell
python --version
node --version
npm --version
psql --version
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d smart_audit -c "SELECT extname FROM pg_extension WHERE extname='vector';"
docker --version
```

Expected results (examples):
- Python 3.10.11
- node v22.22.0
- psql (PostgreSQL) 17.x
- SELECT extname FROM pg_extension WHERE extname='vector'; -> returns 'vector' (if extension installed in that database)
- docker -> Docker version x.y.z

7) Troubleshooting

- PATH issues: If a command like python or psql isn't found, ensure the installer added its bin folder to PATH, or use the explicit absolute path ("C:\Program Files\PostgreSQL\17\bin\psql.exe"). Restart your shell after modifying PATH.
- pg_config not found during build: ensure the PostgreSQL bin directory is on PATH or set PGROOT to the PostgreSQL installation path before building pgvector.
- Visual Studio build errors: ensure you opened the "x64 Native Tools Command Prompt for VS" and installed the "Desktop development with C++" workload.
- Permission errors: run the command prompt / PowerShell as Administrator where the instructions require admin privileges.
- WSL2 alternative: If native Windows build fails, set up WSL2 (Ubuntu), install libpq-dev and build pgvector in WSL; then copy the compiled files into your PostgreSQL extension directory or use the same DB instance in WSL.

8) Recommended next steps

- Set environment variables used by the project (see project README or .env.example).
- Run backend migrations and start the dev server (see repository Backend README).
- Commit a small document or script for your team to automate repetitive steps (for example a PowerShell script or a Chocolatey/winget manifest).

---

If you want, I can also:
- Provide an automated PowerShell script that installs these components (where possible) and validates versions, or
- Add a WSL2-based companion guide that builds pgvector inside Ubuntu and installs it to PostgreSQL.

End of prerequisites guide.
