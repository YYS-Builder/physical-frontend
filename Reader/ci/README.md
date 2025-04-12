# CI/CD Setup

This directory contains scripts and configuration for the CI/CD pipeline.

## Structure

- `run_tests.sh`: Script to run tests, linting, and security checks
- `deploy.sh`: Script to deploy the application to different environments
- `README.md`: This documentation

## Local Testing

To run the CI pipeline locally:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Local Deployment

To deploy locally:

```bash
chmod +x deploy.sh
ENVIRONMENT=staging ./deploy.sh
```

## Integration with GitHub

The project manager will integrate these scripts with GitHub Actions. The integration will:

1. Run tests on every push to any branch
2. Run tests and deploy to staging on push to `develop` branch
3. Run tests and deploy to production on push to `main` branch

## Required Environment Variables

- `ENVIRONMENT`: Set to either "production" or "staging"
- Database credentials and other sensitive information should be stored in GitHub Secrets

## Dependencies

The CI/CD pipeline requires:

- Python 3.8+
- pip
- pytest
- pytest-cov
- flake8
- mypy
- bandit
- alembic
- uvicorn

## Notes for Project Manager

1. The `run_tests.sh` script includes:
   - Unit tests with coverage reporting
   - Code linting with flake8
   - Type checking with mypy
   - Security checks with bandit

2. The `deploy.sh` script handles:
   - Environment-specific deployments
   - Database migrations
   - Dependency installation
   - Application startup

3. To integrate with GitHub Actions:
   - Create workflows for test, staging, and production
   - Set up environment secrets
   - Configure branch protection rules
   - Set up status checks for pull requests

4. Consider adding:
   - Docker containerization
   - Kubernetes deployment
   - Performance testing
   - Load testing
   - Automated rollback procedures 