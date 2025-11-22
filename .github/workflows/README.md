# GitHub Actions Workflows

Simplified CI/CD workflows for the Keycloak Auth Service project.

## Workflows

### 1. Backend CI (`ci-backend.yml`)

**Triggers:** Push/PR to main or develop (backend changes only)

**What it does:**
- Runs pytest tests with Keycloak service container
- Performs linting (flake8)
- Runs security scans (Bandit, Safety)
- Generates code coverage reports
- Uploads coverage to Codecov

**Local equivalent:**
```bash
cd auth-service
pytest tests/ -v --cov=app
flake8 app/
bandit -r app/
safety check
```

---

### 2. Frontend CI (`ci-frontend.yml`)

**Triggers:** Push/PR to main or develop (frontend changes only)

**What it does:**
- Builds the React application
- Runs ESLint linting
- Performs npm security audit
- Uploads build artifacts

**Local equivalent:**
```bash
cd frontend
npm ci
npm run lint
npm run build
npm audit
```

---

### 3. Docker Build & Push (`docker-build.yml`)

**Triggers:** Push to main branch or version tags (v*)

**What it does:**
- Builds Docker images for all services:
  - auth-service
  - frontend
  - keycloak-init
- Pushes images to GitHub Container Registry (ghcr.io)
- Tags images with branch name, version, and SHA

**Image naming:**
```
ghcr.io/{username}/{repo}/auth-service:main
ghcr.io/{username}/{repo}/frontend:v1.0.0
ghcr.io/{username}/{repo}/keycloak-init:sha-abc123
```

**Note:** Requires `GITHUB_TOKEN` (automatically provided)

---

### 4. Security Scanning (`security-scan.yml`)

**Triggers:**
- Push/PR to main or develop
- Weekly on Sunday at midnight

**What it does:**
- Trivy vulnerability scanning (filesystem and Docker images)
- CodeQL static analysis (Python and JavaScript)
- Dependency review on pull requests
- Uploads results to GitHub Security tab

**View results:**
- Go to: Security → Code scanning alerts

---

## Setup

### Required Secrets

Optional:
- `CODECOV_TOKEN` - For code coverage uploads (get from codecov.io)

All other secrets are automatically provided by GitHub Actions.

---

## How Workflows Run

**On Pull Requests:**
- ✅ Backend CI (if backend files changed)
- ✅ Frontend CI (if frontend files changed)
- ✅ Security Scanning
- ❌ Docker Build (does not run on PRs)

**On Push to main/develop:**
- ✅ Backend CI (if backend files changed)
- ✅ Frontend CI (if frontend files changed)
- ✅ Security Scanning

**On Push to main only:**
- ✅ Docker Build & Push

**On Version Tags (v*):**
- ✅ Docker Build & Push (with version tags)

---

## Troubleshooting

### "Tests failed in CI but pass locally"

- Ensure Keycloak is running: `docker-compose up keycloak`
- Check environment variables match CI configuration
- Backend CI uses `microservices-realm` realm

### "Docker build failed"

- Test locally: `docker build -t test ./auth-service`
- Check Dockerfile exists and is valid
- Ensure GitHub Container Registry permissions are enabled

### "Security scan found vulnerabilities"

- Review alerts in: Security → Code scanning
- Check `.trivyignore` to suppress false positives
- Update dependencies if needed

---

## Dependabot

Automated dependency updates run weekly on Monday:

- **Python packages** (auth-service)
- **npm packages** (frontend)
- **GitHub Actions** versions

Updates are created as pull requests automatically.

---

## Badge Status

Add to your README:

```markdown
[![Backend CI](https://github.com/USERNAME/REPO/workflows/Backend%20CI/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci-backend.yml)
[![Frontend CI](https://github.com/USERNAME/REPO/workflows/Frontend%20CI/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/ci-frontend.yml)
[![Docker Build](https://github.com/USERNAME/REPO/workflows/Docker%20Build%20%26%20Push/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/docker-build.yml)
[![Security](https://github.com/USERNAME/REPO/workflows/Security%20Scanning/badge.svg)](https://github.com/USERNAME/REPO/actions/workflows/security-scan.yml)
```

Replace `USERNAME` and `REPO` with your actual GitHub username and repository name.
