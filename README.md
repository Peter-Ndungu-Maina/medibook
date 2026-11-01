# MediBook

![CI](https://github.com/Peter-Ndungu-Maina/medibook/actions/workflows/ci.yml/badge.svg)

A small clinic appointment API, built as a hands-on DevOps project. The application is deliberately simple. The focus is on everything around it: containers, a production-style setup, automated testing, and (as the project grows) infrastructure as code, Kubernetes and monitoring.

## What it does

- Manage **doctors**, **patients** and **appointments** through a REST API
- Prevent **double-booking**: a doctor cannot have two active appointments at the same time, enforced both in the API and by a database constraint
- Cancelled appointments free up their time slot
- A `/health/` endpoint that checks the database connection (used for monitoring and, later, Kubernetes probes)

## Architecture

```
Browser -> NGINX (:8080) -> gunicorn + Django -> PostgreSQL
              |
              +-> serves static files directly
```

| Piece | Technology |
|---|---|
| API | Python, Django, Django REST Framework |
| Database | PostgreSQL 16 |
| App server | gunicorn (3 workers) |
| Reverse proxy | NGINX |
| Packaging | Docker (multi-stage build, non-root user), Docker Compose |
| CI | GitHub Actions |

## Run it locally

Requirements: Docker (with WSL 2 on Windows).

**Development mode** (auto-reloading Django server, port 8000):

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py migrate
curl localhost:8000/health/
```

**Production-style mode** (NGINX + gunicorn, port 8080):

```bash
docker compose down
docker compose -f docker-compose.prod.yml up --build -d
curl localhost:8080/health/
```

Run the tests:

```bash
docker compose exec web python manage.py test
```

## API

| Endpoint | Purpose |
|---|---|
| `GET /health/` | App and database status |
| `/api/doctors/` | List, create, update, delete doctors |
| `/api/patients/` | List, create, update, delete patients |
| `/api/appointments/` | List, create, update, delete appointments |

Example:

```bash
curl -X POST localhost:8000/api/doctors/ \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Dr. Amina Otieno","specialty":"General Practice"}'
```

## Continuous integration

Every push to `main` and every pull request triggers a GitHub Actions pipeline that:

1. Starts a fresh PostgreSQL service container
2. Installs dependencies and runs the Django system check
3. Runs the automated test suite
4. Builds the production Docker image (only if the tests pass)

### Proving the pipeline catches failures

A pipeline that has only ever been green might not be testing anything. To check, I deliberately broke a test (changed an expected status code from 201 to 200), confirmed the pipeline failed, then reverted the change and confirmed it passed again.

**Failing run.** `FF..` means the first two of four tests failed. The API returned `201` (Created) while the edited test expected `200`. The app was right and the test was wrong, so CI caught the mismatch and exited with code 1:

```
FF..
======================================================================
FAIL: test_create_appointment (clinic.tests.AppointmentApiTests.test_create_appointment)
----------------------------------------------------------------------
Traceback (most recent call last):
  File ".../app/clinic/tests.py", line 25, in test_create_appointment
    self.assertEqual(response.status_code, status.HTTP_200_OK)
AssertionError: 201 != 200
----------------------------------------------------------------------
Ran 4 tests in 0.060s
FAILED (failures=2)
Error: Process completed with exit code 1.
```

**Passing run after `git revert`:**

```
....
----------------------------------------------------------------------
Ran 4 tests in 0.044s

OK
```

Full logs: [failing run](docs/ci-logs/ci-red.txt) and [passing run](docs/ci-logs/ci-green.txt).

## Incident notes

### 001: Container up but not answering (`Connection reset by peer`)

- **Symptom:** `curl` to the API failed while `docker compose ps` showed both containers as running.
- **Investigation:** `docker compose logs web` showed a `RuntimeError` saying the `clinic` models were not in `INSTALLED_APPS`.
- **Root cause:** two edits were applied in the wrong order. The URL configuration started importing the new app before the settings registered it. The development server auto-reloaded between the two edits, crashed, and never recovered, although the container itself stayed up.
- **Fix:** restarted the web container. The code was correct once both edits were in place.
- **Lessons:** a container being "Up" does not mean the application inside is healthy; read the logs before guessing; apply dependent changes together or in dependency order. Production uses gunicorn, which loads the code once and has no auto-reloader.

## Roadmap

- [x] Django REST API with PostgreSQL
- [x] Docker and Docker Compose
- [x] Production setup: gunicorn, NGINX, multi-stage Dockerfile, non-root user
- [x] CI pipeline with tests and image build
- [x] Ansible playbooks: deploy the app, harden SSH (firewall and Docker install still to do on a cloud VM)
- [ ] Terraform for cloud infrastructure
- [ ] Kubernetes deployment (probes, secrets, CronJob for backups)
- [ ] Monitoring with Prometheus and Grafana, error tracking with Sentry
- [ ] Image vulnerability scanning in CI
- [ ] Database backups and a tested restore
- [ ] More incident write-ups in `docs/rca/`

## Repository layout

```
app/                     Django project and the clinic app
nginx/                   NGINX configuration
ansible/                 Server automation (in progress)
terraform/               Infrastructure as code (planned)
k8s/                     Kubernetes manifests (planned)
docs/                    Documentation, CI logs and incident reports
.github/workflows/       CI pipeline
docker-compose.yml       Development stack
docker-compose.prod.yml  Production-style stack
```
