# Smart Campus Facility and Maintenance Platform

A representative Flask application for a Software Engineering testing and DevOps assignment.

## Features
- Room booking validation and overlap prevention
- Maintenance ticket creation with duplicate-request protection
- Ticket status transition validation
- Sensor threshold checks
- Restricted booking approval checks
- External synchronization retry policy
- Health endpoint for deployment smoke tests

## Run on Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app
```

Open http://127.0.0.1:5000 to use the visual dashboard.

## Run tests

```powershell
python -m pytest -v
```

Optional coverage:

```powershell
python -m coverage run -m pytest
python -m coverage report -m
```

## Run with Docker

```powershell
docker compose up --build -d
docker compose ps
```

Open http://localhost:5000

Stop:

```powershell
docker compose down
```

## Jenkins
Create a Pipeline job connected to this Git repository and use the included Jenkinsfile.
This Jenkinsfile uses Windows `bat` steps. For a Linux Jenkins agent, replace `bat` with `sh`
and adjust the commands.

## Demonstrating blocked delivery
Temporarily change an expected result in a test so that the test fails, commit the change,
and run the pipeline. Confirm that the pipeline stops before Docker build/deployment.
Restore the correct test and rerun the pipeline.

## Important limitations
This is an educational starter, not a production-ready campus platform. The `X-Role` header
is a demonstration mechanism, not real authentication. Replace it with authenticated
sessions or tokens and server-side role lookup before production use. Add CSRF protection,
audit logging, input hardening, database migrations, backups, and concurrency-safe booking
constraints before real deployment.

The default dates in tests are fixed examples and are not live schedules.
